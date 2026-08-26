import pandas as pd
from ml.app.research.cycle17.h005 import H005_THRESHOLD, evaluate_h005


def test_h005_threshold_is_frozen_at_two_percent():
    assert H005_THRESHOLD == 0.02


def test_h005_requires_exact_pit_and_opening_evidence():
    rows = pd.DataFrame([
        {"event_id":"e1","kickoff_timestamp":"2026-08-24T20:00:00Z","provider_timestamp":"2026-08-24T17:00:00Z","decision_timestamp":"2026-08-24T17:05:00Z","provider":"Bet365","bookmaker":"Bet365","market":"1X2","selection":"HOME","odds":2.10,"opening_status":"CONFIRMED","pit_status":"EXACT_PIT","result":"WIN"},
        {"event_id":"e1","kickoff_timestamp":"2026-08-24T20:00:00Z","provider_timestamp":"2026-08-24T17:00:00Z","decision_timestamp":"2026-08-24T17:05:00Z","provider":"Reference","bookmaker":"Average","market":"1X2","selection":"HOME","odds":2.00,"opening_status":"CONFIRMED","pit_status":"EXACT_PIT","result":"WIN"},
    ])
    report = evaluate_h005(rows)
    assert report["threshold"] == 0.02
    assert report["eligible_events"] == 1
    assert report["bets"] == 1


def test_h005_does_not_use_non_pit_rows():
    rows = pd.DataFrame([
        {"event_id":"e1","kickoff_timestamp":"2026-08-24T20:00:00Z","provider_timestamp":"2026-08-24T17:00:00Z","decision_timestamp":"2026-08-24T17:05:00Z","provider":"Bet365","bookmaker":"Bet365","market":"1X2","selection":"HOME","odds":2.10,"opening_status":"CONFIRMED","pit_status":"NON_PIT","result":"WIN"},
        {"event_id":"e1","kickoff_timestamp":"2026-08-24T20:00:00Z","provider_timestamp":"2026-08-24T17:00:00Z","decision_timestamp":"2026-08-24T17:05:00Z","provider":"Reference","bookmaker":"Average","market":"1X2","selection":"HOME","odds":2.00,"opening_status":"CONFIRMED","pit_status":"EXACT_PIT","result":"WIN"},
    ])
    report = evaluate_h005(rows)
    assert report["eligible_events"] == 0
    assert report["bets"] == 0


def test_h005_reference_bookmaker_is_average_only():
    from ml.app.research.cycle17.h005 import REFERENCE_BOOKMAKER
    assert REFERENCE_BOOKMAKER == "Average"
