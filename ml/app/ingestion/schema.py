from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import pandas as pd

SUPPORTED = {'.csv', '.json', '.parquet'}

@dataclass(frozen=True)
class IngestionSpec:
    dataset_type: str
    required: tuple[str, ...]
    version: str = 'v16.0'

SPECS = {
    'matches': IngestionSpec('matches', ('event_id', 'event_time')),
    'odds': IngestionSpec('odds', ('event_id', 'bookmaker', 'market', 'selection', 'price', 'captured_at')),
    'stats': IngestionSpec('stats', ('event_id', 'event_time')),
    'events': IngestionSpec('events', ('event_id', 'event_time')),
}

TIMESTAMP_COLUMNS = ('event_time','source_time','available_at','ingested_at','decision_time','captured_at','source_timestamp')

def read_source(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    if p.suffix.lower() not in SUPPORTED:
        raise ValueError(f'UNSUPPORTED_FORMAT:{p.suffix}')
    if p.suffix.lower() == '.csv':
        return pd.read_csv(p)
    if p.suffix.lower() == '.json':
        raw = json.loads(p.read_text(encoding='utf-8'))
        return pd.json_normalize(raw if isinstance(raw, list) else raw.get('data', raw))
    return pd.read_parquet(p)

def canonicalize(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in TIMESTAMP_COLUMNS:
        if c in out.columns:
            out[c] = pd.to_datetime(out[c], utc=True, errors='coerce')
    for c in ('event_id','source_id','source_record_id','bookmaker','market','selection'):
        if c in out.columns:
            out[c] = out[c].astype('string')
    if 'price' in out.columns:
        out['price'] = pd.to_numeric(out['price'], errors='coerce')
    if 'line' in out.columns:
        out['line'] = pd.to_numeric(out['line'], errors='coerce')
    return out

def validate_schema(df: pd.DataFrame, dataset_type: str) -> None:
    if dataset_type not in SPECS:
        raise ValueError(f'UNKNOWN_DATASET_TYPE:{dataset_type}')
    missing = [c for c in SPECS[dataset_type].required if c not in df.columns]
    if missing:
        raise ValueError(f'MISSING_SCHEMA_COLUMNS:{missing}')
    d = canonicalize(df)
    if d['event_id'].isna().any() or (d['event_id'].astype(str).str.len() == 0).any():
        raise ValueError('INVALID_EVENT_ID')
    if pd.to_datetime(d['event_time'], utc=True, errors='coerce').isna().any():
        raise ValueError('INVALID_TIMESTAMP:event_time')
    if dataset_type == 'odds':
        prices = pd.to_numeric(d['price'], errors='coerce')
        if prices.isna().any() or (prices <= 1).any():
            raise ValueError('INVALID_ODDS')
        for c in ('captured_at',):
            if pd.to_datetime(d[c], utc=True, errors='coerce').isna().any():
                raise ValueError(f'INVALID_TIMESTAMP:{c}')
        if 'available_at' in d and d['available_at'].isna().any():
            raise ValueError('INVALID_TIMESTAMP:available_at')
        if 'source_timestamp' in d and d['source_timestamp'].isna().any():
            raise ValueError('INVALID_TIMESTAMP:source_timestamp')
    for c in TIMESTAMP_COLUMNS:
        if c in d.columns and d[c].isna().any():
            raise ValueError(f'INVALID_TIMESTAMP:{c}')
    if {'available_at','decision_time'}.issubset(d.columns):
        if (d['available_at'] > d['decision_time']).any():
            raise ValueError('POINT_IN_TIME_VIOLATION')
    if {'source_time','decision_time'}.issubset(d.columns):
        if (d['source_time'] > d['decision_time']).any():
            raise ValueError('SOURCE_TIME_AFTER_DECISION')
    if {'ingested_at','source_time'}.issubset(d.columns):
        if (d['ingested_at'] < d['source_time']).any():
            raise ValueError('INGESTED_BEFORE_SOURCE')
