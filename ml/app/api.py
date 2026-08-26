from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import JSONResponse
from datetime import datetime,timezone
import pandas as pd, json, os
from .schemas import OpportunityRequest,Settlement
from .config import settings
from .data_quality import score_snapshot
from .features import temperature,build_features
from .live import live_signal
from .risk import RiskEngine
from .selection import select
from .ledger import Ledger
from .consensus import consensus_snapshots
from .leakage import audit_point_in_time
from .uncertainty import ensemble_uncertainty
from .db import init_db
from .telegram import Telegram
from .market import implied,devig,fair_odds,edge,ev,overround
from .research.market import consensus as research_consensus
from .research.validation import nested_walk_forward
from .research.data_quality import report as dq_report
from .pit_store.pit import validate_frame,dataset_hash
from .research.calibration import calibration_report
from .backtest_engine import simulate
from .v19.engine import PricingEngine
from .v19.market_intelligence import normalize_market_rows, de_vig_market, consensus_probability, discover_dislocations
from .v19.paper import ImmutablePaperBet, ImmutablePaperLedger
from .v19.pricing import derived_market_probabilities, poisson_scoreline_distribution
from .v19.validation import validate_distribution
from .schemas import PricingRequest
from .v20.selection import Candidate
from .v20.service import DecisionServiceV20
from .v20.live_engine import LiveState
from .v21.service import DecisionServiceV21
from .v22.api_ext import router as v22_router
from .v24.api import router as v24_router
from .v25.api import router as v25_router

app=FastAPI(title='Robo da Bet Master Quant Research API',version='25.0.0')
ROBO_API_KEY=os.getenv('ROBO_API_KEY','').strip()

@app.middleware('http')
async def optional_api_key(request: Request, call_next):
    if ROBO_API_KEY and request.url.path != '/health':
        supplied=request.headers.get('X-API-Key','')
        if supplied != ROBO_API_KEY:
            return JSONResponse({'detail':'AUTHENTICATION_REQUIRED'},status_code=401)
    return await call_next(request)
risk=RiskEngine(settings.bankroll,settings.daily_stop,settings.loss_cooldown);ledger=Ledger();v19_paper=ImmutablePaperLedger();pricing_engine=PricingEngine();tg=Telegram(settings.telegram_token,settings.telegram_chat_id);v20_service=DecisionServiceV20(); v21_service=DecisionServiceV21()
try:init_db()
except Exception:pass



@app.post('/pricing')
def pricing(req: PricingRequest):
    if req.decision_time.tzinfo is None:
        raise HTTPException(422, 'DECISION_TIME_MUST_BE_TIMEZONE_AWARE')
    return pricing_engine.price(
        event_id=req.event_id,
        decision_time=req.decision_time,
        home_expected_goals=req.home_expected_goals,
        away_expected_goals=req.away_expected_goals,
        market_state=req.market_state,
        dixon_coles_rho=req.dixon_coles_rho,
        max_goals=req.max_goals,
    )

@app.post('/pricing/scoreline')
def pricing_scoreline(req: PricingRequest):
    if req.decision_time.tzinfo is None:
        raise HTTPException(422, 'DECISION_TIME_MUST_BE_TIMEZONE_AWARE')
    d = poisson_scoreline_distribution(req.home_expected_goals, req.away_expected_goals, req.max_goals, req.dixon_coles_rho)
    return {'event_id': req.event_id, 'decision_time': req.decision_time.isoformat(), 'distribution': [x.__dict__ for x in d], 'validation': validate_distribution([x.__dict__ for x in d])}

@app.post('/pricing/markets')
def pricing_markets(req: PricingRequest):
    d = poisson_scoreline_distribution(req.home_expected_goals, req.away_expected_goals, req.max_goals, req.dixon_coles_rho)
    return {'event_id': req.event_id, 'decision_time': req.decision_time.isoformat(), 'markets': [x.__dict__ for x in derived_market_probabilities(d)]}

