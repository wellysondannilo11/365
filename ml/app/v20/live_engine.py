from __future__ import annotations
from dataclasses import dataclass,asdict
from datetime import datetime
from .selection import Candidate,evaluate
from ..v19.engine import PricingEngine
@dataclass(frozen=True)
class LiveState:
    event_id:str; decision_time:datetime; minute:int; home_goals:int; away_goals:int; home_xg:float; away_xg:float; shots:int=0; shots_on_target:int=0; corners:int=0; red_cards_home:int=0; red_cards_away:int=0; possession_home:float|None=None; possession_away:float|None=None
    def sample_size(self): return self.shots+self.shots_on_target+self.corners+round((self.home_xg+self.away_xg)*4)
class LiveRepricingEngine:
    version='20.0.0-live'
    def __init__(self): self.pricer=PricingEngine()
    def reprice(self,state,home_lambda,away_lambda,markets):
        if state.minute<15 or state.sample_size()<8:return {'status':'NO BET','reason':'INSUFFICIENT_SAMPLE','state':asdict(state),'markets':[]}
        rem=max(0,90-state.minute)/90;tempo=max(0.05,(state.home_xg+state.away_xg)/max(state.minute/90,0.15));total_pre=max(0.05,home_lambda+away_lambda);factor=0.55+0.45*min(2.0,tempo/total_pre)
        hl=max(0.01,home_lambda*factor*rem);al=max(0.01,away_lambda*factor*rem)
        priced=self.pricer.price(event_id=state.event_id,decision_time=state.decision_time,home_expected_goals=hl,away_expected_goals=al,market_state='LIVE')
        by={(m['market'],m['selection'],m.get('line')):m for m in priced['markets']};out=[]
        for row in markets:
            mp=by.get((row['market'],row['selection'],row.get('line')))
            if not mp: continue
            c=Candidate(state.event_id,row['market'],row['selection'],float(row['odds']),float(mp['probability']),data_quality=float(row.get('data_quality',90)),calibration=float(row.get('calibration',0.85)),uncertainty=float(row.get('uncertainty',0.05)),liquidity=float(row.get('liquidity',1)),market_quality=float(row.get('market_quality',0.8)),robustness=float(row.get('robustness',0.7)),model_agreement=float(row.get('model_agreement',0.85)),live=True,pit_ok=bool(row.get('pit_ok',True)),sample_size=state.sample_size())
            out.append({**row,'probability':c.probability,**evaluate(c,min_odds=1.50,min_edge=0.05,min_ev=0.05,min_data_quality=80)})
        out.sort(key=lambda x:(x['decision']=='BET',x['score'],x['ev']),reverse=True)
        return {'status':'OK','state':asdict(state),'markets':out,'best':out[0] if out else None,'pricing':priced}
