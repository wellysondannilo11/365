from datetime import datetime,timezone,timedelta
from pathlib import Path
import json
from app.v25.settlement import asian_settlement,total_settlement,settlement_result
from app.v25.market_expression import MarketExpressionEngine
from app.v25.price_discovery import PriceDiscovery
from app.v25.policy import EntryPolicy
from app.v25.dataset import V25Dataset
from app.v25.position import reassess,reversal
from app.v25.live import LiveStateEngine
from app.v25.replay import replay_decision
from app.v19.pricing import poisson_scoreline_distribution

def rows(event='e1'):
    now=datetime.now(timezone.utc).isoformat()
    return [
      {'event_id':event,'market':'h2h','selection':'LDU','bookmaker':'b1','odds':1.57,'source_timestamp':now,'captured_at':now},
      {'event_id':event,'market':'h2h','selection':'Draw','bookmaker':'b1','odds':3.75,'source_timestamp':now,'captured_at':now},
      {'event_id':event,'market':'h2h','selection':'Mirassol','bookmaker':'b1','odds':6.50,'source_timestamp':now,'captured_at':now},
      {'event_id':event,'market':'h2h','selection':'LDU','bookmaker':'b2','odds':1.60,'source_timestamp':now,'captured_at':now},
      {'event_id':event,'market':'h2h','selection':'Draw','bookmaker':'b2','odds':3.60,'source_timestamp':now,'captured_at':now},
      {'event_id':event,'market':'h2h','selection':'Mirassol','bookmaker':'b2','odds':6.20,'source_timestamp':now,'captured_at':now},
    ]

def test_quarter_line_settlement():
    assert asian_settlement(1,0,0.25,'HOME')=='WIN'
    assert asian_settlement(0,0,0.25,'HOME')=='HALF_WIN'
    assert asian_settlement(0,1,0.25,'HOME')=='LOSS'
    assert asian_settlement(0,0,-0.25,'HOME')=='HALF_LOSS'
    assert asian_settlement(1,1,-0.25,'HOME')=='HALF_LOSS'

def test_quarter_total_settlement():
    assert total_settlement(2,0,2.25,'OVER')=='HALF_LOSS'
    assert total_settlement(3,0,2.25,'OVER')=='WIN'
    assert total_settlement(2,0,2.25,'UNDER')=='HALF_WIN'

def test_expression_engine_compares_all_markets_and_selects_one():
    d=poisson_scoreline_distribution(1.8,.7)
    r=rows(); r += [
      {'event_id':'e1','market':'spreads','selection':'LDU','line':-0.5,'bookmaker':'b1','odds':1.85},
      {'event_id':'e1','market':'spreads','selection':'Mirassol','line':0.5,'bookmaker':'b1','odds':1.95},
    ]
    for x in r:
        x.setdefault('source_timestamp',datetime.now(timezone.utc).isoformat());x.setdefault('captured_at',x['source_timestamp'])
    ranked,selected=MarketExpressionEngine(min_edge=.01,min_ev=.01).select(r,d,1)
    assert ranked and len(selected)<=1

def test_ludu_scenarios():
    eng=MarketExpressionEngine(min_edge=.01,min_ev=.01)
    r=rows();d=poisson_scoreline_distribution(2.2,.5)
    ranked,selected=eng.select(r,d,1)
    assert selected or any(x['decision']=='NO BET' for x in ranked)

def test_odd_floor_and_exception_band():
    p=EntryPolicy()
    assert p.check(1.49,.30,.30,.02)=='ODDS_BELOW_MINIMUM'
    assert p.check(1.55,.06,.06,.02)=='ODDS_IN_EXCEPTION_BAND'
    assert p.check(1.55,.12,.12,.02) is None
    assert p.check(1.70,.06,.06,.02) is None

def test_price_discovery():
    pd=PriceDiscovery();now=datetime.now(timezone.utc)
    r={'event_id':'e','bookmaker':'b','market':'h2h','selection':'A','line':None,'odds':2.0,'source_timestamp':now.isoformat()};a=pd.observe(r);r['odds']=2.2;r['source_timestamp']=(now+timedelta(seconds=10)).isoformat();b=pd.observe(r)
    assert a['opening_price']==2.0 and b['current_price']==2.2 and b['movement']==.2

