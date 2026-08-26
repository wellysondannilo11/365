from pathlib import Path
import pandas as pd
import json, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'ml'))
from app.master_staff.round_analyzer import load_round, add_market_math, run_round

def test_round_has_five_real_sourced_matches():
    d=load_round(ROOT/'data/raw/round_2026-08-20_web_verified.json')
    assert len(d)==5
    assert set(d.competition)=={'CONMEBOL Libertadores','CONMEBOL Sudamericana'}

def test_date_level_odds_do_not_pass_pit_gate():
    d=add_market_math(load_round(ROOT/'data/raw/round_2026-08-20_web_verified.json'))
    assert not d.market_pit_eligible.any()
    assert (d.value_gate=='NO_BET').all()

def test_market_math_is_factual_only():
    d=add_market_math(load_round(ROOT/'data/raw/round_2026-08-20_web_verified.json'))
    assert (d.home_implied > 0).all()
    assert (d.home_market_fair_prob.between(0,1)).all()

def test_real_money_disabled_in_package_config():
    text=(ROOT/'data/master_staff/MASTER_STAFF_MANIFEST.json').read_text()
    assert 'DISABLED' in text
