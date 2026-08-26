import pandas as pd
from ml.app.cycle16.statistics import bootstrap_mean_ci, drawdown, execution_stress, holm_bonferroni


def test_bootstrap_is_seeded():
    a=bootstrap_mean_ci([1,-1,1,-1], n=200, seed=7)
    b=bootstrap_mean_ci([1,-1,1,-1], n=200, seed=7)
    assert a==b and a['n']==4


def test_drawdown():
    assert drawdown([1,-2,1,-1])==2.0


def test_execution_stress_preserves_base():
    d=pd.DataFrame({'entry_odds':[2,2], 'result':['WIN','LOSS'], 'stake_units':[1,1]})
    out=execution_stress(d)
    assert out['base']['slippage_pct']==0.0
    assert len(out['grid'])>1


def test_holm_bonferroni():
    out=holm_bonferroni([0.01,0.04,0.2])
    assert out[0]['reject'] is True
    assert out[-1]['reject'] is False
