from datetime import datetime,timezone
from ml.app.v20.live_engine import LiveState,LiveRepricingEngine

def test_live_insufficient_sample_fails_closed():
    s=LiveState('e',datetime.now(timezone.utc),10,0,0,.05,.03,shots=1)
    r=LiveRepricingEngine().reprice(s,1.2,.9,[{'market':'1X2','selection':'Home','odds':2.0}])
    assert r['status']=='NO BET' and r['reason']=='INSUFFICIENT_SAMPLE'

def test_live_repricing_produces_market_state():
    s=LiveState('e',datetime.now(timezone.utc),35,1,0,.9,.25,shots=12,shots_on_target=5,corners=4)
    r=LiveRepricingEngine().reprice(s,1.4,.9,[{'market':'TOTAL','selection':'Over','line':2.5,'odds':2.2}])
    assert r['status']=='OK' and r['pricing']['market_state']=='LIVE'
