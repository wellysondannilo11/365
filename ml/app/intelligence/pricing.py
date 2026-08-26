from __future__ import annotations
from dataclasses import dataclass, asdict
from math import isfinite

@dataclass(frozen=True)
class PriceAssessment:
    market:str; selection:str; line:float|None; bookmaker:str; odds:float
    implied_probability:float|None; robo_probability:float|None; fair_odds:float|None
    edge:float|None; ev:float|None; confidence:str; status:str; reason:str
    pit_status:str; odds_source:str
    def as_dict(self): return asdict(self)

class LiveMarketPricer:
    def __init__(self,min_edge=.05,min_ev=.05,max_uncertainty=.12):
        self.min_edge=min_edge; self.min_ev=min_ev; self.max_uncertainty=max_uncertainty

    def assess(self,row,robo_probability,uncertainty=.05,pit_status='KNOWN_BEFORE_DECISION',model_validated=False):
        odds=float(row['odds']); implied=1/odds if odds>1 else None
        fair=1/robo_probability if robo_probability and robo_probability>0 else None
        edge=robo_probability-implied if implied is not None and robo_probability is not None else None
        ev=robo_probability*odds-1 if robo_probability is not None and odds>1 else None
        confidence='HIGH' if model_validated and uncertainty<=.05 else 'MEDIUM' if model_validated and uncertainty<=.12 else 'LOW'
        status='NO BET'; reason='NOT_DETERMINED'
        if pit_status!='KNOWN_BEFORE_DECISION': reason='PIT_NOT_PROVEN'
        elif not model_validated: reason='MODEL_NOT_VALIDATED'
        elif edge is None or ev is None: reason='PRICE_OR_PROBABILITY_MISSING'
        elif uncertainty>self.max_uncertainty: reason='HIGH_UNCERTAINTY'
        elif edge<self.min_edge or ev<self.min_ev: reason='INSUFFICIENT_EDGE_OR_EV'
        else: status='BET'; reason='QUALITY_GATE_PASSED'
        return PriceAssessment(str(row.get('market')),str(row.get('selection')),row.get('line'),str(row.get('bookmaker','')),odds,implied,robo_probability,fair,edge,ev,confidence,status,reason,pit_status,str(row.get('source','UNKNOWN'))).as_dict()