def test_reversal_is_independent():
    assert reversal(3.0,.40,.05).action=='REVERSE'
    assert reversal(3.0,.20,.05).action=='REASSESS'

def test_position_management():
    assert reassess(2.3,2.5,.45).action=='HOLD'
    assert reassess(2.3,2.4,.45).action=='REDUCE'
    assert reassess(2.3,1.2,.45).action=='EXIT'

def test_live_reprice_changes_with_state():
    eng=MarketExpressionEngine(min_edge=.01,min_ev=.01)
    markets=[{'event_id':'e','market':'h2h','selection':'Home','bookmaker':'b1','odds':2.0},{'event_id':'e','market':'h2h','selection':'Draw','bookmaker':'b1','odds':3.5},{'event_id':'e','market':'h2h','selection':'Away','bookmaker':'b1','odds':3.8}]
    d1=poisson_scoreline_distribution(2.0,.5);d2=poisson_scoreline_distribution(.5,2.0)
    a=eng.select(markets,d1,1)[0];b=eng.select(markets,d2,1)[0]
    assert a[0]['probability']!=b[0]['probability'] or a[0]['decision']!=b[0]['decision']

def test_live_quality_blocks_stale_and_missing():
    e=LiveStateEngine(20);now=datetime.now(timezone.utc);p={'event_id':'e','captured_at':now.isoformat(),'minute':60,'home_goals':1,'away_goals':0}
    assert e.ingest(p)['status']=='BLOCK';p['source_timestamp']=(now-timedelta(seconds=60)).isoformat();assert e.ingest(p)['status']=='BLOCK'

def test_dataset_hash_tamper(tmp_path):
    d=V25Dataset(tmp_path/'x.jsonl');d.append({'event_id':'e','snapshot_id':'s','mode':'SHADOW','decision':'NO BET'});d.append({'event_id':'e','snapshot_id':'s2','mode':'SHADOW','decision':'NO BET'});assert d.verify()['valid']
    lines=(tmp_path/'x.jsonl').read_text().splitlines();x=json.loads(lines[0]);x['decision']='BET';(tmp_path/'x.jsonl').write_text(json.dumps(x)+'\n'+lines[1]+'\n');assert not d.verify()['valid']

def test_real_money_forbidden(tmp_path):
    d=V25Dataset(tmp_path/'x.jsonl')
    try:d.append({'mode':'LIVE','event_id':'e'})
    except ValueError as e:assert 'REAL_MONEY' in str(e)
    else:raise AssertionError

def test_replay():
    x={'decision':'NO BET','event_id':'e','edge':0};assert replay_decision(x,dict(x))['match']

def test_settlement_registry_result():
    assert settlement_result(market='ASIAN_HANDICAP',selection='Home',line=-0.5,home_goals=1,away_goals=0)=='WIN'
    assert settlement_result(market='TOTAL',selection='OVER',line=2.25,home_goals=2,away_goals=0)=='HALF_LOSS'

def test_price_discovery_aggregate():
    from app.v25.price_discovery import PriceDiscovery
    p=PriceDiscovery();rows=[{'event_id':'e','bookmaker':'b1','market':'h2h','selection':'A','odds':2.0},{'event_id':'e','bookmaker':'b2','market':'h2h','selection':'A','odds':2.2}]
    a=p.aggregate(rows)[('e','h2h',None,'A')]
    assert a['bookmaker_count']==2 and a['best_price']==2.2 and a['divergence']==.2

def test_settle_paper_position(tmp_path):
    from app.v25.session import V25Session
    from app.v25.dataset import V25Dataset
    s=V25Session(dataset=V25Dataset(tmp_path/'d.jsonl'))
    s.positions['p']={'position_id':'p','entry_odds':2.0}
    out=s.settle_position('p','WIN',2.1,1.0,.05)
    assert out['position_state']=='SETTLED' and out['result']=='WIN'

def test_notification_idempotency():
    from app.v25.notifications import FakeNotificationProvider
    p=FakeNotificationProvider();assert p.send('x','1');assert p.send('x','1');assert len(p.messages)==1


def test_exception_odds_band_requires_strong_edge():
    eng=MarketExpressionEngine(min_edge=.01,min_ev=.01)
    d=poisson_scoreline_distribution(1.8,.7)
    row={'event_id':'e','market':'h2h','selection':'HOME','bookmaker':'b','odds':1.55}
    ranked,_=eng.select([row],d,1)
    assert ranked[0]['decision']=='NO BET' and ranked[0]['reason']=='ODDS_IN_EXCEPTION_BAND'

