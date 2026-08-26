from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class PositionDecision:
    action:str; reason:str; current_edge:float|None=None; entry_edge:float|None=None

def reassess(entry_odds,current_odds,fair_probability,min_edge=.05,exit_edge=0.0):
    if current_odds<=1 or not 0<fair_probability<1:return PositionDecision("REASSESS","INVALID_CURRENT_PRICE")
    entry_edge=fair_probability-1/entry_odds; current_edge=fair_probability-1/current_odds
    if current_edge < exit_edge - 1e-12:return PositionDecision("EXIT","NEGATIVE_CURRENT_VALUE",current_edge,entry_edge)
    if current_edge < min_edge - 1e-12:return PositionDecision("REDUCE","EDGE_DETERIORATED",current_edge,entry_edge)
    return PositionDecision("HOLD","VALUE_REMAINS",current_edge,entry_edge)

def reversal(current_odds,current_probability,min_edge=.05):
    if current_odds<=1 or not 0<current_probability<1:return PositionDecision("REASSESS","INVALID_REVERSAL_PRICE")
    edge=current_probability-1/current_odds
    return PositionDecision("REVERSE","INDEPENDENT_VALUE",edge,None) if edge>=min_edge else PositionDecision("REASSESS","NO_INDEPENDENT_VALUE",edge,None)
