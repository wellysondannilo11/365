from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
import hashlib
import pandas as pd

@dataclass(frozen=True)
class PITResult:
    status: str
    reason: str
    observation_id: str
    provider_timestamp: str | None
    decision_timestamp: str | None
    kickoff_timestamp: str | None
    evidence_class: str


def _ts(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    t = pd.to_datetime(v, utc=True, errors='coerce')
    return None if pd.isna(t) else t


def _obs_id(row: dict[str, Any]) -> str:
    parts = [str(row.get(k, '') or '') for k in ('event_id','provider_timestamp','bookmaker','market','selection','odds')]
    return hashlib.sha256('|'.join(parts).encode()).hexdigest()


def classify_observation(row: dict[str, Any]) -> PITResult:
    oid = _obs_id(row)
    evidence = str(row.get('temporal_evidence') or 'PROVIDER_NATIVE').upper()
    if evidence in {'DATE_LEVEL','DATE_ONLY','OPENING_ONLY','CLOSING_ONLY','RECEIVED_AT','FILE_TIME'}:
        return PITResult('NON_PIT','TEMPORAL_EVIDENCE_NOT_EXACT',oid,None,None,None,evidence)
    pt, dt, kt = _ts(row.get('provider_timestamp')), _ts(row.get('decision_timestamp')), _ts(row.get('kickoff_timestamp'))
    required = ('event_id','bookmaker','market','selection','source','provenance','raw_hash')
    if any(not str(row.get(k) or '').strip() for k in required):
        return PITResult('PIT_INVALID','REQUIRED_PROVENANCE_FIELD_MISSING',oid,*[x.isoformat() if x is not None else None for x in (pt,dt,kt)],evidence)
    try: odds=float(row.get('odds'))
    except (TypeError,ValueError): odds=float('nan')
    if not (odds > 1.0):
        return PITResult('PIT_INVALID','ODDS_INVALID',oid,*[x.isoformat() if x is not None else None for x in (pt,dt,kt)],evidence)
    if pt is None or dt is None or kt is None:
        return PITResult('PIT_INVALID','TEMPORAL_FIELD_MISSING',oid,*[x.isoformat() if x is not None else None for x in (pt,dt,kt)],evidence)
    if pt > dt:
        return PITResult('PIT_INVALID','PROVIDER_AFTER_DECISION',oid,*[x.isoformat() for x in (pt,dt,kt)],evidence)
    if dt >= kt or pt >= kt:
        return PITResult('PIT_INVALID','OBSERVATION_NOT_PREMATCH',oid,*[x.isoformat() for x in (pt,dt,kt)],evidence)
    return PITResult('EXACT_PIT','PROVIDER_TIMESTAMP_PREDECISION_PREKICKOFF',oid,*[x.isoformat() for x in (pt,dt,kt)],evidence)


def canonicalize_row(row: dict[str, Any]) -> dict[str, Any]:
    r=dict(row)
    result=classify_observation(r)
    r.update({'observation_id':result.observation_id,'pit_status':result.status,'pit_reason':result.reason,'evidence_class':result.evidence_class})
    return r
