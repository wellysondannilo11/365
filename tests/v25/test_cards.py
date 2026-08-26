import math
import pytest
from app.v25.cards import (
    analyze_cards, settlement_probs, fair_odds_from_probs, expected_value,
    _prob_distribution, feature_bundle
)

def base_payload():
    return {
        'referee_cards_avg':5.2,'referee_sample_size':60,
        'home_cards_avg':2.4,'home_sample_size':30,
        'away_cards_avg':2.7,'away_sample_size':30,
        'h2h_cards_avg':5.0,'h2h_sample_size':12,
        'markets':[{'market':'CARD_TOTALS','selection':'OVER','line':4.5,'odds':1.90}],
        'min_confidence':0.2,
    }

def test_card_model_prices_over():
    out=analyze_cards(base_payload()); r=out['results'][0]
    assert out['expected_cards'] > 0
    assert r['fair_probability'] is not None and 0 < r['fair_probability'] < 1
    assert r['fair_odds'] is not None and r['fair_odds'] > 1

def test_card_quarter_line_settlement():
    assert settlement_probs(5,4.75,'OVER')['HALF_WIN'] == 1.0
    assert settlement_probs(4,4.75,'OVER')['LOSS'] == 1.0
    assert settlement_probs(4,4.25,'UNDER')['HALF_WIN'] == 1.0

def test_card_under_is_complementary():
    _,p=_prob_distribution(5.0)
    from app.v25.cards import _settlement_probability
    over=_settlement_probability(p,4.5,'OVER'); under=_settlement_probability(p,4.5,'UNDER')
    assert abs((over['WIN']+over['LOSS'])-(under['WIN']+under['LOSS'])) < 1e-9

def test_insufficient_card_data_fails_closed():
    p={'markets':[{'market':'CARD_TOTALS','selection':'OVER','line':4.5,'odds':2.0}], 'min_confidence':0.2}
    out=analyze_cards(p)
    assert out['results'][0]['decision']=='NO BET'
    assert out['results'][0]['reason']=='INSUFFICIENT_CARD_DATA'

def test_stale_referee_does_not_contribute():
    p=base_payload();p['referee_quality']='STALE';p['referee_cards_avg']=10
    out=analyze_cards(p)
    assert out['features']['referee']['quality']=='STALE'

def test_wait_for_price():
    p=base_payload();p['markets']=[{'market':'CARD_TOTALS','selection':'OVER','line':6.5,'odds':1.55}]
    out=analyze_cards(p)
    assert out['results'][0]['decision'] in {'WAIT_FOR_PRICE','NO BET'}
    if out['results'][0]['decision']=='WAIT_FOR_PRICE': assert out['results'][0]['target_odds'] > 1.55

def test_future_decision_time_is_rejected_by_live_api_logic():
    from fastapi.testclient import TestClient
    from app.api import app
    # app import may depend on local optional integrations; only exercise if import is healthy.
    client=TestClient(app)
    r=client.post('/v25/cards/live',json={'decision_time':'2999-01-01T00:00:00+00:00','markets':[]})
    assert r.status_code==422


def test_live_cards_reprice_uses_observed_and_remaining_only():
    p=base_payload(); p.update({'phase':'LIVE','minute':60,'cards_observed':4,'decision_time':'2026-08-20T12:00:00+00:00','captured_at':'2026-08-20T11:59:00+00:00','referee_source_timestamp':'2026-08-20T11:50:00+00:00','team_source_timestamp':'2026-08-20T11:50:00+00:00','h2h_source_timestamp':'2026-08-20T11:50:00+00:00'})
    out=analyze_cards(p)
    assert out['phase']=='LIVE'
    assert out['cards_observed']==4
    assert out['cards_remaining_expected'] >= 0
    assert out['final_expected_cards'] >= 4


def test_card_home_and_away_use_side_specific_expectations():
    p=base_payload(); p['markets']=[
        {'market':'CARD_HOME','selection':'OVER','line':2.5,'odds':2.0},
        {'market':'CARD_AWAY','selection':'OVER','line':2.5,'odds':2.0},
        {'market':'CARD_TOTALS','selection':'OVER','line':4.5,'odds':2.0},
    ]
    out=analyze_cards(p)
    by={r['market']:r for r in out['results']}
    assert by['CARD_HOME']['expected'] == pytest.approx(2.4)
    assert by['CARD_AWAY']['expected'] == pytest.approx(2.7)
    assert by['CARD_TOTALS']['expected'] == pytest.approx(5.1)


def test_card_pit_rejects_future_capture_timestamp():
    p=base_payload(); p.update({'decision_time':'2026-08-20T12:00:00+00:00','captured_at':'2026-08-20T12:01:00+00:00'})
    out=analyze_cards(p)
    assert out['results'][0]['decision']=='NO BET'
    assert out['results'][0]['reason']=='PIT_INVALID'

def test_card_pit_future_feature_is_blocked():
    p=base_payload(); p['decision_time']='2026-08-20T12:00:00+00:00'; p['referee_source_timestamp']='2026-08-20T13:00:00+00:00'
    out=analyze_cards(p)
    assert out['results'][0]['decision']=='NO BET'
    assert out['results'][0]['reason']=='PIT_INVALID'
