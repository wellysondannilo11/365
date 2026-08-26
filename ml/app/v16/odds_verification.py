from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any
import pandas as pd


class OddsVerification(str, Enum):
    EXISTS = "EXISTS"
    NUMERICALLY_VALID = "NUMERICALLY_VALID"
    SOURCE_VERIFIED = "SOURCE_VERIFIED"
    PIT_VERIFIED = "PIT_VERIFIED"
    AVAILABLE_AT_DECISION = "AVAILABLE_AT_DECISION"
    PROVENANCE_VERIFIED = "PROVENANCE_VERIFIED"
    SCIENTIFICALLY_ELIGIBLE = "SCIENTIFICALLY_ELIGIBLE"


@dataclass(frozen=True)
class OddsGateResult:
    odds_exists: bool
    odds_numerically_valid: bool
    odds_source_verified: bool
    odds_pit_verified: bool
    odds_available_at_decision: bool
    odds_provenance_verified: bool
    odds_scientifically_eligible: bool
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _ts(value: Any) -> pd.Timestamp | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    t = pd.to_datetime(value, utc=True, errors="coerce")
    return None if pd.isna(t) else t


def verify_odds(row: Any, decision_time: Any | None = None) -> OddsGateResult:
    def get(k: str, default=None):
        if hasattr(row, "get"):
            return row.get(k, default)
        return default

    exists = get("price") is not None
    try:
        price = float(get("price")) if exists else None
        numeric = price is not None and pd.notna(price) and price > 1.0
    except (TypeError, ValueError):
        numeric = False

    source = str(get("source", "")).strip().lower()
    source_verified = bool(source and source not in {"unknown", "none", "nan"}) and bool(get("source_record_id") or get("raw_hash"))

    decision = _ts(decision_time if decision_time is not None else get("decision_time"))
    available = _ts(get("available_at") or get("snapshot_timestamp") or get("captured_at"))
    source_ts = _ts(get("source_timestamp") or get("snapshot_timestamp") or get("captured_at"))

    pit_verified = bool(decision is not None and available is not None and source_ts is not None and available <= decision and source_ts <= decision)
    available_at_decision = bool(decision is not None and available is not None and available <= decision)

    evidence = str(get("availability_evidence", "")).upper()
    provenance = bool(source_verified and (get("source_record_id") or get("raw_hash"))) and not any(x in evidence for x in ("NO_EXACT_TIMESTAMP", "EVENT_LEVEL_SOURCE_ONLY", "DATE_ONLY"))

    eligible = all((exists, numeric, source_verified, pit_verified, available_at_decision, provenance))
    if not exists:
        reason = "ODDS_MISSING"
    elif not numeric:
        reason = "ODDS_NOT_NUMERICALLY_VALID"
    elif not source_verified:
        reason = "SOURCE_NOT_VERIFIED"
    elif not pit_verified:
        reason = "PIT_NOT_VERIFIED"
    elif not available_at_decision:
        reason = "NOT_AVAILABLE_AT_DECISION"
    elif not provenance:
        reason = "PROVENANCE_NOT_VERIFIED"
    else:
        reason = "SCIENTIFICALLY_ELIGIBLE"

    return OddsGateResult(exists, numeric, source_verified, pit_verified, available_at_decision, provenance, eligible, reason)
