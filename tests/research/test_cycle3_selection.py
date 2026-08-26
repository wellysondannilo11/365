import math
import pandas as pd

from app.research.cycle3 import (
    assign_selection,
    assign_stake,
    simulate_portfolio,
    summarize_ev_buckets,
)


def test_selection_requires_positive_ev_and_marks_non_pit():
    df = pd.DataFrame([
        {"probability": 0.60, "odds": 2.00, "outcome": 1, "pit_status": "NON_PIT"},
        {"probability": 0.40, "odds": 2.00, "outcome": 1, "pit_status": "NON_PIT"},
    ])
    out = assign_selection(df, ev_threshold=0.0)
    assert out.loc[0, "selection_status"] == "APPROVED_RESEARCH"
    assert out.loc[1, "selection_status"] == "REJECT"
    assert set(out["scientific_status"]) == {"COUNTERFACTUAL_NON_PIT"}


def test_dynamic_stake_respects_hard_two_unit_ceiling():
    assert assign_stake(0.60, 2.0, uncertainty=0.0, data_quality=1.0, edge=0.20) <= 2.0
    assert assign_stake(0.99, 10.0, uncertainty=0.0, data_quality=1.0, edge=0.89) == 2.0
    assert assign_stake(0.60, 2.0, uncertainty=1.0, data_quality=1.0, edge=0.20) == 0.0


def test_portfolio_simulation_reports_theoretical_non_pit_metrics():
    df = pd.DataFrame([
        {"odds": 2.0, "outcome": 1, "stake": 1.0},
        {"odds": 2.0, "outcome": 0, "stake": 1.0},
        {"odds": 3.0, "outcome": 1, "stake": 0.5},
    ])
    result = simulate_portfolio(df)
    assert result["bets"] == 3
    assert math.isclose(result["units"], 1.0, rel_tol=1e-9)
    assert result["scientific_status"] == "COUNTERFACTUAL_NON_PIT"


def test_ev_bucket_summary_keeps_negative_and_positive_buckets_separate():
    df = pd.DataFrame({
        "raw_ev": [-0.02, 0.01, 0.04, 0.12],
        "outcome": [0, 1, 0, 1],
        "odds": [2.0, 2.0, 2.0, 2.0],
    })
    out = summarize_ev_buckets(df)
    assert set(out["ev_bucket"]) == {"EV < 0", "0–2%", "2–5%", "10–15%"}
