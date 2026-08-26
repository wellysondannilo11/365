from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import hashlib
import json
import pandas as pd


@dataclass(frozen=True)
class ExactPITResult:
    status: str
    reason: str
    event_id: str
    provider_timestamp: pd.Timestamp | None
    decision_timestamp: pd.Timestamp | None
    kickoff_timestamp: pd.Timestamp | None
    raw_hash: str | None
    provenance: str | None


def _timestamp(value: Any) -> pd.Timestamp | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    parsed = pd.to_datetime(value, utc=True, errors="coerce")
    return None if pd.isna(parsed) else parsed


def _stable_hash(row: dict[str, Any]) -> str:
    payload = json.dumps(row, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def classify_exact_pit(row: dict[str, Any]) -> ExactPITResult:
    event_id = str(row.get("event_id") or "")
    provider_ts = _timestamp(row.get("provider_timestamp"))
    decision_ts = _timestamp(row.get("decision_timestamp"))
    kickoff_ts = _timestamp(row.get("kickoff_timestamp"))
    raw_hash = str(row.get("raw_hash") or "").strip() or None
    provenance = str(row.get("provenance") or row.get("source") or "").strip() or None

    if not event_id:
        return ExactPITResult("PIT_INVALID", "EVENT_ID_MISSING", event_id, provider_ts, decision_ts, kickoff_ts, raw_hash, provenance)
    if decision_ts is None:
        return ExactPITResult("NON_PIT", "DECISION_TIMESTAMP_MISSING", event_id, provider_ts, decision_ts, kickoff_ts, raw_hash, provenance)
    if provider_ts is None:
        return ExactPITResult("NON_PIT", "PROVIDER_TIMESTAMP_MISSING", event_id, provider_ts, decision_ts, kickoff_ts, raw_hash, provenance)
    if kickoff_ts is None:
        return ExactPITResult("NON_PIT", "KICKOFF_TIMESTAMP_MISSING", event_id, provider_ts, decision_ts, kickoff_ts, raw_hash, provenance)
    if provider_ts >= kickoff_ts:
        return ExactPITResult("PIT_INVALID", "PROVIDER_TIMESTAMP_AFTER_KICKOFF", event_id, provider_ts, decision_ts, kickoff_ts, raw_hash, provenance)
    if provider_ts > decision_ts:
        return ExactPITResult("PIT_INVALID", "PROVIDER_TIMESTAMP_AFTER_DECISION", event_id, provider_ts, decision_ts, kickoff_ts, raw_hash, provenance)
    try:
        odds = float(row.get("odds"))
    except (TypeError, ValueError):
        odds = float("nan")
    if not pd.notna(odds) or odds <= 1.0:
        return ExactPITResult("PIT_INVALID", "ODDS_INVALID", event_id, provider_ts, decision_ts, kickoff_ts, raw_hash, provenance)
    if not provenance:
        return ExactPITResult("NON_PIT", "PROVENANCE_MISSING", event_id, provider_ts, decision_ts, kickoff_ts, raw_hash, provenance)
    if not raw_hash:
        return ExactPITResult("NON_PIT", "RAW_HASH_MISSING", event_id, provider_ts, decision_ts, kickoff_ts, raw_hash, provenance)
    return ExactPITResult("EXACT_PIT", "EXACT_PIT_CONTRACT_SATISFIED", event_id, provider_ts, decision_ts, kickoff_ts, raw_hash, provenance)


def normalize_rows(rows: list[dict[str, Any]]) -> pd.DataFrame:
    normalized = []
    for row in rows:
        result = classify_exact_pit(row)
        record = dict(row)
        record["pit_status"] = result.status
        record["pit_reason"] = result.reason
        record["provider_timestamp"] = result.provider_timestamp
        record["decision_timestamp"] = result.decision_timestamp
        record["kickoff_timestamp"] = result.kickoff_timestamp
        if not record.get("raw_hash"):
            record["raw_hash"] = _stable_hash(record)
        normalized.append(record)
    return pd.DataFrame(normalized)
