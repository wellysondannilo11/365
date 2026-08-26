from __future__ import annotations
from fastapi import APIRouter,HTTPException
import os
from .session import V25Session
from .dataset import V25Dataset
from .analytics import summary
from .live import LiveStateEngine
from .replay import replay_decision
from .notifications import FakeNotificationProvider,format_decision
from .persistence import PostgreSQLV25Store,RedisV25Store

router=APIRouter(prefix="/v25",tags=["v25"])
pg=PostgreSQLV25Store(); pg.connect(); pg.ensure_schema()
dataset=V25Dataset(os.getenv("V25_DATASET_PATH","data/research/robo_bet_dataset_v25.jsonl"),persistence=pg);session=V25Session(dataset=dataset);live=LiveStateEngine(float(os.getenv("LIVE_MAX_AGE_SECONDS","20")));redis_store=RedisV25Store()

@router.get('/status')
def status():
    from .cards import CARD_MARKETS
    return {"version":"25.0.0","real_money_execution":False,"session_id":session.session_id,"feed":{"provider":session.provider.name,"configured":session.provider.configured,"status":session.health.status.value},"dataset":dataset.stats(),"card_markets":{"supported":sorted(CARD_MARKETS),"real_data_status":"NOT_DETERMINED"},"kill_switch":{"enabled":session.kill,"reason":session.kill_reason}}
@router.get('/infra/health')
def infra_health():
    return {'postgres':pg.health(),'redis':redis_store.health(),'dataset_primary':'POSTGRESQL' if pg.available else 'JSONL_FALLBACK'}

@router.get('/dataset')
def ds(limit:int=500):
 r=dataset.rows();return {"stats":dataset.stats(),"rows":r[-max(1,min(limit,5000)):],"paper":dataset.performance('PAPER'),"shadow":dataset.performance('SHADOW')}
@router.get('/analytics')
def analytics():return summary(dataset)

@router.get('/observability')
def observability():return session.observability.snapshot()
@router.post('/export/xlsx')
def export():return {"path":dataset.export_xlsx()}
@router.get('/hash-chain')
def hash_chain():return dataset.verify()
@router.post('/kill-switch')
def kill(enabled:bool=True,reason:str='MANUAL'):
 session.kill=enabled;session.kill_reason=reason if enabled else None;return {"enabled":session.kill,"reason":session.kill_reason}
@router.post('/feed/poll')
def poll():
 try:return session.poll()
 except RuntimeError as e:raise HTTPException(503,f'BLOCKED_EXTERNAL_DEPENDENCY:{e}')
 except Exception as e:raise HTTPException(502,f'FEED_PROVIDER_ERROR:{type(e).__name__}')
@router.post('/session/start')
def session_start(mode:str='SHADOW'):
    mode=mode.upper()
    if mode not in {'PAPER','SHADOW'}: raise HTTPException(422,'MODE_MUST_BE_PAPER_OR_SHADOW')
    session.kill=False; session.kill_reason=None
    return {'session_id':session.session_id,'mode':mode,'status':'READY','kill_switch':session.kill}

@router.post('/session/stop')
def session_stop(reason:str='MANUAL'):
    session.kill=True; session.kill_reason=reason; return {'session_id':session.session_id,'status':'STOPPED','reason':reason}

@router.get('/session/status')
def session_status():
    return {'session_id':session.session_id,'kill_switch':session.kill,'reason':session.kill_reason,'provider':session.provider.name,'feed_status':session.health.status.value}

@router.post('/session/scan')
def scan(mode:str='SHADOW'):
 try:return session.scan(session.poll(),mode)
 except RuntimeError as e:raise HTTPException(503,f'BLOCKED_EXTERNAL_DEPENDENCY:{e}')