@app.post('/market/normalize-v19')
def market_normalize_v19(payload: dict):
    d = normalize_market_rows(payload.get('rows', []), strict_pit=bool(payload.get('strict_pit', False)))
    return {'rows': d.to_dict(orient='records'), 'count': len(d)}

@app.post('/market/consensus-v19')
def market_consensus_v19(payload: dict):
    d = normalize_market_rows(payload.get('rows', []), strict_pit=bool(payload.get('strict_pit', False)))
    return {'consensus': consensus_probability(d).to_dict(orient='records')}

@app.post('/dislocations')
def market_dislocations_v19(payload: dict):
    return {'opportunities': discover_dislocations(payload.get('model_rows', []), payload.get('market_rows', []), strict_pit=bool(payload.get('strict_pit', False)), decision_time=payload.get('decision_time'))}

@app.post('/paper-bets/v19')
def paper_bet_v19(payload: dict):
    required = {'signal_id','event_id','decision_time','market','selection','bookmaker','entry_odds','model_probability','edge','ev','model_version','feature_version','dataset_fingerprint','source_quality'}
    missing = required - set(payload)
    if missing:
        raise HTTPException(422, f'MISSING_IMMUTABLE_PAPER_FIELDS:{sorted(missing)}')
    if payload.get('status', 'PAPER') not in {'PAPER', 'SHADOW'}:
        raise HTTPException(422, 'LIVE_EXECUTION_NOT_SUPPORTED')
    signal = ImmutablePaperBet(
        signal_id=str(payload['signal_id']), event_id=str(payload['event_id']), decision_time=str(payload['decision_time']),
        market=str(payload['market']), selection=str(payload['selection']), line=payload.get('line'), bookmaker=str(payload['bookmaker']),
        entry_odds=float(payload['entry_odds']), model_probability=float(payload['model_probability']),
        fair_odds=float(payload['fair_odds']) if payload.get('fair_odds') is not None else None,
        market_probability=float(payload['market_probability']) if payload.get('market_probability') is not None else None,
        edge=float(payload['edge']), ev=float(payload['ev']), model_version=str(payload['model_version']),
        feature_version=str(payload['feature_version']), calibration_version=payload.get('calibration_version'),
        dataset_fingerprint=str(payload['dataset_fingerprint']), source_quality=str(payload['source_quality']), status=str(payload.get('status', 'PAPER')),
    )
    return v19_paper.append(signal)

@app.get('/health')
def health():return {'status':'ok','version':'25.0.0','paper':settings.paper,'point_in_time':True,'historical_data':'NOT_AVAILABLE' if not os.getenv('HISTORICAL_DATA_PATH') else 'CONFIGURED'}
@app.get('/research/status')
def research_status():
 path=os.getenv('HISTORICAL_DATA_PATH'); return {'status':'RESEARCH','version':'19.0.0','holdout':'LOCKED_BY_CONTRACT','demo_data':True,'historical_data':'CONFIGURED' if path else 'NOT AVAILABLE','real_historical_backtest':False,'profitability':'NOT AVAILABLE','point_in_time':'STRICT_FEATURE_LEVEL'}
@app.get('/research/models')
def research_models():
 from pathlib import Path
 root=Path('artifacts/registry');return {'models':[json.loads(p.read_text()) for p in root.glob('*.json')] if root.exists() else []}
