from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json, re
from typing import Any
import pandas as pd

REQUIRED_FIELDS=('event_id','kickoff_timestamp','provider_timestamp','decision_timestamp','bookmaker','market','selection','odds','source','provenance','raw_hash')
HEX64=re.compile(r'^[0-9a-fA-F]{64}$')
NON_EXACT_EVIDENCE={'DATE_LEVEL','DATE_ONLY','OPENING_ONLY','CLOSING_ONLY','RECEIVED_AT','FILE_TIME','DOWNLOAD_TIME','SYNTHETIC'}

@dataclass(frozen=True)
class PITClassification:
    status:str; reason:str; observation_id:str
    provider_timestamp:str|None; decision_timestamp:str|None; kickoff_timestamp:str|None
    evidence_class:str=''
    def to_dict(self): return asdict(self)

def _ts(v):
    if v is None or (isinstance(v,float) and pd.isna(v)): return None
    t=pd.to_datetime(v,utc=True,errors='coerce')
    return None if pd.isna(t) else t

def _text(v): return '' if v is None else str(v).strip()

def canonical_observation_id(row:dict[str,Any])->str:
    payload={k:_text(row.get(k)) for k in ('event_id','provider_timestamp','decision_timestamp','bookmaker','market','selection','source','provenance')}
    try: payload['odds']=round(float(row.get('odds')),12)
    except Exception: payload['odds']=_text(row.get('odds'))
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()

def classify_observation(row:dict[str,Any])->PITClassification:
    oid=canonical_observation_id(row)
    evidence=_text(row.get('temporal_evidence') or 'PROVIDER_NATIVE').upper()
    if evidence in NON_EXACT_EVIDENCE:
        return PITClassification('NON_PIT',f'TEMPORAL_EVIDENCE_NOT_EXACT:{evidence}',oid,None,None,None,evidence)
    provider=_ts(row.get('provider_timestamp')); decision=_ts(row.get('decision_timestamp')); kickoff=_ts(row.get('kickoff_timestamp'))
    if provider is None:
        return PITClassification('NON_PIT','provider_timestamp_missing_or_invalid',oid,None,decision.isoformat() if decision is not None else None,kickoff.isoformat() if kickoff is not None else None,evidence)
    missing=[k for k in REQUIRED_FIELDS if _text(row.get(k))=='']
    if missing:
        return PITClassification('PIT_INVALID',f'MISSING_REQUIRED_FIELDS:{",".join(missing)}',oid,provider.isoformat(),decision.isoformat() if decision is not None else None,kickoff.isoformat() if kickoff is not None else None,evidence)
    if not HEX64.fullmatch(_text(row.get('raw_hash'))):
        return PITClassification('PIT_INVALID','raw_hash_invalid',oid,provider.isoformat(),decision.isoformat() if decision is not None else None,kickoff.isoformat() if kickoff is not None else None,evidence)
    if decision is None: return PITClassification('PIT_INVALID','decision_timestamp_missing_or_invalid',oid,provider.isoformat(),None,kickoff.isoformat() if kickoff is not None else None,evidence)
    if kickoff is None: return PITClassification('PIT_INVALID','kickoff_timestamp_missing_or_invalid',oid,provider.isoformat(),decision.isoformat(),None,evidence)
    try: odds=float(row.get('odds'))
    except Exception: odds=float('nan')
    if not (odds>1): return PITClassification('PIT_INVALID','odds_invalid',oid,provider.isoformat(),decision.isoformat(),kickoff.isoformat(),evidence)
    if provider>decision: return PITClassification('PIT_INVALID','provider_after_decision',oid,provider.isoformat(),decision.isoformat(),kickoff.isoformat(),evidence)
    if decision>=kickoff or provider>=kickoff: return PITClassification('PIT_INVALID','observation_not_prematch',oid,provider.isoformat(),decision.isoformat(),kickoff.isoformat(),evidence)
    return PITClassification('EXACT_PIT','provider_timestamp<=decision_timestamp<kickoff_timestamp',oid,provider.isoformat(),decision.isoformat(),kickoff.isoformat(),evidence)
