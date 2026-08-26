from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
import hashlib, json
import pandas as pd
from .odds_verification import verify_odds


DECISION_COLUMNS = [
    "event_id", "event_time", "decision_time", "market", "selection", "bookmaker",
    "price", "price_timestamp", "source", "source_timestamp", "features",
    "feature_version", "model_version", "probability", "fair_price", "EV", "realistic_EV",
    "confidence", "data_trust", "all_gates", "stake", "decision", "provenance", "raw_hash",
]


@dataclass(frozen=True)
class DecisionRecord:
    event_id: str
    event_time: str
    decision_time: str
    market: str
    selection: str
    bookmaker: str
    price: float | None
    price_timestamp: str | None
    source: str | None
    source_timestamp: str | None
    features: dict[str, Any]
    feature_version: str
    model_version: str
    probability: float | None
    fair_price: float | None
    EV: float | None
    realistic_EV: float | None
    confidence: str | None
    data_trust: str
    all_gates: dict[str, Any]
    stake: float
    decision: str
    provenance: dict[str, Any]
    raw_hash: str

    def as_dict(self):
        return asdict(self)


def canonical_hash(payload: dict[str, Any]) -> str:
    clean = {k: payload[k] for k in sorted(payload) if k not in {"raw_hash"}}
    return hashlib.sha256(json.dumps(clean, sort_keys=True, default=str, separators=(",", ":")).encode()).hexdigest()


def build_decision_record(*, event_id: str, event_time: Any, decision_time: Any, market: str,
                          selection: str, bookmaker: str, price: float | None, source: str | None,
                          source_timestamp: Any | None, features: dict[str, Any], feature_version: str,
                          model_version: str, probability: float | None, confidence: str | None,
                          stake: float, decision: str, raw_hash: str | None = None,
                          realistic_ev: float | None = None, provenance: dict[str, Any] | None = None) -> DecisionRecord:
    fair = (1.0 / float(probability)) if probability and probability > 0 else None
    ev = (float(probability) * float(price) - 1.0) if probability is not None and price and price > 1 else None
    row = {
        "event_id": str(event_id), "event_time": str(pd.Timestamp(event_time, tz="UTC")),
        "decision_time": str(pd.Timestamp(decision_time, tz="UTC")), "market": str(market),
        "selection": str(selection), "bookmaker": str(bookmaker), "price": price,
        "price_timestamp": str(pd.Timestamp(source_timestamp, tz="UTC")) if source_timestamp is not None else None,
        "source": source, "source_timestamp": str(pd.Timestamp(source_timestamp, tz="UTC")) if source_timestamp is not None else None,
        "features": features, "feature_version": feature_version, "model_version": model_version,
        "probability": probability, "fair_price": fair, "EV": ev, "realistic_EV": realistic_ev,
        "confidence": confidence, "stake": float(stake), "decision": decision,
        "provenance": provenance or {}, "raw_hash": raw_hash or "",
    }
    effective_hash = raw_hash or canonical_hash(row)
    gates = verify_odds({"price": price, "available_at": source_timestamp, "source_timestamp": source_timestamp,
                         "source": source, "raw_hash": effective_hash, "source_record_id": effective_hash}, decision_time=decision_time)
    row["all_gates"] = gates.as_dict()
    row["data_trust"] = "EXACT_PIT" if gates.odds_scientifically_eligible else "NON_PIT"
    row["raw_hash"] = effective_hash
    return DecisionRecord(**row)
