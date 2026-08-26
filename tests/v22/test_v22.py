from datetime import datetime, timezone, timedelta
from pathlib import Path
import tempfile
from ml.app.v22.providers import normalize_odds_api, OddsAPIProvider, ProviderError
from ml.app.v22.replay import ReplayEngine
from ml.app.v22.dataset import ResearchDataset
from ml.app.v22.position import assess_position, reversal_candidate
from ml.app.v21.realtime import FeedHealth, FeedStatus

def test_normalize_odds_api():
    rows=normalize_odds_api([{'id':'e1','sport_key':'soccer_test','home_team':'A','away_team':'B','bookmakers':[{'key':'x','markets':[{'key':'h2h','last_update':'2026-08-19T10:00:00Z','outcomes':[{'name':'A','price':2.0}]}]}]}], datetime(2026,8,19,10,1,tzinfo=timezone.utc))
    assert len(rows)==1 and rows[0]['odds']==2.0 and rows[0]['event_id']=='e1'

def test_provider_missing_credentials():
    p=OddsAPIProvider(api_key='')
    try:p.fetch_events_odds();assert False
    except ProviderError as e:assert 'CREDENTIALS_UNAVAILABLE' in str(e)

def test_replay_and_dataset():
    r=ReplayEngine();r.add('e1',{'minute':1},'2026-08-19T10:00:00Z',0);r.add('e1',{'minute':2},'2026-08-19T10:01:00Z',1)
    assert len(r.export())==2 and r.export()[1]['sequence']==1
    with tempfile.TemporaryDirectory() as d:
        ds=ResearchDataset(Path(d)/'d.jsonl'); row=ds.append({'event_id':'e1','decision':'NO BET'}); assert row['row_hash'] and ds.stats()['rows']==1

def test_position_actions():
    assert assess_position(entry_odds=2,current_odds=2.2,fair_probability=.55,remaining_minutes=20)['action']=='HOLD'
    assert assess_position(entry_odds=2,current_odds=1.5,fair_probability=.4,remaining_minutes=20)['action']=='EXIT'
    assert reversal_candidate(opposite_odds=2,opposite_probability=.55,remaining_minutes=30)['decision']=='NEW OPPORTUNITY'

def test_feed_health_states():
    h=FeedHealth('x',max_age_seconds=20,delayed_after_seconds=5)
    now=datetime.now(timezone.utc)
    assert h.observe(now-timedelta(seconds=2),now)==FeedStatus.ONLINE
    assert h.observe(now-timedelta(seconds=8),now)==FeedStatus.DELAYED
    assert h.observe(now-timedelta(seconds=30),now)==FeedStatus.STALE
    assert h.fail()==FeedStatus.OFFLINE