def test_live_reprice_respects_current_score():
    from app.v25.session import V25Session
    s=V25Session()
    markets=[{'event_id':'e','market':'h2h','selection':'HOME','home_team':'A','away_team':'B','bookmaker':'b','odds':1.8},
             {'event_id':'e','market':'h2h','selection':'AWAY','home_team':'A','away_team':'B','bookmaker':'b','odds':4.0},
             {'event_id':'e','market':'h2h','selection':'DRAW','home_team':'A','away_team':'B','bookmaker':'b','odds':3.5}]
    a=s.live_reprice('e',60,2,0,1.5,.4,markets)
    assert a['state']['home_goals']==2
    assert a['markets']

def test_frontend_infra_state_is_loaded_from_fourth_api_result():
    src=Path('frontend/src/main.jsx').read_text(encoding='utf-8')
    assert 'const [x,y,z,w]' in src
    assert 'setI(w)' in src


def test_duplicate_bookmakers_do_not_create_duplicate_selected_positions():
    eng=MarketExpressionEngine(min_edge=.01,min_ev=.01)
    d=poisson_scoreline_distribution(2.0,.5)
    rows=[
      {'event_id':'e','market':'h2h','selection':'HOME','bookmaker':'b1','odds':2.1},
      {'event_id':'e','market':'h2h','selection':'HOME','bookmaker':'b2','odds':2.0},
      {'event_id':'e','market':'h2h','selection':'AWAY','bookmaker':'b1','odds':5.0},
      {'event_id':'e','market':'h2h','selection':'AWAY','bookmaker':'b2','odds':4.8},
      {'event_id':'e','market':'h2h','selection':'DRAW','bookmaker':'b1','odds':3.8},
      {'event_id':'e','market':'h2h','selection':'DRAW','bookmaker':'b2','odds':3.6},
    ]
    ranked,selected=eng.select(rows,d,1)
    assert len(selected)==1
    assert sum(x['decision']=='BET' for x in ranked)==1

def test_wait_for_price_exposes_target_without_betting():
    eng=MarketExpressionEngine(min_edge=.05,min_ev=.05)
    row={'event_id':'e','market':'h2h','selection':'HOME','bookmaker':'b','odds':1.70}
    x=eng.analyze([row],poisson_scoreline_distribution(.9,.9))[0]
    assert x['decision']=='WATCH'
    assert x['reason']=='WAIT_FOR_PRICE'
    assert x['target_odds'] and x['target_odds']>x['odds']


def test_dataset_deduplicates_same_observation(tmp_path):
    d=V25Dataset(tmp_path/'x.jsonl')
    a=d.append({'event_id':'e','snapshot_id':'s','mode':'SHADOW','decision':'NO BET','market':'H2H','selection':'A','odds':2.0})
    b=d.append({'event_id':'e','snapshot_id':'s','mode':'SHADOW','decision':'NO BET','market':'H2H','selection':'A','odds':2.0})
    assert a['observation_id']==b['observation_id']
    assert len(d.rows())==1


def test_portfolio_limits_block_excess_exposure():
    from app.v20.risk import PortfolioRisk,PortfolioLimits
    from datetime import datetime,timezone
    r=PortfolioRisk(PortfolioLimits(max_per_event=1,max_per_day=3,max_simultaneous=1))
    now=datetime.now(timezone.utc)
    assert r.allowed(now,'e',1)
    r.open('e',1)
    assert not r.allowed(now,'e',.1)


def test_session_stop_start_api_contract():
    from fastapi.testclient import TestClient
    from app.api import app
    c=TestClient(app)
    assert c.post('/v25/session/start',params={'mode':'SHADOW'}).status_code==200
    assert c.get('/v25/session/status').status_code==200
    assert c.post('/v25/session/stop',params={'reason':'TEST'}).status_code==200

def test_portfolio_enforces_daily_tip_limit():
    from app.v20.risk import PortfolioRisk, PortfolioLimits
    from datetime import datetime, timezone
    r=PortfolioRisk(PortfolioLimits(max_per_event=10,max_per_day=2,max_simultaneous=10))
    now=datetime.now(timezone.utc)
    assert r.allowed(now,'e1',1)
    r.open('e1',1)
    assert r.allowed(now,'e2',1)
    r.open('e2',1)
    assert not r.allowed(now,'e3',1)


