from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class PricePoint:
    timestamp:str; odds:float; bookmaker:str; market:str; selection:str; line:float|None

class PriceDiscovery:
    def __init__(self): self._points=defaultdict(list)
    def observe(self,row):
        key=(str(row.get("event_id")),str(row.get("bookmaker")),str(row.get("market")),str(row.get("selection")),row.get("line"))
        p=PricePoint(str(row.get("source_timestamp") or row.get("captured_at")),float(row["odds"]),key[1],key[2],key[3],key[4])
        self._points[key].append(p); self._points[key].sort(key=lambda x:x.timestamp)
        return self.metrics(key)
    def metrics(self,key):
        ps=self._points.get(key,[])
        if not ps:return None
        odds=[p.odds for p in ps]; cur=ps[-1].odds; prev=ps[-2].odds if len(ps)>1 else cur
        try:
            t0=float(__import__('datetime').datetime.fromisoformat(ps[-2].timestamp.replace('Z','+00:00')).timestamp()) if len(ps)>1 else float(__import__('datetime').datetime.fromisoformat(ps[0].timestamp.replace('Z','+00:00')).timestamp())
            t1=float(__import__('datetime').datetime.fromisoformat(ps[-1].timestamp.replace('Z','+00:00')).timestamp())
            dt=max(1e-6,t1-t0); velocity=(cur-prev)/dt
        except Exception: velocity=0.0
        acceleration=0.0
        if len(ps)>2:
            try:
                t2=float(__import__('datetime').datetime.fromisoformat(ps[-2].timestamp.replace('Z','+00:00')).timestamp()); t3=float(__import__('datetime').datetime.fromisoformat(ps[-3].timestamp.replace('Z','+00:00')).timestamp());
                v0=(ps[-2].odds-ps[-3].odds)/max(1e-6,t2-t3); acceleration=velocity-v0
            except Exception: pass
        return {"opening_price":odds[0],"current_price":cur,"max_price":max(odds),"min_price":min(odds),"movement":round(cur-odds[0],10),"direction":"UP" if cur>odds[0] else "DOWN" if cur<odds[0] else "FLAT","velocity":velocity,"acceleration":acceleration,"n":len(ps)}


    def aggregate(self, rows):
        groups=defaultdict(list)
        for r in rows:
            try:
                groups[(str(r.get("event_id")),str(r.get("market")),r.get("line"),str(r.get("selection")))].append(float(r["odds"]))
            except Exception:
                pass
        out={}
        for k,vals in groups.items():
            if not vals: continue
            out[k]={"consensus_price":sum(vals)/len(vals),"best_price":max(vals),"worst_price":min(vals),"bookmaker_count":len(vals),"divergence":round(max(vals)-min(vals),10)}
        return out
