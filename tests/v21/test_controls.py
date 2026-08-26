from datetime import datetime, timezone
from ml.app.v21.controls import RiskControllerV21, ExposureLimits

def test_kill_switch_and_exposure():
    r=RiskControllerV21(ExposureLimits(max_per_event=1,max_daily_exposure=2,max_simultaneous=2))
    now=datetime.now(timezone.utc)
    assert r.allowed(now,'e','L','M',1)[0]
    r.open('e','L','M',1,'e')
    assert r.allowed(now,'e','L','M',0.5)[0] is False
    r.set_kill_switch(True)
    assert r.allowed(now,'e2','L','M',0.1)[1]=='GLOBAL_KILL_SWITCH'
