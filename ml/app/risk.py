from dataclasses import dataclass,field
from datetime import datetime
@dataclass
class RiskState:
    bankroll:float=50.0; daily_pnl:float=0; loss_streak:int=0; cooldown_until:datetime|None=None
    event_exposure:dict=field(default_factory=dict); correlated_exposure:dict=field(default_factory=dict)
class RiskEngine:
    def __init__(self,bankroll=50,daily_stop=-4,loss_limit=3): self.state=RiskState(bankroll=bankroll);self.daily_stop=daily_stop;self.loss_limit=loss_limit
    def reset_if_new_day(self,now):
        if self.state.cooldown_until and now.date()>self.state.cooldown_until.date(): self.state.cooldown_until=None;self.state.loss_streak=0;self.state.daily_pnl=0
    def allowed(self,now):
        self.reset_if_new_day(now);return self.state.daily_pnl>self.daily_stop and not(self.state.cooldown_until and now<self.state.cooldown_until)
    def settle(self,pnl,now):
        self.reset_if_new_day(now);self.state.daily_pnl+=pnl;self.state.bankroll+=pnl;self.state.loss_streak=self.state.loss_streak+1 if pnl<0 else 0
        if self.state.loss_streak>=self.loss_limit or self.state.daily_pnl<=self.daily_stop:self.state.cooldown_until=now.replace(hour=23,minute=59,second=59,microsecond=0)
    def register_exposure(self,event_id,stake,correlation_group=None):
        self.state.event_exposure[event_id]=self.state.event_exposure.get(event_id,0)+stake
        if correlation_group:self.state.correlated_exposure[correlation_group]=self.state.correlated_exposure.get(correlation_group,0)+stake
    def stake(self,p,odds):
        b=odds-1;k=max(0,(b*p-(1-p))/b)*.25;raw=k*self.state.bankroll
        return 2.0 if raw>=1.5 else 1.5 if raw>=.9 else 1.0 if raw>=.45 else .5 if raw>0 else 0
