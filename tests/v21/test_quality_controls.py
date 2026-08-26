from datetime import datetime, timezone, timedelta
from ml.app.v21.quality import validate_market_snapshot, validate_live_state

def test_market_pit_and_odds():
    now=datetime.now(timezone.utc)
    row={'event_id':'e','market':'h2h','selection':'A','odds':2.0,'available_at':(now-timedelta(seconds=1)).isoformat()}
    assert validate_market_snapshot(row,now)['ok']
    row['available_at']=(now+timedelta(seconds=1)).isoformat()
    q=validate_market_snapshot(row,now);assert not q['ok'] and 'POINT_IN_TIME_VIOLATION' in q['reasons']

def test_live_stale_fails_closed():
    now=datetime.now(timezone.utc)
    s={'event_id':'e','captured_at':(now-timedelta(seconds=30)).isoformat(),'minute':60,'home_goals':0,'away_goals':0,'home_xg':1,'away_xg':0.5}
    q=validate_live_state(s,now,max_age_seconds=20);assert not q['ok'] and 'STALE_LIVE_FEED' in q['reasons']