def test_session_start_rearms_after_stop():
    from fastapi.testclient import TestClient
    from app.api import app
    c=TestClient(app)
    c.post('/v25/session/stop',params={'reason':'TEST'})
    r=c.post('/v25/session/start',params={'mode':'SHADOW'})
    assert r.status_code==200 and r.json()['kill_switch'] is False


def test_snapshot_store_keeps_raw_observations_and_deduplicates(tmp_path):
    from app.v25.persistence import V25SnapshotStore
    p=V25SnapshotStore(None,tmp_path/'snapshots.jsonl')
    row={'snapshot_id':'s1','event_id':'e1','source':'fake','market':'h2h','selection':'A','odds':2.0,'source_timestamp':datetime.now(timezone.utc).isoformat(),'captured_at':datetime.now(timezone.utc).isoformat(),'received_at':datetime.now(timezone.utc).isoformat(),'mode':'PRE','raw_hash':'h'}
    assert p.append(row)['snapshot_id']=='s1'
    assert p.append(row)['snapshot_id']=='s1'
    assert len(p.rows())==1


def test_session_restores_open_position_and_daily_risk(tmp_path):
    from app.v25.session import V25Session
    from app.v25.dataset import V25Dataset
    d=V25Dataset(tmp_path/'d.jsonl')
    d.append({'event_id':'e1','snapshot_id':'s1','mode':'SHADOW','decision':'BET','market':'H2H','selection':'A','odds':2.0,'stake_units':1.0,'position_id':'p1','created_at':datetime.now(timezone.utc).isoformat()})
    s=V25Session(dataset=d)
    assert 'p1' in s.positions and s.portfolio.state.open_exposure==1.0 and s.portfolio.state.tips_taken==1


def test_future_source_timestamp_is_pit_rejected(tmp_path):
    from app.v25.session import V25Session
    from app.v25.dataset import V25Dataset
    from app.v25.persistence import V25SnapshotStore
    class P:
        name='fake';configured=True
        def fetch_events_odds(self):
            future=(datetime.now(timezone.utc)+timedelta(seconds=60)).isoformat()
            return ([{'id':'e','home_team':'A','away_team':'B','sport_key':'soccer_test','bookmakers':[{'key':'b','markets':[{'key':'h2h','last_update':future,'outcomes':[{'name':'A','price':2.0}]}]}]}],{})
        def fetch_scores(self,days_from=1): return []
    d=V25Dataset(tmp_path/'d.jsonl');s=V25Session(provider=P(),dataset=d,snapshot_store=V25SnapshotStore(None,tmp_path/'s.jsonl'))
    f=s.poll(); assert f['odds']==[] and s.observability.snapshot()['PIT_rejections']==1


def test_telegram_notification_idempotency_survives_restart(tmp_path,monkeypatch):
    from app.v25.notifications import TelegramNotificationProvider
    monkeypatch.setenv('TELEGRAM_BOT_TOKEN','token');monkeypatch.setenv('TELEGRAM_CHAT_ID','chat');monkeypatch.setenv('TELEGRAM_SENT_IDS_PATH',str(tmp_path/'ids'))
    class R:
        def raise_for_status(self): pass
    calls=[]
    import app.v25.notifications as n
    monkeypatch.setattr(n.requests,'post',lambda *a,**k: calls.append(1) or R())
    p=TelegramNotificationProvider(); assert p.send('x','id1'); assert p.send('x','id1')
    p2=TelegramNotificationProvider(); assert p2.send('x','id1'); assert len(calls)==1


def test_runner_blocks_without_primary_infrastructure(tmp_path, monkeypatch):
    # Static/behavioral contract: the operational runner must fail closed when
    # either persistent infrastructure dependency is unavailable. This test
    # exercises the stores without requiring a live service.
    from app.v25.persistence import PostgreSQLV25Store, RedisV25Store
    pg = PostgreSQLV25Store(url=None)
    redis = RedisV25Store(url=None)
    assert pg.connect() is False
    assert redis.connect() is False
    assert pg.health()["primary"] is False
    assert redis.health()["role"] == "CACHE/EPHEMERAL_ONLY"