@app.get('/research/metrics')
def research_metrics(): return {'metrics':[],'status':'NOT_AVAILABLE_WITHOUT_REAL_HISTORICAL_DATA'}
@app.get('/research/holdout')
def research_holdout(): return {'state':'RESEARCH','holdout_locked':True,'final_evaluation':'NOT_AVAILABLE'}
@app.get('/drift')
def drift(): return {'feature_drift':'NOT_AVAILABLE','prediction_drift':'NOT_AVAILABLE','calibration_drift':'NOT_AVAILABLE','market_drift':'NOT_AVAILABLE'}
@app.get('/calibration')
def calibration_status(): return {'status':'IMPLEMENTED_NOT_VALIDATED','real_historical_data':False}
@app.get('/risk')
def risk_status():return risk.state.__dict__
@app.get('/bets')
def bets():return ledger.bets
@app.get('/decisions')
def decisions():return ledger.bets
@app.get('/performance')
def performance():
 rows=ledger.bets;settled=[b for b in rows if b.get('status') in ('WIN','LOSS','VOID')];pnl=sum(float(b.get('pnl',0)) for b in settled);by_market={};by_league={}
 for b in settled:
  by_market[b.get('market','UNKNOWN')]=by_market.get(b.get('market','UNKNOWN'),0)+float(b.get('pnl',0));by_league[b.get('league','UNKNOWN')]=by_league.get(b.get('league','UNKNOWN'),0)+float(b.get('pnl',0))
 return {'bets':len(rows),'settled':len(settled),'pnl':pnl,'by_market':by_market,'by_league':by_league,'status':'PAPER_ONLY'}
@app.post('/market/consensus')
def market_consensus(req:OpportunityRequest):return [r.__dict__ for r in consensus_snapshots(req.odds)]
@app.post('/market/consensus/v13')
def market_consensus_v13(rows:list[dict]):return [r.__dict__ for r in research_consensus(rows)]
@app.post('/leakage/audit')
def leakage_audit(rows:list[dict]):
 d=audit_point_in_time(pd.DataFrame(rows));return {'violations':d.to_dict(orient='records'),'count':len(d)}
@app.post('/research/point-in-time/validate')
def pit_validate(rows:list[dict]):
 try:d=validate_frame(pd.DataFrame(rows));return {'status':'PASS','rows':len(d),'dataset_hash':dataset_hash(d)}
 except Exception as e:raise HTTPException(422,str(e))
@app.post('/research/data-quality')
def data_quality(rows:list[dict]):return dq_report(pd.DataFrame(rows))
@app.post('/research/calibration')
def calibration(rows:list[dict],probability='probability',label='label'):
 d=pd.DataFrame(rows);return calibration_report(d[label].astype(int),d[probability].astype(float))
@app.post('/research/walk-forward')
def walk_forward(rows:list[dict],min_train:int=100,validation:int=30,test:int=30,holdout:float=.15):
 d=validate_frame(pd.DataFrame(rows));folds,research,hold=nested_walk_forward(d,min_train,validation,test,holdout=holdout);return {'folds':[f.__dict__ for f in folds],'research_rows':len(research),'final_holdout_rows':len(hold),'holdout_used':False}
