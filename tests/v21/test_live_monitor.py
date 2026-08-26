from datetime import datetime,timezone,timedelta
from ml.app.v21.live_monitor import LiveMonitor
from ml.app.v21.service import DecisionServiceV21

def test_live_monitor_blocks_stale(tmp_path):
    now=datetime.now(timezone.utc);m=LiveMonitor(max_age_seconds=10);s=DecisionServiceV21();s.ledger.path=tmp_path/'l.jsonl';s.research.path=tmp_path/'r.jsonl'
    state={'event_id':'e','captured_at':(now-timedelta(seconds=30)).isoformat(),'minute':50,'home_goals':0,'away_goals':0,'home_xg':1,'away_xg':.5}
    out=m.observe(source='test',event_id='e',live_state=state,odds_rows=[],decision_time=now,decision_service=s)
    assert out['status']=='DATA QUALITY BLOCK'

def test_live_monitor_routes_online_data(tmp_path):
    now=datetime.now(timezone.utc);m=LiveMonitor(max_age_seconds=20);s=DecisionServiceV21();s.ledger.path=tmp_path/'l.jsonl';s.research.path=tmp_path/'r.jsonl'
    state={'event_id':'e','captured_at':(now-timedelta(seconds=1)).isoformat(),'minute':50,'home_goals':0,'away_goals':0,'home_xg':1,'away_xg':.5}
    odds=[{'market':'h2h','selection':'A','odds':2.0,'probability':.6,'available_at':(now-timedelta(seconds=1)).isoformat(),'sample_size':100}]
    out=m.observe(source='test',event_id='e',live_state=state,odds_rows=odds,decision_time=now,decision_service=s)
    assert out['status']=='FEED ONLINE'
