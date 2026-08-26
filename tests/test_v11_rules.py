from ml.app.market import fair_odds, edge, ev, price_anomaly
from ml.app.mlops.champion_challenger import compare

def test_fair_odds_and_value():
    assert round(fair_odds(.50),2)==2.00
    assert abs(edge(.50,2.50)-.10)<1e-9
    assert abs(ev(.50,2.50)-.25)<1e-9
    assert price_anomaly(2.50,2.0)>0

def test_champion_challenger_gate():
    assert compare({"oos_logloss":.60,"oos_brier":.20},
                    {"oos_logloss":.58,"oos_brier":.18,"sample":200})["promote"]
