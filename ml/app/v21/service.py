from __future__ import annotations
from datetime import datetime, timezone
import os
from .controls import RiskControllerV21, ExposureLimits
from .decision_trace import DecisionTrace
from .ledger import ImmutableEventLedger
from .notifications import provider_from_env, format_signal
from .quality import validate_market_snapshot
from .research import ResearchStore
from ..v20.selection import Candidate, rank_candidates
from ..v20.stake import StakePolicy

class DecisionServiceV21:
    version='21.0.0'
    def __init__(self):
        self.policy=StakePolicy(float(os.getenv('FRACTIONAL_KELLY','0.25')),float(os.getenv('MAX_STAKE_UNITS','1')),float(os.getenv('MIN_STAKE_UNITS','0.10')),float(os.getenv('BANKROLL_UNITS','50')))
        self.ledger=ImmutableEventLedger(unit_brl=float(os.getenv('UNIT_BRL','500')))
        self.research=ResearchStore()
        self.notify=provider_from_env()
        self.risk=RiskControllerV21(ExposureLimits(max_per_event=float(os.getenv('MAX_EVENT_EXPOSURE','1')),max_simultaneous=float(os.getenv('MAX_SIMULTANEOUS_EXPOSURE','5')),max_daily_exposure=float(os.getenv('MAX_DAILY_EXPOSURE','3')),max_daily_loss=float(os.getenv('MAX_DAILY_LOSS','4')),max_per_league=float(os.getenv('MAX_LEAGUE_EXPOSURE','2')),max_per_market=float(os.getenv('MAX_MARKET_EXPOSURE','2')),max_correlated=float(os.getenv('MAX_CORRELATED_EXPOSURE','1'))))
    def select(self,rows,decision_time,mode='SHADOW'):
        candidates=[];blocked=[]
        for r in rows:
            q=validate_market_snapshot(r,decision_time,max_age_seconds=float(os.getenv('LIVE_MAX_AGE_SECONDS','20')))
            if not q['ok']:
                blocked.append({**r,'decision':'NO BET','no_bet_reason':'|'.join(q['reasons']),'trace':DecisionTrace.create(decision='NO BET',why='DATA_QUALITY_BLOCK',event_id=str(r.get('event_id')),market=r.get('market'),selection=r.get('selection'),pit_status='FAIL',inputs=r,outputs={},reasons=q['reasons']).to_dict()})
                continue
            candidates.append(Candidate(event_id=str(r['event_id']),market=str(r['market']),selection=str(r['selection']),odds=float(r['odds']),probability=float(r['probability']),data_quality=float(r.get('data_quality',100)),calibration=float(r.get('calibration',1)),uncertainty=float(r.get('uncertainty',0)),liquidity=float(r.get('liquidity',1)),market_quality=float(r.get('market_quality',1)),robustness=float(r.get('robustness',1)),model_agreement=float(r.get('model_agreement',1)),live=bool(r.get('live',False)),stale=bool(r.get('stale',False)),pit_ok=bool(r.get('pit_ok',True)),correlation_penalty=float(r.get('correlation_penalty',0)),sample_size=int(r.get('sample_size',30))))
        ranked=rank_candidates(candidates,min_odds=float(os.getenv('MIN_ODDS','1.50')),preferred_odds=float(os.getenv('PREFERRED_ODDS','1.66')),min_edge=float(os.getenv('MIN_EDGE','0.05')),min_ev=float(os.getenv('MIN_EV','0.05')),min_data_quality=float(os.getenv('MIN_DQ','80')),max_uncertainty=float(os.getenv('MAX_UNCERTAINTY','0.12')),min_market_quality=float(os.getenv('MIN_MARKET_QUALITY','0.40')),policy=self.policy)
        # One best expression per event; reject correlated alternatives unless explicitly independent.
        approved=[];seen_events=set()
        for item in ranked:
            if item['decision']!='BET': continue
            league=next((str(r.get('league','')) for r in rows if str(r.get('event_id'))==item['event_id']), '')
            ok,reason=self.risk.allowed(decision_time,item['event_id'],league,item['market'],item['stake'],item['event_id'])
            if item['event_id'] in seen_events: ok,reason=False,'CORRELATED_EVENT_ALTERNATIVE'
            if not ok:
                item.update(decision='NO BET',stake=0,no_bet_reason=reason)
            else:
                seen_events.add(item['event_id']);approved.append(item)
        out=blocked+ranked
        approved_ids={(x['event_id'],x['market'],x['selection']) for x in approved}
        for item in out:
            if item.get('decision')=='BET' and (item['event_id'],item['market'],item['selection']) not in approved_ids:item.update(decision='NO BET',stake=0,no_bet_reason=item.get('no_bet_reason') or 'NOT_SELECTED')
        source_by_key={(str(r.get('event_id')),str(r.get('market')),str(r.get('selection'))):r for r in rows}
        for item in out:
            src=source_by_key.get((item['event_id'],item.get('market'),item.get('selection')), {})
            item['league']=str(src.get('league','')); item['country']=str(src.get('country','')); item['season']=str(src.get('season','')); item['event_name']=src.get('event_name')
            item['stake_units']=float(item.get('stake',0)); item['stake_brl']=item['stake_units']*self.ledger.unit_brl
            item['mode']=mode; item['trace']=DecisionTrace.create(decision=item['decision'],why='WHY_BET' if item['decision']=='BET' else 'WHY_NO_BET',event_id=item['event_id'],market=item.get('market'),selection=item.get('selection'),model_version='v21',feature_version='v21',pricing_version='v20',config_version='v21',data_snapshot_id=item.get('data_snapshot_id'),pit_status='PASS' if item.get('pit_ok',True) else 'FAIL',inputs=item,outputs={k:item.get(k) for k in ('fair_probability','fair_odds','edge','ev','score','stake')},reasons=[item['no_bet_reason']] if item.get('no_bet_reason') else []).to_dict()
            payload={**item,'decision_time':decision_time.isoformat()}
            et='SIGNAL_CREATED' if item['decision']=='BET' else 'SIGNAL_REJECTED'
            self.ledger.append(et,f"{item['event_id']}|{item['market']}|{item['selection']}",payload)
            self.research.append(mode,item['event_id'],item['decision'],payload)
        for item in approved:
            self.risk.open(item['event_id'],next((str(r.get('league','')) for r in rows if str(r.get('event_id'))==item['event_id']),''),item['market'],item['stake'],item['event_id'])
            if self.notify.enabled:self.notify.send(format_signal(item,status=mode))
        return {'opportunities':out,'approved':approved,'no_bet_count':sum(x.get('decision')=='NO BET' for x in out),'mode':mode,'kill_switch':self.risk.state.kill_switch}
    def settle(self,aggregate_id,result,closing_odds=None,exit_reason=None):
        positions=[p for p in self.ledger.positions() if p.get('record_id')==aggregate_id or p.get('aggregate_id')==aggregate_id]
        if not positions: raise KeyError(aggregate_id)
        p=positions[0];odds=float(p['odds']);stake=float(p.get('stake_units',p.get('stake',0)));pnl=stake*(odds-1) if result=='WIN' else -stake if result=='LOSS' else 0.0
        clv=(odds/float(closing_odds)-1) if closing_odds and float(closing_odds)>1 else None
        payload={'result':result,'pnl_units':pnl,'clv':clv,'status':'SETTLED','exit_reason':exit_reason,'settled_at':datetime.now(timezone.utc).isoformat()}
        row=self.ledger.append('RESULT_SETTLED',aggregate_id,payload)
        self.risk.close(p.get('event_id',''),p.get('league',''),p.get('market',''),stake,pnl,datetime.now(timezone.utc),p.get('event_id'))
        return row
