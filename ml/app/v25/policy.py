from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class EntryPolicy:
    min_odds:float=1.50; preferred_odds:float=1.66; exception_edge:float=.10; min_edge:float=.05; min_ev:float=.05; max_uncertainty:float=.12
    def check(self,odds,edge,ev,uncertainty,action="NEW_ENTRY"):
        if action != "NEW_ENTRY": return None
        if odds < self.min_odds:return "ODDS_BELOW_MINIMUM"
        if odds < self.preferred_odds and (edge < self.exception_edge or ev < self.exception_edge):return "ODDS_IN_EXCEPTION_BAND"
        if uncertainty>self.max_uncertainty:return "HIGH_UNCERTAINTY"
        if edge<self.min_edge:return "INSUFFICIENT_EDGE"
        if ev<self.min_ev:return "INSUFFICIENT_EV"
        return None
