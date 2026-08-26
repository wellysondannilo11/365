from __future__ import annotations
from dataclasses import dataclass,field
from datetime import timezone
@dataclass
class PortfolioLimits:
    max_per_event:float=1.0; max_per_day:float=3.0; max_simultaneous:float=5.0; daily_stop:float=-4.0; loss_streak_limit:int=3
@dataclass
class PortfolioState:
    daily_pnl:float=0.0; open_exposure:float=0.0; loss_streak:int=0; tips_taken:int=0; event_exposure:dict=field(default_factory=dict); day:str=''
class PortfolioRisk:
    def __init__(self,limits=None): self.limits=limits or PortfolioLimits(); self.state=PortfolioState()
    def _day(self,now): return now.astimezone(timezone.utc).date().isoformat() if now.tzinfo else now.replace(tzinfo=timezone.utc).date().isoformat()
    def reset(self,now):
        d=self._day(now)
        if self.state.day and self.state.day!=d: self.state=PortfolioState(day=d)
        elif not self.state.day: self.state.day=d
    def allowed(self,now,event_id,stake):
        self.reset(now)
        if self.state.daily_pnl<=self.limits.daily_stop or self.state.loss_streak>=self.limits.loss_streak_limit:return False
        if self.state.tips_taken >= self.limits.max_per_day:return False
        if stake <= 0:return False
        if self.state.open_exposure+stake>self.limits.max_simultaneous:return False
        if self.state.event_exposure.get(event_id,0)+stake>self.limits.max_per_event:return False
        return True
    def open(self,event_id,stake):
        self.state.open_exposure+=stake; self.state.event_exposure[event_id]=self.state.event_exposure.get(event_id,0)+stake; self.state.tips_taken+=1
    def close(self,event_id,stake,pnl,now):
        self.reset(now);self.state.open_exposure=max(0,self.state.open_exposure-stake);self.state.event_exposure[event_id]=max(0,self.state.event_exposure.get(event_id,0)-stake);self.state.daily_pnl+=pnl;self.state.loss_streak=self.state.loss_streak+1 if pnl<0 else 0