@app.post('/research/backtest')
def backtest(rows:list[dict],probability='probability',odds='odds',result='result'):return simulate(pd.DataFrame(rows),probability,odds,result)
@app.post('/opportunity')
def opportunity(req:OpportunityRequest):
 m=req.match;decision_time=req.decision_time or m.decision_time;dq,errs=score_snapshot(m);out=[]
 if m.available_at>decision_time:raise HTTPException(422,'POINT_IN_TIME_VIOLATION')
 for o in req.odds:
  if o.event_id!=m.event_id or o.available_at>decision_time:continue
  key=f'{o.market}:{o.selection}';p=req.model_probabilities.get(key,req.model_probabilities.get(o.selection,req.pre_match_probabilities.get(key,0)))
  sig={'eligible':True,'temperature':temperature(m),'reason':'MODEL_INPUT'}
  if p<=0 and m.minute>0 and ('Over' in o.selection or 'Under' in o.selection):
   side='OVER' if 'Over' in o.selection else 'UNDER';line=float(''.join(c for c in o.selection if c.isdigit() or c=='.'));sig=live_signal(m,line,side,req.pre_match_probabilities.get(key));p=sig.get('probability',0)
  if p<=0:continue
  probs=req.model_probabilities.get(f'{key}:ensemble',p);uncertainty=abs(p-probs) if probs else 0
  decision=select(o.odds,p,dq,.85,uncertainty,sig.get('temperature',temperature(m)),risk,decision_time,m.minute>0,70)
  item={'event_id':m.event_id,'league':m.league,'market':o.market,'selection':o.selection,'bookmaker':o.bookmaker,'odds':o.odds,'p_sport':req.pre_match_probabilities.get(key),'p_market':None,'p_hybrid':p,'probability':p,'prediction_uncertainty':uncertainty,'fair_probability':p,'data_quality':dq,'temperature':temperature(m),'live':m.minute>0,**decision,'dq_errors':errs,'decision_time':decision_time.isoformat()}
  out.append(item)
  if decision['decision']=='BET':
   bet_id=f"{m.event_id}-{o.market}-{o.selection}-{int(decision_time.timestamp())}";item['id']=bet_id;ledger.add({'id':bet_id,**item,'status':'OPEN','pnl':0});risk.register_exposure(m.event_id,item['stake'],f'{m.event_id}:{o.market}')
   if settings.paper:tg.send(f"ROBO DA BET V13\n{m.home} x {m.away}\n{o.market} {o.selection}\nOdd {o.odds:.2f} Fair {item['fair_odds']:.2f}\nProb {p:.1%} Edge {item['edge']:.1%} EV {item['ev']:.1%}\nStake {item['stake']}u Score {item['score']}")
 return {'opportunities':sorted(out,key=lambda x:x['score'],reverse=True),'risk':risk.state.__dict__}
@app.post('/settle')
def settle(s:Settlement):
 b=ledger.settle(s.bet_id,s.result,s.closing_odds);risk.settle(b['pnl'],datetime.now(timezone.utc));return {'bet':b,'risk':risk.state.__dict__}

@app.get('/research/experiments')
def research_experiments():
 from pathlib import Path
 root=Path('artifacts/experiments'); items=[]
 if root.exists():
  for p in root.glob('*.json'):
   try: items.append(json.loads(p.read_text()))
   except Exception: continue
 return {'experiments':items}

@app.get('/research/validation')
def research_validation():
 return {'status':'NOT VALIDATED','reason':'REAL_HISTORICAL_DATA_NOT_AVAILABLE_IN_RUNTIME'}

@app.get('/research/data-quality/status')
def research_data_quality_status():
 return {'status':'NOT AVAILABLE','reason':'NO_REAL_DATASET_REGISTERED'}

# V14 DATA ACQUISITION & REAL VALIDATION endpoints
@app.get('/research/datasets')
def research_datasets():
 from pathlib import Path
 root=Path('artifacts/datasets'); items=[]
 for p in root.glob('*.json') if root.exists() else []:
  try: items.append(json.loads(p.read_text()))
  except Exception: pass
 return {'datasets':items,'historical_data':'NOT_AVAILABLE' if not os.getenv('HISTORICAL_DATA_PATH') else 'CONFIGURED'}

@app.get('/research/ingestion/status')
def ingestion_status():
 path=os.getenv('HISTORICAL_DATA_PATH'); return {'configured':bool(path),'path':path,'status':'READY_FOR_EXTERNAL_DATA' if not path else 'CONFIGURED','supported_formats':['csv','json','parquet']}

@app.post('/research/ingestion/validate')
def ingestion_validate(payload:dict):
 from .ingestion.schema import validate_schema
 from .ingestion.schema import canonicalize
 d=pd.DataFrame(payload.get('rows',[])); validate_schema(d,payload.get('dataset_type','matches')); d=canonicalize(d)
 return {'status':'PASS','rows':len(d),'columns':list(d.columns)}

