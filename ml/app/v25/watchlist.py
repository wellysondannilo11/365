from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime,timezone
import uuid
@dataclass
class Watch:
    watch_id:str;event_id:str;market:str;selection:str;line:float|None;target_odds:float;current_odds:float;fair_odds:float|None;created_at:str;status:str='WATCH'
class Watchlist:
    def __init__(self):self.items={}
    def add(self,event_id,market,selection,line,current_odds,target_odds,fair_odds=None):
        if target_odds<=1 or current_odds<=1:raise ValueError('INVALID_WATCH_ODDS')
        w=Watch(str(uuid.uuid4()),str(event_id),str(market),str(selection),line,float(target_odds),float(current_odds),fair_odds,datetime.now(timezone.utc).isoformat());self.items[w.watch_id]=w;return w
    def update(self,current_odds,watch_id=None):
        out=[]
        for w in list(self.items.values()):
            if watch_id and w.watch_id!=watch_id:continue
            w.current_odds=float(current_odds) if watch_id else w.current_odds
            if w.status=='WATCH' and w.current_odds>=w.target_odds:w.status='TRIGGERED'
            out.append(w.__dict__.copy())
        return out
    def all(self):return [w.__dict__.copy() for w in self.items.values()]
