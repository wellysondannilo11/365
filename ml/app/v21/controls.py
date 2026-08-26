from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class ExposureLimits:
    max_per_event: float=1.0
    max_simultaneous: float=5.0
    max_daily_exposure: float=3.0
    max_daily_loss: float=4.0
    max_per_league: float=2.0
    max_per_market: float=2.0
    max_correlated: float=1.0

@dataclass
class ControlState:
    kill_switch: bool=False
    day: str=''
    daily_exposure: float=0.0
    daily_pnl: float=0.0
    open_exposure: float=0.0
    event_exposure: dict=field(default_factory=dict)
    league_exposure: dict=field(default_factory=dict)
    market_exposure: dict=field(default_factory=dict)
    correlated_exposure: dict=field(default_factory=dict)

class RiskControllerV21:
    def __init__(self,limits=None): self.limits=limits or ExposureLimits();self.state=ControlState()
    def _reset(self,now):
        day=now.astimezone(timezone.utc).date().isoformat() if now.tzinfo else now.replace(tzinfo=timezone.utc).date().isoformat()
        if self.state.day!=day:self.state=ControlState(day=day,kill_switch=self.state.kill_switch)
    def set_kill_switch(self,enabled): self.state.kill_switch=bool(enabled)
    def allowed(self,now,event_id,league,market,stake,correlation_key=None):
        self._reset(now); s=float(stake)
        if self.state.kill_switch:return False,'GLOBAL_KILL_SWITCH'
        if self.state.daily_pnl<=-self.limits.max_daily_loss:return False,'MAX_DAILY_LOSS'
        if self.state.daily_exposure+s>self.limits.max_daily_exposure:return False,'MAX_DAILY_EXPOSURE'
        if self.state.open_exposure+s>self.limits.max_simultaneous:return False,'MAX_SIMULTANEOUS_EXPOSURE'
        if self.state.event_exposure.get(event_id,0)+s>self.limits.max_per_event:return False,'MAX_EVENT_EXPOSURE'
        if self.state.league_exposure.get(league,0)+s>self.limits.max_per_league:return False,'MAX_LEAGUE_EXPOSURE'
        if self.state.market_exposure.get(market,0)+s>self.limits.max_per_market:return False,'MAX_MARKET_EXPOSURE'
        if correlation_key and self.state.correlated_exposure.get(correlation_key,0)+s>self.limits.max_correlated:return False,'MAX_CORRELATED_EXPOSURE'
        return True,None
    def open(self,event_id,league,market,stake,correlation_key=None):
        s=float(stake);self.state.daily_exposure+=s;self.state.open_exposure+=s
        for d,k in ((self.state.event_exposure,event_id),(self.state.league_exposure,league),(self.state.market_exposure,market)) : d[k]=d.get(k,0)+s
        if correlation_key:self.state.correlated_exposure[correlation_key]=self.state.correlated_exposure.get(correlation_key,0)+s
    def close(self,event_id,league,market,stake,pnl,now,correlation_key=None):
        self._reset(now);s=float(stake);self.state.open_exposure=max(0,self.state.open_exposure-s);self.state.daily_pnl+=float(pnl)
        for d,k in ((self.state.event_exposure,event_id),(self.state.league_exposure,league),(self.state.market_exposure,market)) : d[k]=max(0,d.get(k,0)-s)
        if correlation_key:self.state.correlated_exposure[correlation_key]=max(0,self.state.correlated_exposure.get(correlation_key,0)-s)