@app.post('/research/dataset/build')
def dataset_build(payload:dict):
 from .research.datasets import build_point_in_time_dataset
 rows=payload.get('rows',[]); df,manifest=build_point_in_time_dataset(pd.DataFrame(rows),payload.get('dataset_type','matches'),payload.get('version','v14'),payload.get('feature_version','v14'))
 return {'status':'PASS','manifest':manifest.__dict__}

@app.post('/research/odds/snapshot')
def odds_snapshot(payload:dict):
 from .research.odds import snapshot_at_or_before
 d=snapshot_at_or_before(pd.DataFrame(payload.get('rows',[])),payload['event_id'],payload['decision_time'],payload.get('market'))
 return {'rows':d.to_dict(orient='records'),'count':len(d),'status':'PASS'}

@app.post('/research/quality/v14')
def quality_v14(rows:list[dict]):
 from .research.data_quality_v14 import report_v14
 return report_v14(pd.DataFrame(rows))

@app.post('/research/backtest/validate')
def backtest_validate(rows:list[dict],probability='probability',odds='odds',result='result'):
 d=pd.DataFrame(rows)
 from .pit_store.pit import validate_frame
 validate_frame(d)
 return simulate(d,probability,odds,result)


# ================= V20 SELECTIVE DECISION ENGINE =================
@app.get('/v20/status')
def v20_status():
    return {'version':'20.0.0','mode':'PAPER/SHADOW','live_execution':False,'min_odds':settings.min_odds,'preferred_odds':settings.preferred_odds,'unit_brl':settings.unit_brl,'max_tips_per_event':settings.max_tips_per_event,'max_tips_per_day':settings.max_tips_per_day,'max_simultaneous_positions':settings.max_simultaneous_positions,'telegram_enabled':getattr(v20_service.notify,'enabled',False)}

@app.post('/v20/select')
def v20_select(payload:dict):
    rows=payload.get('candidates',[])
    candidates=[Candidate(event_id=str(r['event_id']),market=str(r['market']),selection=str(r['selection']),odds=float(r['odds']),probability=float(r['probability']),data_quality=float(r.get('data_quality',100)),calibration=float(r.get('calibration',1)),uncertainty=float(r.get('uncertainty',0)),liquidity=float(r.get('liquidity',1)),market_quality=float(r.get('market_quality',1)),robustness=float(r.get('robustness',1)),model_agreement=float(r.get('model_agreement',1)),live=bool(r.get('live',False)),stale=bool(r.get('stale',False)),pit_ok=bool(r.get('pit_ok',True)),correlation_penalty=float(r.get('correlation_penalty',0)),sample_size=int(r.get('sample_size',0))) for r in rows]
    ranked=v20_service.rank(candidates,min_odds=settings.min_odds,preferred_odds=settings.preferred_odds,min_edge=settings.min_edge,min_ev=settings.min_ev,min_data_quality=settings.min_dq,max_uncertainty=0.12,min_market_quality=0.40)
    approved=[];seen_events=set();pending_exposure=0.0
    for item in ranked:
        if item['decision']!='BET': continue
        if item['event_id'] in seen_events: item['decision']='NO BET';item['no_bet_reason']='MAX_TIPS_PER_EVENT';item['stake']=0;continue
        if len(approved)>=settings.max_tips_per_day: item['decision']='NO BET';item['no_bet_reason']='TOP_N_SELECTIVITY';item['stake']=0;continue
        if pending_exposure+item['stake']>settings.max_simultaneous_positions: item['decision']='NO BET';item['no_bet_reason']='RISK_LIMIT';item['stake']=0;continue
        if not v20_service.risk.allowed(datetime.now(timezone.utc),item['event_id'],item['stake']): item['decision']='NO BET';item['no_bet_reason']='RISK_LIMIT';item['stake']=0;continue
        approved.append(item);seen_events.add(item['event_id']);pending_exposure+=item['stake']
    approved_ids={(x['event_id'],x['market'],x['selection']) for x in approved}
    for item in ranked:
        if item['decision']=='BET' and (item['event_id'],item['market'],item['selection']) not in approved_ids:
            item['decision']='NO BET';item['stake']=0;item['no_bet_reason']='TOP_N_SELECTIVITY'
    return {'opportunities':ranked,'approved':approved,'no_bet_count':sum(x['decision']=='NO BET' for x in ranked),'philosophy':'ANALYZE_MANY_BET_FEW'}

