import math
import pandas as pd
import pytest

from ml.app.v19.pricing import (
    poisson_scoreline_distribution,
    derived_market_probabilities,
    asian_handicap_outcomes,
    fair_odds_from_probability,
    market_dislocation,
)
from ml.app.v19.engine import PricingEngine
from ml.app.v19.market_intelligence import normalize_market_rows, de_vig_market, discover_dislocations
from ml.app.v19.validation import validate_distribution, fair_odds_sanity
from ml.app.v19.paper import ImmutablePaperBet, ImmutablePaperLedger


def test_scoreline_distribution_normalizes():
    d = poisson_scoreline_distribution(1.4, 1.1, max_goals=8)
    assert math.isclose(sum(x.probability for x in d), 1.0, abs_tol=1e-10)
    assert len(d) == 81
    assert validate_distribution([x.__dict__ for x in d])['status'] == 'PASS'


def test_dixon_coles_distribution_normalizes():
    d = poisson_scoreline_distribution(1.4, 1.1, max_goals=8, dixon_coles_rho=-0.08)
    assert math.isclose(sum(x.probability for x in d), 1.0, abs_tol=1e-10)


def test_derived_1x2_and_totals_and_btts_sum():
    d = poisson_scoreline_distribution(1.5, 1.0)
    rows = derived_market_probabilities(d)
    one = [x for x in rows if x.market == '1X2']
    assert math.isclose(sum(x.probability for x in one), 1.0, abs_tol=1e-8)
    for line in (0.5, 1.5, 2.5, 3.5):
        x = [x for x in rows if x.market == 'TOTAL' and x.line == line]
        assert math.isclose(sum(y.probability for y in x), 1.0, abs_tol=1e-8)
    btts = [x for x in rows if x.market == 'BTTS']
    assert math.isclose(sum(x.probability for x in btts), 1.0, abs_tol=1e-8)


def test_fair_odds():
    assert fair_odds_from_probability(0.25) == 4.0
    assert fair_odds_from_probability(0) is None
    assert fair_odds_sanity(0.2, 5.0)
    with pytest.raises(ValueError):
        fair_odds_from_probability(1.01)


def test_asian_handicap_has_push_for_whole_line():
    d = poisson_scoreline_distribution(1.3, 1.3)
    o = asian_handicap_outcomes(d, 0.0, 'HOME')
    assert o['push'] > 0
    assert math.isclose(sum(o.values()), 1.0, abs_tol=1e-8)


def test_market_dislocation_ev():
    x = market_dislocation(0.30, 4.0, market_probability=0.25, market='1X2', selection='Home')
    assert math.isclose(x.probability_edge, 0.05)
    assert math.isclose(x.ev, 0.20)
    assert math.isclose(x.fair_odds, 1/0.30)


def test_market_normalization_and_devig():
    d = pd.DataFrame([
        {'event_id':'e1','bookmaker':'a','market':'1X2','selection':'Home','odds':2.0},
        {'event_id':'e1','bookmaker':'a','market':'1X2','selection':'Draw','odds':3.5},
        {'event_id':'e1','bookmaker':'a','market':'1X2','selection':'Away','odds':3.5},
    ])
    n = normalize_market_rows(d)
    x = de_vig_market(n)
    assert math.isclose(float(x['fair_market_probability'].sum()), 1.0, abs_tol=1e-10)


def test_strict_pit_market_rejects_missing_timestamps():
    d = pd.DataFrame([{'event_id':'e1','bookmaker':'a','market':'1X2','selection':'Home','odds':2.0}])
    with pytest.raises(ValueError, match='STRICT_PIT_MARKET_REQUIRES'):
        normalize_market_rows(d, strict_pit=True)


def test_dislocation_respects_decision_time():
    markets = [
        {'event_id':'e1','bookmaker':'a','market':'1X2','selection':'Home','odds':4.0,'line':None,'available_at':'2026-01-01T10:00:00Z','source_timestamp':'2026-01-01T10:00:00Z'},
        {'event_id':'e1','bookmaker':'a','market':'1X2','selection':'Home','odds':2.0,'line':None,'available_at':'2026-01-01T12:00:00Z','source_timestamp':'2026-01-01T12:00:00Z'},
    ]
    model = [{'event_id':'e1','market':'1X2','selection':'Home','line':None,'probability':0.30}]
    out = discover_dislocations(model, markets, strict_pit=True, decision_time='2026-01-01T11:00:00Z')
    assert len(out) == 1
    assert math.isclose(out[0]['market_odds'], 4.0)


def test_engine_supports_pre_and_live_states_without_two_pricing_cores():
    e = PricingEngine()
    pre = e.price(event_id='e1', decision_time=pd.Timestamp('2026-01-01T10:00:00Z').to_pydatetime(), home_expected_goals=1.2, away_expected_goals=1.0, market_state='PRE')
    live = e.price(event_id='e1', decision_time=pd.Timestamp('2026-01-01T11:00:00Z').to_pydatetime(), home_expected_goals=0.6, away_expected_goals=0.4, market_state='LIVE')
    assert pre['pricing_engine_version'] == live['pricing_engine_version']
    assert pre['market_state'] == 'PRE' and live['market_state'] == 'LIVE'


def test_immutable_paper_bet_persists(tmp_path):
    ledger = ImmutablePaperLedger(tmp_path/'signals.jsonl')
    bet = ImmutablePaperBet('s1','e1','2026-01-01T10:00:00Z','1X2','Home',None,'bk',4.0,0.30,3.333,0.25,0.05,0.20,'m1','f1','c1','hash','PIT_EXACT')
    out = ledger.append(bet)
    assert out['signal_id'] == 's1'
    assert (tmp_path/'signals.jsonl').exists()
    with pytest.raises(Exception):
        bet.edge = 0.1


def test_asian_settlement_ev_and_fair_odds():
    from ml.app.v19.settlement import SettlementProbabilities, expected_value, fair_odds
    p = SettlementProbabilities(win=0.4, half_win=0.0, push=0.1, half_loss=0.0, loss=0.5)
    assert math.isclose(expected_value(2.0, p), -0.1)
    assert math.isclose(fair_odds(p), 2.25)


def test_price_movement_and_clv():
    from ml.app.v19.price_movement import build_price_timeline, clv
    rows=[
        {'event_id':'e1','market':'1X2','selection':'Home','bookmaker':'bk','odds':4.0,'available_at':'2026-01-01T10:00:00Z'},
        {'event_id':'e1','market':'1X2','selection':'Home','bookmaker':'bk','odds':3.5,'available_at':'2026-01-01T11:00:00Z'},
    ]
    x=build_price_timeline(rows, decision_time='2026-01-01T12:00:00Z', strict_pit=True)
    assert x[0]['opening_price']==4.0 and x[0]['current_price']==3.5
    assert clv(4.0,3.5)>0