@router.post('/market/analyze')
def market_analyze(payload:dict):
 from .cards import analyze_cards, CARD_MARKETS
 from ..v19.pricing import poisson_scoreline_distribution
 rows=payload.get('rows',[])
 football=[r for r in rows if str(r.get('market','')).upper() not in CARD_MARKETS]
 card_rows=[r for r in rows if str(r.get('market','')).upper() in CARD_MARKETS]
 d=payload.get('distribution')
 if d and isinstance(d,dict): d=poisson_scoreline_distribution(float(d['home_lambda']),float(d['away_lambda']),int(d.get('max_goals',10)))
 ranked=session.engine.analyze(football,d); selected=session.engine.select(football,d,1)[1]
 cards=analyze_cards({**payload.get('card_context',{}),'markets':card_rows}) if card_rows else {'results':[]}
 return {"ranked":ranked,"selected":selected,"cards":cards}
@router.post('/notification/test')
def notification_test(payload:dict):
    fake=FakeNotificationProvider();row=payload.get('row',payload);ok=fake.send(format_decision(row),'test');return {'sent':ok,'messages':fake.messages}

@router.post('/watchlist')
def watchlist_add(payload:dict):
    w=session.watchlist.add(payload['event_id'],payload['market'],payload['selection'],payload.get('line'),float(payload['current_odds']),float(payload['target_odds']),payload.get('fair_odds'));return w.__dict__
@router.get('/watchlist')
def watchlist_get():return {'items':session.watchlist.all()}

@router.post('/live/reprice')
def live_reprice(payload:dict):return session.live_reprice(payload['event_id'],payload['minute'],payload['home_goals'],payload['away_goals'],payload['home_xg'],payload['away_xg'],payload.get('markets',[]))
@router.post('/live/snapshot')
def live_snapshot(payload:dict):return live.ingest(payload)
@router.get('/live/{event_id}')
def live_history(event_id:str):return {"event_id":event_id,"snapshots":live.snapshots(event_id)}
@router.post('/position/reassess')
def position_reassess(payload:dict):return session.manage_position(payload['position'],float(payload['current_odds']),float(payload['fair_probability'])).__dict__
@router.post('/position/settle')
def position_settle(payload:dict):
    try:return session.settle_position(payload['position_id'],payload['result'],float(payload['closing_odds']),float(payload['pnl_units']),payload.get('clv'))
    except KeyError as e:raise HTTPException(404,str(e))

@router.post('/position/reversal')
def position_reversal(payload:dict):return session.reversal(float(payload['current_odds']),float(payload['current_probability'])).__dict__
@router.post('/replay')
def replay(payload:dict):return replay_decision(payload.get('expected',{}),payload.get('actual',{}))

@router.post('/cards/analyze')
def cards_analyze(payload:dict):
    from .cards import analyze_cards
    return analyze_cards(payload)

@router.post('/cards/live')
def cards_live(payload:dict):
    from .cards import analyze_cards
    # LIVE payload must contain only information known at decision_time. The
    # endpoint rejects explicit future timestamps rather than attempting to fix them.
    from datetime import datetime, timezone
    decision=payload.get('decision_time')
    if decision:
        dt=datetime.fromisoformat(str(decision).replace('Z','+00:00'))
        if dt.tzinfo is None or dt > datetime.now(timezone.utc):
            raise HTTPException(422,'INVALID_DECISION_TIME')
    return analyze_cards(payload)

@router.post('/cards/referee')
def cards_referee(payload:dict):
    from .cards import _feature
    return _feature(payload.get('cards_per_match'),payload.get('sample_size',0),payload.get('source'),payload.get('source_timestamp'),payload.get('captured_at'),payload.get('quality')).to_dict()

@router.post('/cards/markets')
def cards_markets(payload:dict):
    from .cards import CARD_MARKETS
    rows=[]
    for r in payload.get('rows',[]):
        if str(r.get('market','')).upper() in CARD_MARKETS: rows.append(r)
    return {'supported_markets':sorted(CARD_MARKETS),'rows':rows}