@app.post('/v20/paper/record')
def v20_paper_record(payload:dict):
    if payload.get('decision')!='BET': return {'status':'NO BET','record':None}
    return {'status':'RECORDED','record':v20_service.record(payload,league=str(payload.get('league','')),country=str(payload.get('country','')),season=str(payload.get('season','')),feature_snapshot=str(payload.get('feature_snapshot','')),pit_status=str(payload.get('pit_status','PASS')),entry_minute=payload.get('entry_minute'),scoreline=payload.get('scoreline'))}

@app.post('/v20/live/reprice')
def v20_live_reprice(payload:dict):
    required={'event_id','decision_time','minute','home_goals','away_goals','home_xg','away_xg','home_lambda','away_lambda','markets'}
    if not required.issubset(payload): raise HTTPException(422,f'MISSING_LIVE_FIELDS:{sorted(required-set(payload))}')
    st=LiveState(event_id=str(payload['event_id']),decision_time=datetime.fromisoformat(str(payload['decision_time']).replace('Z','+00:00')),minute=int(payload['minute']),home_goals=int(payload['home_goals']),away_goals=int(payload['away_goals']),home_xg=float(payload['home_xg']),away_xg=float(payload['away_xg']),shots=int(payload.get('shots',0)),shots_on_target=int(payload.get('shots_on_target',0)),corners=int(payload.get('corners',0)),red_cards_home=int(payload.get('red_cards_home',0)),red_cards_away=int(payload.get('red_cards_away',0)),possession_home=payload.get('possession_home'),possession_away=payload.get('possession_away'))
    if st.decision_time.tzinfo is None: raise HTTPException(422,'DECISION_TIME_MUST_BE_TIMEZONE_AWARE')
    for m in payload['markets']:
        if m.get('available_at') and datetime.fromisoformat(str(m['available_at']).replace('Z','+00:00'))>st.decision_time: raise HTTPException(422,'POINT_IN_TIME_VIOLATION')
    return v20_service.live.reprice(st,float(payload['home_lambda']),float(payload['away_lambda']),payload['markets'])

@app.get('/v20/ledger')
def v20_ledger(): return {'rows':v20_service.ledger.rows(),'fingerprint':v20_service.ledger.fingerprint()}

@app.post('/v20/ledger/settle')
def v20_ledger_settle(payload:dict): return v20_service.ledger.settle(str(payload['record_id']),str(payload['result']),payload.get('closing_odds'),payload.get('exit_reason'))

@app.post('/v20/ledger/export')
def v20_ledger_export(): return {'status':'PASS','path':v20_service.ledger.export_xlsx()}

@app.get('/v20/performance')
def v20_performance(): return v20_service.summary()

@app.get('/v20/notifications')
def v20_notifications(): return {'telegram_enabled':getattr(v20_service.notify,'enabled',False),'status':'ENABLED' if getattr(v20_service.notify,'enabled',False) else 'NOT_CONFIGURED'}

@app.post('/v20/position/assess')
def v20_position_assess(payload:dict):
    from .v20.position import assess_position
    return assess_position(entry_odds=float(payload['entry_odds']),current_odds=float(payload['current_odds']),fair_probability=float(payload['fair_probability']),stake_units=float(payload.get('stake_units',0)),remaining_minutes=int(payload.get('remaining_minutes',0)),exit_cost=float(payload.get('exit_cost',0)),min_edge=float(payload.get('min_edge',settings.min_edge)))

