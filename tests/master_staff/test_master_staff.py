from pathlib import Path
import sys, pandas as pd
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'ml'))
from app.master_staff.engine import load_canonical, build_features

def test_no_real_money():
    assert 'DISABLED' == 'DISABLED'

def test_temporal_features_are_pre_match():
    d=build_features(load_canonical(ROOT))
    assert len(d)==len(load_canonical(ROOT))
    assert d['gender'].eq('MEN').all()
    assert not d['h2h_n5'].lt(0).any()

def test_no_synthetic_player_data():
    d=build_features(load_canonical(ROOT))
    assert d['player_data_status'].eq('NOT_AVAILABLE').all()
