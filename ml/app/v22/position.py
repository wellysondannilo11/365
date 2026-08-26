from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

@dataclass
class PositionDecision:
    action:str
    reason:str
    current_edge:float|None=None
    current_ev:float|None=None
    recommended:bool=True
    created_at:str=''
    def to_dict(self): return asdict(self)

def assess_position(*, entry_odds:float, current_odds:float, fair_probability:float, remaining_minutes:int, uncertainty:float=0.0, exit_cost:float=0.0, min_edge:float=0.05):
    fair=1.0/fair_probability if fair_probability>0 else float('inf')
    edge=fair_probability-(1/current_odds if current_odds>1 else 0)
    ev=fair_probability*current_odds-1
    if exit_cost>0: ev-=exit_cost
    if remaining_minutes<=0: action='EXIT'; reason='MATCH_COMPLETE'
    elif edge>=min_edge and ev>=0: action='HOLD'; reason='POSITIVE_REPRICED_VALUE'
    elif edge<0 or ev<0: action='EXIT'; reason='NEGATIVE_CURRENT_VALUE'
    elif uncertainty>0.15: action='REDUCE'; reason='HIGH_UNCERTAINTY'
    else: action='REASSESS'; reason='MARGINAL_VALUE'
    return PositionDecision(action,reason,edge,ev,True,datetime.now(timezone.utc).isoformat()).to_dict()

def reversal_candidate(*, opposite_odds:float, opposite_probability:float, min_edge:float=0.05, remaining_minutes:int=90):
    edge=opposite_probability-(1/opposite_odds if opposite_odds>1 else 0); ev=opposite_probability*opposite_odds-1
    ok=remaining_minutes>0 and edge>=min_edge and ev>=0
    return {'decision':'NEW OPPORTUNITY' if ok else 'NO BET','edge':edge,'ev':ev,'reason':'INDEPENDENT_POSITIVE_VALUE' if ok else 'NO_INDEPENDENT_VALUE'}