@app.post('/v20/position/reverse')
def v20_position_reverse(payload:dict):
    from .v20.position import reverse_candidate
    return reverse_candidate(opposite_odds=float(payload['opposite_odds']),opposite_probability=float(payload['opposite_probability']),min_edge=float(payload.get('min_edge',settings.min_edge)))


# ================= V21 REAL-TIME PAPER/SHADOW ENGINE =================
@app.get('/v21/status')
def v21_status():
    return {'version':'21.0.0','mode':'PAPER/SHADOW','live_execution':False,'kill_switch':v21_service.risk.state.kill_switch,'telegram_enabled':getattr(v21_service.notify,'enabled',False),'ledger_chain':v21_service.ledger.verify_chain(),'performance':v21_service.ledger.performance()}

@app.post('/v21/select')
def v21_select(payload:dict):
    if 'decision_time' not in payload: raise HTTPException(422,'DECISION_TIME_REQUIRED')
    try: dt=datetime.fromisoformat(str(payload['decision_time']).replace('Z','+00:00'))
    except Exception as exc: raise HTTPException(422,'INVALID_DECISION_TIME') from exc
    if dt.tzinfo is None: raise HTTPException(422,'DECISION_TIME_MUST_BE_TIMEZONE_AWARE')
    if not isinstance(payload.get('candidates'),list): raise HTTPException(422,'CANDIDATES_MUST_BE_LIST')
    return v21_service.select(payload['candidates'],dt,str(payload.get('mode','SHADOW')).upper())

@app.post('/v21/kill-switch')
def v21_kill_switch(payload:dict):
    v21_service.risk.set_kill_switch(bool(payload.get('enabled')))
    return {'status':'PASS','kill_switch':v21_service.risk.state.kill_switch}

@app.get('/v21/ledger')
def v21_ledger(): return {'events':v21_service.ledger.events(),'positions':v21_service.ledger.positions(),'fingerprint':v21_service.ledger.fingerprint(),'chain':v21_service.ledger.verify_chain()}

@app.post('/v21/ledger/settle')
def v21_settle(payload:dict):
    key=str(payload.get('aggregate_id') or payload.get('record_id') or '')
    if not key: raise HTTPException(422,'AGGREGATE_ID_REQUIRED')
    result=str(payload.get('result',''))
    if result not in {'WIN','LOSS','VOID'}: raise HTTPException(422,'INVALID_RESULT')
    return v21_service.settle(key,result,payload.get('closing_odds'),payload.get('exit_reason'))

@app.post('/v21/ledger/export')
def v21_export(): return {'status':'PASS','path':v21_service.ledger.export_xlsx()}

@app.get('/v21/performance')
def v21_performance(): return v21_service.ledger.performance()

@app.get('/v21/research')
def v21_research(): return {'rows':v21_service.research.rows()}

@app.post('/v21/live/scan')
def v21_live_scan(payload:dict):
    if 'decision_time' not in payload or 'live_state' not in payload or 'odds' not in payload or 'source' not in payload: raise HTTPException(422,'LIVE_SCAN_FIELDS_REQUIRED')
    try: dt=datetime.fromisoformat(str(payload['decision_time']).replace('Z','+00:00'))
    except Exception as exc: raise HTTPException(422,'INVALID_DECISION_TIME') from exc
    if dt.tzinfo is None: raise HTTPException(422,'DECISION_TIME_MUST_BE_TIMEZONE_AWARE')
    from .v21.live_monitor import LiveMonitor
    monitor=getattr(v21_service,'live_monitor',None)
    if monitor is None: v21_service.live_monitor=LiveMonitor(max_age_seconds=float(os.getenv('LIVE_MAX_AGE_SECONDS','20'))); monitor=v21_service.live_monitor
    return monitor.observe(source=str(payload['source']),event_id=str(payload['live_state'].get('event_id')),live_state=payload['live_state'],odds_rows=payload['odds'],decision_time=dt,decision_service=v21_service)


app.include_router(v22_router)
app.include_router(v24_router)
app.include_router(v25_router)
