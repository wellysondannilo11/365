from __future__ import annotations
import hashlib, json
from pathlib import Path
import pandas as pd


def fingerprint_dataframe(df: pd.DataFrame) -> str:
    x=df.copy(); x=x[sorted(x.columns)]
    for c in x.columns:
        if pd.api.types.is_datetime64_any_dtype(x[c]): x[c]=pd.to_datetime(x[c],utc=True).astype(str)
    payload=x.sort_values(sorted(x.columns),kind='stable').to_json(orient='records',date_format='iso',default_handler=str)
    return hashlib.sha256(payload.encode()).hexdigest()


def manifest(df: pd.DataFrame, source: str, schema_version='v18.0') -> dict:
    events=int(df.event_id.astype(str).nunique()) if 'event_id' in df else 0
    markets=int(df.market.astype(str).nunique()) if 'market' in df else 0
    bookmakers=int(df.bookmaker.astype(str).nunique()) if 'bookmaker' in df else 0
    t=pd.to_datetime(df.event_time,utc=True,errors='coerce') if 'event_time' in df else pd.Series(dtype='datetime64[ns, UTC]')
    return {
        'dataset_hash':fingerprint_dataframe(df), 'schema_version':schema_version, 'source':source,
        'acquisition_timestamp':pd.Timestamp.now(tz='UTC').isoformat(), 'records':len(df),
        'events':events, 'markets':markets, 'bookmakers':bookmakers,
        'date_start':t.min().isoformat() if len(t) and t.notna().any() else None,
        'date_end':t.max().isoformat() if len(t) and t.notna().any() else None,
    }


def save_manifest(payload, path):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(payload,indent=2,sort_keys=True,default=str),encoding='utf-8')
