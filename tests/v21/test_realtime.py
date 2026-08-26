from datetime import datetime, timezone, timedelta
from ml.app.v21.realtime import FeedHealth, FeedStatus, ResilientPoller, validate_live_snapshot

def test_feed_health_stale_and_online():
    h=FeedHealth('x',max_age_seconds=10,delayed_after_seconds=2)
    now=datetime.now(timezone.utc)
    assert h.observe(now,now)==FeedStatus.ONLINE
    assert h.observe(now-timedelta(seconds=11),now)==FeedStatus.STALE
    assert not h.can_decide()

def test_feed_future_data_blocks():
    now=datetime.now(timezone.utc)
    ok,reasons=validate_live_snapshot({'event_id':'e','captured_at':(now+timedelta(seconds=1)).isoformat()},now)
    assert not ok and 'FUTURE_DATA' in reasons

def test_resilient_poller_retries():
    calls={'n':0}
    def fn():
        calls['n']+=1
        if calls['n']<3: raise RuntimeError('x')
        return 7
    assert ResilientPoller(retries=3,base_delay=0).call(fn)==7
    assert calls['n']==3
