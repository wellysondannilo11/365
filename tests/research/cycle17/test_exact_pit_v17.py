import pandas as pd
from ml.app.research.cycle17.exact_pit import classify_exact_pit


def test_exact_pit_requires_provider_timestamp_before_decision_and_kickoff():
    result = classify_exact_pit({
        "event_id": "e1",
        "kickoff_timestamp": "2026-08-24T20:00:00Z",
        "provider_timestamp": "2026-08-24T18:00:00Z",
        "decision_timestamp": "2026-08-24T18:05:00Z",
        "odds": 2.10,
        "provider": "provider-a",
        "provenance": "raw://e1",
        "raw_hash": "abc",
    })
    assert result.status == "EXACT_PIT"


def test_received_at_cannot_substitute_provider_timestamp():
    result = classify_exact_pit({
        "event_id": "e1",
        "kickoff_timestamp": "2026-08-24T20:00:00Z",
        "received_at": "2026-08-24T18:00:00Z",
        "decision_timestamp": "2026-08-24T18:05:00Z",
        "odds": 2.10,
        "provider": "provider-a",
        "provenance": "raw://e1",
        "raw_hash": "abc",
    })
    assert result.status == "NON_PIT"
    assert result.reason == "PROVIDER_TIMESTAMP_MISSING"


def test_future_provider_timestamp_is_invalid():
    result = classify_exact_pit({
        "event_id": "e1",
        "kickoff_timestamp": "2026-08-24T20:00:00Z",
        "provider_timestamp": "2026-08-24T18:10:00Z",
        "decision_timestamp": "2026-08-24T18:05:00Z",
        "odds": 2.10,
        "provider": "provider-a",
        "provenance": "raw://e1",
        "raw_hash": "abc",
    })
    assert result.status == "PIT_INVALID"
    assert result.reason == "PROVIDER_TIMESTAMP_AFTER_DECISION"


def test_provider_timestamp_after_kickoff_is_invalid():
    result = classify_exact_pit({
        "event_id": "e1",
        "kickoff_timestamp": "2026-08-24T18:00:00Z",
        "provider_timestamp": "2026-08-24T18:10:00Z",
        "decision_timestamp": "2026-08-24T18:05:00Z",
        "odds": 2.10,
        "provider": "provider-a",
        "provenance": "raw://e1",
        "raw_hash": "abc",
    })
    assert result.status == "PIT_INVALID"
    assert result.reason == "PROVIDER_TIMESTAMP_AFTER_KICKOFF"


def test_missing_kickoff_is_not_promoted_to_exact_pit():
    result = classify_exact_pit({
        "event_id": "e1",
        "provider_timestamp": "2026-08-24T18:00:00Z",
        "decision_timestamp": "2026-08-24T18:05:00Z",
        "odds": 2.10,
        "provider": "provider-a",
        "provenance": "raw://e1",
        "raw_hash": "abc",
    })
    assert result.status == "NON_PIT"
    assert result.reason == "KICKOFF_TIMESTAMP_MISSING"
