import pandas as pd
from app.research.cycle3 import assign_selection, assign_stakes, simulate_portfolio


def test_selection_and_stake_pipeline_never_exceeds_two_units():
    df = pd.DataFrame([
        {"probability": 0.80, "odds": 2.50, "outcome": 1, "pit_status": "NON_PIT"},
        {"probability": 0.55, "odds": 2.10, "outcome": 0, "pit_status": "NON_PIT"},
    ])
    selected = assign_selection(df, ev_threshold=0.0)
    selected["data_quality"] = 1.0
    selected["uncertainty"] = 0.0
    selected = assign_stakes(selected, "dynamic")
    assert selected["stake"].max() <= 2.0
    result = simulate_portfolio(selected)
    assert result["scientific_status"] == "COUNTERFACTUAL_NON_PIT"
