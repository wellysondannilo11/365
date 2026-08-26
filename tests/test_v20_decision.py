from datetime import datetime, timezone
from ml.app.v20.selection import Candidate, evaluate, rank_candidates
from ml.app.v20.stake import StakePolicy, kelly_fraction, size_stake

def test_value_and_zero_value_stake():
    p=0.60;o=2.0
    assert kelly_fraction(p,o)>0
    r=evaluate(Candidate('e1','ML','Home',o,p),policy=StakePolicy(max_stake_units=1,bankroll_units=50),min_edge=.05,min_ev=.05)
    assert r['decision']=='BET' and r['stake']>0
    r2=evaluate(Candidate('e2','ML','Home',1.50,.60),policy=StakePolicy())
    assert r2['decision']=='NO BET' and r2['stake']==0

def test_no_bet_gates():
    c=Candidate('e','ML','Home',2.5,.50,data_quality=50,uncertainty=.30,pit_ok=False)
    r=evaluate(c,policy=StakePolicy())
    assert r['decision']=='NO BET'
    assert 'PIT_FAILURE' in r['no_bet_reason'] and 'LOW_DATA_QUALITY' in r['no_bet_reason']

def test_global_ranking_prefers_best_value():
    cs=[Candidate('a','ML','Home',2.0,.60),Candidate('b','ML','Home',2.2,.55)]
    out=rank_candidates(cs,policy=StakePolicy())
    assert out[0]['event_id']=='a'
