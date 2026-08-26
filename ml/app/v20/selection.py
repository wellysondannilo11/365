from __future__ import annotations
from dataclasses import dataclass
from .stake import StakePolicy,size_stake
@dataclass(frozen=True)
class Candidate:
    event_id:str; market:str; selection:str; odds:float; probability:float
    data_quality:float=100.0; calibration:float=1.0; uncertainty:float=0.0
    liquidity:float=1.0; market_quality:float=1.0; robustness:float=1.0
    model_agreement:float=1.0; live:bool=False; stale:bool=False; pit_ok:bool=True
    correlation_penalty:float=0.0; sample_size:int=0
    def fair_odds(self): return 1.0/self.probability if self.probability>0 else None
    def edge(self): return self.probability-(1.0/self.odds) if self.odds>1 else -1.0
    def ev(self): return self.probability*self.odds-1.0 if self.odds>1 else -1.0
def score(c):
    e=max(0,c.edge()); v=max(0,c.ev())
    return max(0,min(100,100*(0.28*min(e/0.15,1)+0.22*min(v/0.30,1)+0.12*c.calibration+0.10*c.data_quality/100+0.08*c.liquidity+0.07*c.market_quality+0.06*c.robustness+0.07*c.model_agreement-0.10*c.uncertainty)))
def evaluate(c, *, min_odds=1.50, preferred_odds=1.66, min_edge=0.05, min_ev=0.05, min_data_quality=80, min_calibration=0.70, max_uncertainty=0.12, min_market_quality=0.40, risk_allowed=True, policy=None):
    reasons=[]
    if not c.pit_ok: reasons.append('PIT_FAILURE')
    if c.odds < min_odds: reasons.append('ODDS_TOO_LOW')
    if c.data_quality < min_data_quality: reasons.append('LOW_DATA_QUALITY')
    if c.calibration < min_calibration: reasons.append('LOW_CALIBRATION')
    if c.uncertainty > max_uncertainty: reasons.append('HIGH_UNCERTAINTY')
    if c.model_agreement < 0.70: reasons.append('MODEL_DISAGREEMENT')
    if c.stale: reasons.append('STALE_ODDS')
    if c.liquidity <= 0: reasons.append('LOW_LIQUIDITY')
    if c.market_quality < min_market_quality: reasons.append('MARKET_QUALITY_LOW')
    if c.sample_size and c.sample_size < 30: reasons.append('INSUFFICIENT_SAMPLE')
    if c.edge() < min_edge: reasons.append('INSUFFICIENT_EDGE')
    if c.ev() < min_ev: reasons.append('INSUFFICIENT_EV')
    if not risk_allowed: reasons.append('RISK_LIMIT')
    s=score(c); stake=0.0
    if not reasons and policy:
        stake=size_stake(c.probability,c.odds,policy=policy,edge=c.edge(),uncertainty=c.uncertainty,correlation_penalty=c.correlation_penalty)
        if stake<=0: reasons.append('RISK_LIMIT')
    decision='NO BET' if reasons else 'BET'
    grade='NO BET' if decision=='NO BET' else ('EXCEPTIONAL' if s>=85 else 'STRONG VALUE' if s>=72 else 'CANDIDATE')
    return {'decision':decision,'grade':grade,'stake':stake,'score':round(s,2),'fair_probability':c.probability,'fair_odds':c.fair_odds(),'edge':c.edge(),'ev':c.ev(),'no_bet_reason':'|'.join(reasons) if reasons else None,'preferred_odds':preferred_odds}
def rank_candidates(candidates, **kwargs):
    evaluated=[(c,evaluate(c,**kwargs)) for c in candidates]
    evaluated.sort(key=lambda x:(x[1]['decision']=='BET',x[1]['score'],x[1]['ev'],x[1]['edge']),reverse=True)
    return [dict(event_id=c.event_id,market=c.market,selection=c.selection,odds=c.odds,**e) for c,e in evaluated]
