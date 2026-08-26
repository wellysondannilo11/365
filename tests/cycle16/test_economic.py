import pandas as pd
from ml.app.cycle16.economic import create_paper_bets, settle_paper_bets, calculate_real_clv, temporal_oos, walk_forward


def records():
    return pd.DataFrame([
      {'decision_id':'d1','event_id':'e1','decision_timestamp':'2026-01-01T10:00:00Z','entry_timestamp':'2026-01-01T10:00:00Z','entry_odds':2.0,'closing_odds':1.8,'result':'WIN','stake_units':1.0,'pit_status':'EXACT_PIT','hypothesis_id':'H005'},
      {'decision_id':'d2','event_id':'e2','decision_timestamp':'2026-01-02T10:00:00Z','entry_timestamp':'2026-01-02T10:00:00Z','entry_odds':2.5,'closing_odds':2.7,'result':'LOSS','stake_units':1.0,'pit_status':'EXACT_PIT','hypothesis_id':'H005'},
    ])


def test_paper_and_settlement_are_deterministic():
    bets=create_paper_bets(records())
    settled=settle_paper_bets(bets)
    assert len(settled)==2
    assert settled['profit_units'].tolist()==[1.0,-1.0]


def test_real_clv_uses_later_price_only():
    out=calculate_real_clv(records())
    assert out['valid_count']==2
    assert round(out['mean'],6)==round((2/1.8 + 2.5/2.7 - 2)/2,6)


def test_temporal_oos_and_walk_forward():
    d=records(); d['result']='WIN'; d['profit_units']=1.0
    split=temporal_oos(d, '2026-01-02T00:00:00Z')
    assert len(split['train'])==1 and len(split['test'])==1
    folds=walk_forward(d, folds=2)
    assert len(folds)==2
