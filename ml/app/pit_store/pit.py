from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import pandas as pd
from ..leakage import validate_temporal_dataset

REQUIRED = ['event_time','source_time','available_at','ingested_at','decision_time']

@dataclass(frozen=True)
class PITRecord:
    event_id: str; event_time: datetime; source_time: datetime|None; available_at: datetime; ingested_at: datetime; decision_time: datetime
    source: str|None=None; source_record_ids: tuple[str,...]=()
    def validate(self):
        if ensure_utc(self.available_at)>ensure_utc(self.decision_time): raise ValueError('AVAILABLE_AT_AFTER_DECISION')
        if self.source_time is not None and ensure_utc(self.source_time)>ensure_utc(self.decision_time): raise ValueError('SOURCE_TIME_AFTER_DECISION')
        if self.source_time is not None and ensure_utc(self.ingested_at)<ensure_utc(self.source_time): raise ValueError('INGESTED_BEFORE_SOURCE')
        return True

def ensure_utc(v):
    if v is None:return None
    x=pd.Timestamp(v).to_pydatetime() if not isinstance(v,datetime) else v
    if x.tzinfo is None:return x.replace(tzinfo=timezone.utc)
    return x.astimezone(timezone.utc)

def validate_frame(df: pd.DataFrame, require_event_id=True, reject_future_source=True, target_columns=None):
    d=df.copy(); missing=[c for c in REQUIRED if c not in d.columns]
    if require_event_id and 'event_id' not in d.columns: missing.append('event_id')
    if missing: raise ValueError('MISSING_PIT_COLUMNS:'+','.join(missing))
    for c in REQUIRED:
        d[c]=pd.to_datetime(d[c],utc=True,errors='coerce')
        if d[c].isna().any(): raise ValueError(f'INVALID_TIMESTAMP:{c}')
    validate_temporal_dataset(d,target_columns=target_columns)
    return d

def dataset_hash(df):
    cols=sorted(df.columns); x=df[cols].copy()
    for c in x.columns:
        if pd.api.types.is_datetime64_any_dtype(x[c]): x[c]=pd.to_datetime(x[c],utc=True).astype(str)
    payload=x.sort_values(cols,kind='stable').to_json(orient='records',date_format='iso')
    return hashlib.sha256(payload.encode()).hexdigest()
