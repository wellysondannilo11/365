import pandas as pd
from ml.app.cycle16.h005 import evaluate_h005, THRESHOLD


def base(opening_semantics='EXPLICIT_OPENING'):
    return pd.DataFrame([
        {'event_id':'e1','bookmaker':'Bet365','market':'1X2','selection':'home','odds':2.10,'reference_odds':2.00,
         'pit_status':'EXACT_PIT','opening_semantics':opening_semantics,'temporal_evidence':'PROVIDER_NATIVE_SNAPSHOT'},
        {'event_id':'e1','bookmaker':'Average','market':'1X2','selection':'home','odds':2.00,'reference_odds':2.00,
         'pit_status':'EXACT_PIT','opening_semantics':opening_semantics,'temporal_evidence':'PROVIDER_NATIVE_SNAPSHOT'},
    ])


def test_h005_is_frozen_at_two_percent():
    bets, meta = evaluate_h005(base())
    assert THRESHOLD == 0.02
    assert meta['threshold'] == 0.02
    assert len(bets) == 1


def test_h005_refuses_non_opening_snapshot():
    bets, meta = evaluate_h005(base('SNAPSHOT_ONLY'))
    assert len(bets) == 0
    assert meta['status'] == 'NO_EXPLICIT_OPENING'


def test_h005_requires_exact_pit():
    d=base(); d['pit_status']='NON_PIT'
    bets, meta=evaluate_h005(d)
    assert len(bets) == 0
    assert meta['status'] == 'NO_EXACT_PIT'
