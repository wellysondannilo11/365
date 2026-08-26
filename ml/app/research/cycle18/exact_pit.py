from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import pandas as pd


@dataclass(frozen=True)
class PITClassification:
    status: str
    reason: str


def parse_timestamp(value: Any) -> pd.Timestamp | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    parsed = pd.to_datetime(value, utc=True, errors="coerce")
    return None if pd.isna(parsed) else parsed


def classify_exact_pit_row(row: dict[str, Any]) -> PITClassification:
    """Strict PIT contract. No fallback to received/download/file timestamps."""
    provider = parse_timestamp(row.get("provider_timestamp"))
    decision = parse_timestamp(row.get("decision_timestamp"))
    kickoff = parse_timestamp(row.get("kickoff_timestamp"))
    source = str(row.get("source") or "").strip()
    provenance = str(row.get("provenance") or "").strip()
    raw_hash = str(row.get("raw_hash") or "").strip()

    if not provider:
        return PITClassification("NON_PIT", "PROVIDER_TIMESTAMP_MISSING")
    if not decision:
        return PITClassification("NON_PIT", "DECISION_TIMESTAMP_MISSING")
    if not kickoff:
        return PITClassification("NON_PIT", "KICKOFF_TIMESTAMP_MISSING")
    if provider > decision:
        return PITClassification("PIT_INVALID", "PROVIDER_AFTER_DECISION")
    if decision >= kickoff:
        return PITClassification("PIT_INVALID", "DECISION_AT_OR_AFTER_KICKOFF")
    if provider >= kickoff:
        return PITClassification("PIT_INVALID", "PROVIDER_AT_OR_AFTER_KICKOFF")
    if not source:
        return PITClassification("NON_PIT", "SOURCE_MISSING")
    if not provenance:
        return PITClassification("NON_PIT", "PROVENANCE_MISSING")
    if not raw_hash:
        return PITClassification("NON_PIT", "RAW_HASH_MISSING")
    try:
        odds = float(row.get("odds"))
    except (TypeError, ValueError):
        odds = float("nan")
    if not pd.notna(odds) or odds <= 1.0:
        return PITClassification("PIT_INVALID", "ODDS_INVALID")
    return PITClassification("EXACT_PIT", "EXACT_PIT_CONTRACT_SATISFIED")


def normalize_external_timestamped_row(
    row: dict[str, Any],
    *,
    provider_timestamp_field: str,
    kickoff_timestamp_field: str,
    decision_timestamp_field: str,
) -> dict[str, Any]:
    """Map only explicit provider/event/decision fields; forbidden fallbacks stay absent."""
    normalized = dict(row)
    normalized["provider_timestamp"] = row.get(provider_timestamp_field)
    normalized["kickoff_timestamp"] = row.get(kickoff_timestamp_field)
    normalized["decision_timestamp"] = row.get(decision_timestamp_field)
    return normalized
