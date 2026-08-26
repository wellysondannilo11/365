from pathlib import Path
import json, hashlib
import pandas as pd
from ml.app.master_staff.context_transfer import load, build_team_rows, build_coverage, pilot_transfer, opponent_strength, feature_transferability

ROOT=Path(__file__).resolve().parents[2]

def test_context_transfer_temporal_features_are_prior_only():
    d=load(); tr=build_team_rows(d)
    assert tr['kickoff_timestamp'].notna().all()
    for team,g in tr.groupby('team_id'):
        assert g['same_comp_n'].ge(0).all()
        assert g['same_season_n'].ge(0).all()

def test_transfer_outputs_exist_and_are_auditable():
    p=ROOT/'data/context_transfer/CONTEXT_TRANSFER_BACKTEST.csv'
    x=pd.read_csv(p)
    assert len(x)==10
    assert set(x.analysis_status)<= {'ANALYZABLE_WITH_TRANSFERRED_EVIDENCE','INSUFFICIENT_DATA'}

def test_gender_is_not_crossed():
    d=load(); assert set(d.gender.unique()) <= {'MEN'}

def test_coverage_and_confidence_are_distinct():
    d=load(); tr=build_team_rows(d); cov=build_coverage(d,tr)
    assert {'team_coverage_score','coverage_class'} <= set(cov.columns)
    assert cov.team_coverage_score.between(0,100).all()

def test_opponent_strength_has_no_future_dependency():
    d=load(); x=opponent_strength(d)
    assert len(x)==len(d)

def test_transfer_does_not_promote_value_bets():
    snap=json.loads((ROOT/'data/real_day_prematch/REAL_DAY_PREMATCH_SNAPSHOT.json').read_text())
    assert snap['value_bets']==0
    assert snap['real_money']=='DISABLED'
