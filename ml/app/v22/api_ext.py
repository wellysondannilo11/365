from __future__ import annotations
import os
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from .providers import OddsAPIProvider
from .manager import FeedManagerV22
from .dataset import ResearchDataset
from .replay import ReplayEngine
from .position import assess_position,reversal_candidate
from .observability import metrics
from ..market import devig

router=APIRouter(prefix='/v22')
provider=OddsAPIProvider(); manager=FeedManagerV22(provider=provider); dataset=manager.dataset; replay=manager.replay

@router.get('/status')
def status(): return {'version':'22.0.0','mode':'PAPER/SHADOW','live_execution':False,'feed':manager.status(),'dataset':dataset.stats()}
@router.get('/metrics')
def metrics_endpoint(): return metrics.snapshot()
@router.get('/metrics/prometheus')
def prometheus(): return metrics.prometheus()
@router.get('/dataset')
def dataset_endpoint(): return {'stats':dataset.stats(),'rows':dataset.rows()[-500:]}
@router.get('/replay/{event_id}')
def replay_event(event_id): return {'event_id':event_id,'snapshots':[x for x in replay.export() if x['event_id']==event_id]}
@router.post('/feed/poll')
def feed_poll():
    if not provider.configured: raise HTTPException(503,'BLOCKED_EXTERNAL_DEPENDENCY:CREDENTIALS_UNAVAILABLE')
    try: return manager.poll()
    except Exception as e: raise HTTPException(502,f'FEED_PROVIDER_ERROR:{type(e).__name__}') from e
def _baseline_candidates(rows):
    groups={}
    for r in rows:
        if float(r.get('odds',0))<=1: continue
        key=(r.get('event_id'),r.get('market'),r.get('line'))
        groups.setdefault(key,[]).append(r)
    out=[]
    for key,grp in groups.items():
        probs=devig([float(x['odds']) for x in grp])
        for r,p in zip(grp,probs):
            x=dict(r); x['probability']=float(p); x['market_quality']=1.0; x['data_quality']=100; x['calibration']=1.0; x['uncertainty']=0.05; x['robustness']=1.0; x['model_agreement']=1.0; x['pit_ok']=True; x['sample_size']=0; x['model_type']='MARKET_ONLY_BASELINE'; out.append(x)
    return out

@router.post('/scan')
def scan(mode='SHADOW'):
    mode=str(mode).upper()
    if mode not in {'PAPER','SHADOW'}: raise HTTPException(422,'MODE_MUST_BE_PAPER_OR_SHADOW')
    if not provider.configured: raise HTTPException(503,'BLOCKED_EXTERNAL_DEPENDENCY:CREDENTIALS_UNAVAILABLE')
    try: feed=manager.poll()
    except Exception as e: raise HTTPException(502,f'FEED_PROVIDER_ERROR:{type(e).__name__}') from e
    now=datetime.now(timezone.utc)
    if feed['health'] != 'ONLINE': return {'feed_status':feed['health'],'decision':{'opportunities':[],'no_bet_count':0},'scientific_status':'NO_BET_FEED_NOT_HEALTHY'}
    candidates=_baseline_candidates(feed['odds'])
    result=v21_service.select(candidates,now,mode)
    seen=0
    for item in result['opportunities']:
        row={'event_id':item.get('event_id'),'decision':item.get('decision','NO BET'),'mode':mode,'decision_time':now.isoformat(),'result':None,'model_version':item.get('model_type','MARKET_ONLY_BASELINE'),'feature_version':'v23-feed','pricing_version':'market-devig','data_snapshot_id':item.get('data_snapshot_id'),'reason':item.get('no_bet_reason'),'fair_probability':item.get('probability'),'fair_odds':(1/float(item['probability']) if item.get('probability') else None), 'edge':item.get('edge'),'ev':item.get('ev'),**item}
        stored=dataset.append(row); manager.persistence.record_dataset(stored); manager.persistence.record_trace(item['trace']); seen+=1
    metrics.inc('robo_v23_decisions_total',seen); metrics.inc('robo_v23_no_bet_total',sum(x.get('decision')=='NO BET' for x in result['opportunities']))
    return {'feed_status':feed['health'],'model':'MARKET_ONLY_BASELINE','scientific_status':'BASELINE_ONLY_NOT_EDGE_EVIDENCE','decision':result,'dataset':dataset.stats()}

@router.post('/session/poll')
def session_poll(mode='SHADOW'):
    return scan(mode=mode)

@router.post('/position/assess')
def position_assess(payload:dict): return assess_position(entry_odds=float(payload['entry_odds']),current_odds=float(payload['current_odds']),fair_probability=float(payload['fair_probability']),remaining_minutes=int(payload.get('remaining_minutes',0)),uncertainty=float(payload.get('uncertainty',0)),exit_cost=float(payload.get('exit_cost',0)),min_edge=float(payload.get('min_edge',0.05)))
@router.post('/position/reverse')
def position_reverse(payload:dict): return reversal_candidate(opposite_odds=float(payload['opposite_odds']),opposite_probability=float(payload['opposite_probability']),min_edge=float(payload.get('min_edge',0.05)),remaining_minutes=int(payload.get('remaining_minutes',90)))
