from __future__ import annotations
import hashlib
import json
from typing import Any, Callable


class ReplayError(RuntimeError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str, separators=(",", ":"))


def replay_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(payload).encode()).hexdigest()


def replay_decision(snapshot: dict[str, Any], feature_builder: Callable, model_fn: Callable, decision_fn: Callable | None = None) -> dict[str, Any]:
    required = {"decision_id", "decision_time", "dataset_version", "feature_version", "model_version"}
    missing = sorted(required - snapshot.keys())
    if missing:
        raise ReplayError("REPLAY_MISSING_METADATA:" + ",".join(missing))

    features = feature_builder(snapshot, snapshot["decision_time"])
    prediction = model_fn(features)
    decision = decision_fn(prediction, snapshot) if decision_fn else prediction
    result = {
        "decision_id": snapshot["decision_id"],
        "dataset_version": snapshot["dataset_version"],
        "feature_version": snapshot["feature_version"],
        "model_version": snapshot["model_version"],
        "features": features,
        "prediction": prediction,
        "decision": decision,
    }
    result["replay_hash"] = replay_hash(result)
    return result


def assert_reproducible(snapshot: dict[str, Any], feature_builder: Callable, model_fn: Callable, decision_fn: Callable | None = None) -> dict[str, Any]:
    a = replay_decision(snapshot, feature_builder, model_fn, decision_fn)
    b = replay_decision(snapshot, feature_builder, model_fn, decision_fn)
    if a["replay_hash"] != b["replay_hash"]:
        raise ReplayError("REPLAY_FAILED")
    return a
