from __future__ import annotations

def assess_position(*, entry_odds:float, current_odds:float, fair_probability:float, stake_units:float, remaining_minutes:int, exit_cost:float=0.0, min_edge:float=0.05):
    if current_odds<=1 or fair_probability<=0 or fair_probability>=1: return {'action':'REASSESS','reason':'INVALID_CURRENT_PRICE'}
    current_edge=fair_probability-(1/current_odds);entry_edge=fair_probability-(1/entry_odds)
    if current_edge>=min_edge and current_edge>=entry_edge*0.35:return {'action':'HOLD','current_edge':current_edge,'entry_edge':entry_edge,'reason':'VALUE_REMAINS'}
    if current_edge>0 and current_edge<min_edge:return {'action':'REDUCE','current_edge':current_edge,'entry_edge':entry_edge,'reason':'EDGE_DETERIORATED'}
    if current_edge<=-max(exit_cost,0.0):return {'action':'EXIT','current_edge':current_edge,'entry_edge':entry_edge,'reason':'POSITION_NO_LONGER_HAS_VALUE'}
    return {'action':'REASSESS','current_edge':current_edge,'entry_edge':entry_edge,'reason':'MIXED_SIGNALS'}

def reverse_candidate(*,opposite_odds:float,opposite_probability:float,min_edge:float=0.05):
    edge=opposite_probability-(1/opposite_odds) if opposite_odds>1 else -1
    return {'eligible':edge>=min_edge,'edge':edge,'reason':'INDEPENDENT_VALUE' if edge>=min_edge else 'NO_INDEPENDENT_VALUE'}
