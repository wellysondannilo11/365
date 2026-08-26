from pathlib import Path
import json, pandas as pd
ROOT=Path(__file__).resolve().parents[2]

def test_gender_separation_test():
    d=pd.read_csv(ROOT/'data/canonical/football_historical_real_canonical.csv')
    assert 'gender' not in d.columns or set(d.gender.dropna().str.upper()) <= {'MEN','WOMEN'}

def test_entity_resolution_test():
    d=pd.read_csv(ROOT/'data/canonical/football_historical_real_canonical.csv')
    assert d.match_id.notna().all() and d.home_team.notna().all() and d.away_team.notna().all()

def test_H2H_temporal_test():
    h=pd.read_csv(ROOT/'data/master_staff/H2H_INTELLIGENCE.csv')
    assert (h.h2h_n3.fillna(0)>=0).all() and (h.h2h_n5.fillna(0)>=0).all() and (h.h2h_n10.fillna(0)>=0).all()

def test_importance_temporal_test():
    x=pd.read_csv(ROOT/'data/master_staff/IMPORTANCE_CONTEXT_2026-08-20.csv')
    assert set(x.pit_status)=={'DATE_LEVEL_PIT'}
    assert set(x.importance_state)<= {'KNOCKOUT_DECIDER','EXTREME_KNOCKOUT_DECIDER'}

def test_rivalry_test():
    x=pd.read_csv(ROOT/'data/master_staff/RIVALRY_REGISTRY.csv')
    assert len(x)==0

def test_player_impact_test():
    x=pd.read_csv(ROOT/'data/master_staff/PLAYER_RECORDS.csv')
    assert len(x)==0

def test_injury_test():
    x=pd.read_csv(ROOT/'data/master_staff/INJURY_RECORDS.csv')
    assert len(x)==0

def test_lineup_test():
    x=pd.read_csv(ROOT/'data/master_staff/LINEUP_RECORDS.csv')
    assert len(x)==0

def test_market_quality_test():
    x=pd.read_csv(ROOT/'data/processed/round_2026-08-20/ROUND_2026-08-20_INTELLIGENCE.csv')
    assert not x.market_pit_eligible.any()

def test_round_analyzer_test():
    x=pd.read_csv(ROOT/'data/processed/round_2026-08-20/ROUND_2026-08-20_INTELLIGENCE.csv')
    assert len(x)==5 and x.value_gate.eq('NO_BET').all()

def test_prematch_value_test():
    x=pd.read_csv(ROOT/'data/processed/round_2026-08-20/ROUND_2026-08-20_INTELLIGENCE.csv')
    assert not x.market_pit_eligible.any()
    assert x.edge_status.eq('EDGE_NOT_DETERMINED').all()
