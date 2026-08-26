from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

@dataclass(frozen=True)
class QualityResult:
    status: str
    reasons: tuple[str,...]
    source_timestamp: str|None = None
    captured_at: str|None = None
    age_seconds: float|None = None
    def to_dict(self): return asdict(self)

def _dt(v):
    if not v: return None
    try:
        d=datetime.fromisoformat(str(v).replace("Z","+00:00"))
        return d if d.tzinfo else None
    except Exception:
        return None

def gate(row: dict[str,Any], decision_time: datetime, *, max_age_seconds=30, live=False, require_source_timestamp=True):
    reasons=[]
    if decision_time.tzinfo is None: reasons.append("DECISION_TIME_NOT_TZ_AWARE")
    src=_dt(row.get("source_timestamp") or row.get("provider_timestamp"))
    cap=_dt(row.get("captured_at"))
    if require_source_timestamp and src is None: reasons.append("SOURCE_TIMESTAMP_REQUIRED")
    if cap is None: reasons.append("CAPTURED_AT_REQUIRED")
    if src and decision_time.tzinfo and src > decision_time: reasons.append("SOURCE_TIMESTAMP_IN_FUTURE")
    if cap and decision_time.tzinfo and cap > decision_time: reasons.append("CAPTURED_AT_IN_FUTURE")
    age=None
    if src and decision_time.tzinfo:
        age=max(0.0,(decision_time-src).total_seconds())
        if live and age>max_age_seconds: reasons.append("STALE_SOURCE")
    try:
        odds=float(row.get("odds"))
        if odds<=1: reasons.append("INVALID_ODDS")
    except Exception: reasons.append("INVALID_ODDS")
    for key in ("event_id","market","selection"):
        if row.get(key) in (None,""): reasons.append(f"MISSING_{key.upper()}")
    if row.get("pit_ok") is False: reasons.append("PIT_FAILURE")
    if row.get("data_quality") is not None and float(row["data_quality"])<80: reasons.append("LOW_DATA_QUALITY")
    return QualityResult("BLOCK" if reasons else "PASS",tuple(reasons),
                         src.isoformat() if src else None, cap.isoformat() if cap else None, age)

def session_gate(feed_status:str):
    return feed_status == "FEED_ONLINE"
