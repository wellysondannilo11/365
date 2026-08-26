"""Engine determinístico de conflito entre fontes; nunca escolhe silenciosamente."""
from dataclasses import dataclass
from typing import Any, Iterable
import pandas as pd

@dataclass(frozen=True)
class Evidence:
    source: str
    value: Any
    timestamp: str | None = None
    confidence: float | None = None


def classify_conflict(evidence: Iterable[Evidence]) -> dict:
    rows=list(evidence)
    values={repr(x.value) for x in rows}
    if not rows:
        status='UNVERIFIED'
    elif len(values)==1:
        status='CONSENSUS'
    elif len(values)==2:
        status='MINOR_CONFLICT'
    else:
        status='MAJOR_CONFLICT'
    return {
        'status':status,
        'feature_blocked':status in {'MINOR_CONFLICT','MAJOR_CONFLICT','UNVERIFIED'},
        'sources':[x.__dict__ for x in rows]
    }


def temporal_conflict(evidence: Iterable[Evidence], decision_timestamp: str | None) -> dict:
    """Classifica conflito e bloqueia qualquer evidência posterior ao instante de decisão."""
    rows=list(evidence)
    decision=pd.Timestamp(decision_timestamp) if decision_timestamp else None
    future=[]
    for e in rows:
        if e.timestamp and decision is not None:
            try:
                ts=pd.Timestamp(e.timestamp)
                if ts > decision: future.append(e.source)
            except Exception:
                future.append(e.source)
    base=classify_conflict(rows)
    if future:
        base['status']='LEAKAGE'
        base['feature_blocked']=True
        base['future_sources']=future
    else:
        base['future_sources']=[]
    return base
