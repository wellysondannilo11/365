import pandas as pd

from ml.app.research.cycle18.exact_pit import classify_exact_pit_row
from ml.app.research.cycle18.h005 import H005_THRESHOLD, evaluate_h005_frozen


def base():
    return {
        "event_id": "E1",
        "provider_timestamp": "2026-08-20T10:00:00Z",
        "decision_timestamp": "2026-08-20T10:05:00Z",
        "kickoff_timestamp": "2026-08-20T12:00:00Z",
        "source": "provider",
        "provenance": "raw://x",
        "raw_hash": "abc",
        "odds": 2.1,
    }


def test_exact_pit_contract_is_strict():
    assert classify_exact_pit_row(base()).status == "EXACT_PIT"


def test_received_at_is_not_a_provider_timestamp_fallback():
    row = base()
    row.pop("provider_timestamp")
    row["received_at"] = "2026-08-20T10:00:00Z"
    assert classify_exact_pit_row(row).status == "NON_PIT"


def test_future_provider_snapshot_is_invalid():
    row = base()
    row["provider_timestamp"] = "2026-08-20T13:00:00Z"
    assert classify_exact_pit_row(row).status == "PIT_INVALID"


def test_h005_threshold_is_frozen():
    assert H005_THRESHOLD == 0.02
    df = pd.DataFrame([
        {**base(), "market": "1X2", "selection": "HOME", "bookmaker": "Bet365", "opening_status": "CONFIRMED", "pit_status": "EXACT_PIT"},
        {**base(), "market": "1X2", "selection": "HOME", "bookmaker": "Average", "odds": 2.0, "opening_status": "CONFIRMED", "pit_status": "EXACT_PIT"},
    ])
    result = evaluate_h005_frozen(df)
    assert result["threshold"] == 0.02
    assert result["bets"] == 1
