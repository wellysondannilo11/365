import pandas as pd
import numpy as np

from ml.app.research.cycle2 import (
    build_chronological_features, normalize_market_probabilities,
    research_metric_status, build_target
)

def tiny_df():
    return pd.DataFrame({
        "match_id":["a","b","c","d"],
        "kickoff_timestamp":pd.to_datetime(["2024-01-01","2024-01-02","2024-01-03","2024-01-04"],utc=True),
        "home_team":["A","A","B","A"],"away_team":["B","C","A","D"],
        "home_goals":[1,2,0,3],"away_goals":[0,1,1,0],
        "home_shots":[10,12,8,15],"away_shots":[5,9,11,4],
        "home_sot":[4,5,2,7],"away_sot":[2,3,4,1],
        "home_corners":[5,6,3,7],"away_corners":[2,4,5,1],
        "home_cards":[2,1,3,2],"away_cards":[1,2,2,1],
        "odds_1":[2.0,1.8,3.0,1.7],"odds_x":[3.2,3.4,3.0,3.6],"odds_2":[3.5,4.0,2.4,4.5],
    })

def test_current_match_outcome_is_not_a_feature():
    d=tiny_df(); f=build_chronological_features(d)
    row=f.loc[f.match_id=="d"].iloc[0]
    assert row["home_goals"] == 3
    assert row["prior_home_goals_for"] != 3
    assert abs(row["prior_home_goals_for"] - (4/3)) < 1e-12

def test_market_probabilities_are_normalized():
    p=normalize_market_probabilities(2.0,3.0,5.0)
    assert abs(sum(p.values())-1.0)<1e-12
    assert p["home"] > 0 and p["draw"] > 0 and p["away"] > 0

def test_non_pit_metrics_cannot_be_labeled_validated():
    assert research_metric_status(pit_count=0) == "RESEARCH_ONLY_NON_PIT"
    assert research_metric_status(pit_count=1) == "PIT_ELIGIBLE_RESEARCH"

def test_targets_are_derived_from_outcomes():
    d=tiny_df();
    assert build_target(d,"home_win").tolist() == [1,1,0,1]
    assert build_target(d,"over_2_5").tolist() == [0,1,0,1]

def test_pricing_is_explicitly_non_pit():
    from ml.app.research.cycle2 import pricing_research
    r=pricing_research(pd.Series([0.6]),pd.Series([2.0]))
    assert r.loc[0,"fair_odds"] == 1/0.6
    assert r.loc[0,"scientific_status"] == "RESEARCH_ONLY_NON_PIT"

def test_sizing_is_theoretical_only():
    from ml.app.research.cycle2 import simulate_sizing
    r=simulate_sizing([0.6,0.6],[2.0,2.0],[1,0])
    assert set(r.status) == {"THEORETICAL_NON_PIT"}
    assert list(r.stake_u) == [0.25,0.5,1.0,1.5,2.0]

def test_benchmark_preserves_locked_holdout():
    from ml.app.research.cycle2 import build_chronological_features, run_benchmark
    base=tiny_df()
    rows=[]
    for i in range(240):
        r=base.iloc[i%4].copy()
        r["match_id"]=f"m{i}"
        r["kickoff_timestamp"]=pd.Timestamp("2020-01-01",tz="UTC")+pd.Timedelta(days=i)
        rows.append(r)
    d=build_chronological_features(pd.DataFrame(rows))
    res, selections, meta=run_benchmark(d,"home_win",feature_set="BASELINE",min_train=100,validation=30,test=30,holdout_fraction=.15)
    assert meta["holdout_locked"] is True
    assert meta["holdout_events"] > 0
    assert len(res) > 0

def test_market_only_oos_uses_price_only():
    from ml.app.research.cycle2 import market_only_oos
    d=tiny_df()
    r=market_only_oos(d,"home_win",min_train=1,validation=1,test=1,holdout_fraction=0.0)
    assert not r.empty
    assert set(r["model"]) == {"market_only"}

def test_benchmark_includes_ensemble_candidate():
    from ml.app.research.cycle2 import build_chronological_features, run_benchmark
    base=tiny_df(); rows=[]
    for i in range(220):
        r=base.iloc[i%4].copy(); r["match_id"]=f"e{i}"; r["kickoff_timestamp"]=pd.Timestamp("2020-01-01",tz="UTC")+pd.Timedelta(days=i); rows.append(r)
    d=build_chronological_features(pd.DataFrame(rows))
    res,_,_=run_benchmark(d,"home_win",feature_set="BASELINE",min_train=90,validation=30,test=30,holdout_fraction=.15)
    assert "ensemble" in set(res.model)


def test_date_only_kickoff_is_supported():
    d=tiny_df(); d["kickoff_timestamp"]=["2024-01-01","2024-01-02T12:00:00Z","2024-01-03","2024-01-04T12:00:00Z"]
    f=build_chronological_features(d)
    assert len(f)==4

def test_logistic_ablation_marks_missing_features_not_eligible():
    from ml.app.research.cycle2 import run_logistic_ablation
    d=tiny_df(); r=run_logistic_ablation(d,"home_win",{"BASE":["elo_delta"],"MISSING":["xg_feature"]},min_train=1,validation=1,test=1,holdout_fraction=0)
    assert set(r.loc[r.feature_set=="MISSING","status"]) == {"NOT_ELIGIBLE"}

def test_pricing_research_preserves_row_alignment_with_nonzero_indices():
    from ml.app.research.cycle2 import pricing_research
    p=pd.Series([0.5,0.6],index=[10,11]); o=pd.Series([2.0,2.0],index=[10,11])
    r=pricing_research(p,o)
    assert len(r)==2
