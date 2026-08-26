from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import pandas as pd

@dataclass(frozen=True)
class PITDecision:
    event_id: str
    decision_time: pd.Timestamp
    entry_price: float | None
    entry_timestamp: pd.Timestamp | None
    source: str | None
    bookmaker: str | None
    market: str | None
    selection: str | None
    pit_status: str
    scientific_status: str
    reason: str

def _ts(v):
    if v is None or (isinstance(v,float) and pd.isna(v)): return None
    t=pd.to_datetime(v,utc=True,errors='coerce')
    return None if pd.isna(t) else t

def classify_pit(row: dict[str,Any]) -> PITDecision:
    dt=_ts(row.get('decision_time'))
    at=_ts(row.get('entry_timestamp') or row.get('available_at') or row.get('source_timestamp'))
    price=row.get('entry_price',row.get('price'))
    try: price=float(price) if price is not None else None
    except (TypeError,ValueError): price=None
    source=str(row.get('source') or '').strip()
    source_id=row.get('source_record_id') or row.get('raw_hash')
    if dt is None: reason='DECISION_TIME_MISSING'; pit='PIT_INVALID'
    elif at is None: reason='ENTRY_TIMESTAMP_MISSING'; pit='PIT_INVALID'
    elif price is None or price <= 1: reason='ENTRY_PRICE_INVALID'; pit='PIT_INVALID'
    elif at > dt: reason='PRICE_AFTER_DECISION'; pit='PIT_INVALID'
    elif not source: reason='SOURCE_MISSING'; pit='PIT_INVALID'
    elif not source_id: reason='PROVENANCE_ID_MISSING'; pit='PIT_INVALID'
    elif str(row.get('availability_evidence','')).upper() in {'NO_EXACT_TIMESTAMP','DATE_ONLY','EVENT_LEVEL_SOURCE_ONLY'}: reason='EVIDENCE_NOT_EXACT_PIT'; pit='NON_PIT'
    else: reason='SCIENTIFICALLY_ELIGIBLE'; pit='EXACT_PIT'
    scientific='SCIENTIFICALLY_ELIGIBLE' if pit=='EXACT_PIT' else 'RESEARCH_ONLY'
    return PITDecision(str(row.get('event_id','')),dt,price,at,source,row.get('bookmaker'),row.get('market'),row.get('selection'),pit,scientific,reason)

def validate_decision_snapshot(row: dict[str,Any]) -> list[str]:
    required=['event_id','decision_time','market','selection','entry_price','entry_timestamp','model_version','feature_version','probability','fair_odds','EV','selection_rule','stake','provenance_hash','pit_status']
    return [c for c in required if c not in row]
