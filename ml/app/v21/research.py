from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json
import numpy as np

@dataclass(frozen=True)
class ResearchObservation:
    observation_id: str
    created_at: str
    mode: str
    event_id: str
    decision: str
    payload: dict

class ResearchStore:
    def __init__(self,path='artifacts/paper_trading/v21_research.jsonl'):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
    def append(self,mode,event_id,decision,payload):
        now=datetime.now(timezone.utc).isoformat();oid=hashlib.sha256(f'{now}|{event_id}|{decision}|{json.dumps(payload,sort_keys=True,default=str)}'.encode()).hexdigest()[:32]
        row=asdict(ResearchObservation(oid,now,mode,event_id,decision,payload))
        with self.path.open('a',encoding='utf-8') as f:f.write(json.dumps(row,sort_keys=True,default=str)+'\n')
        return row
    def rows(self): return [json.loads(x) for x in self.path.read_text(encoding='utf-8').splitlines() if x.strip()] if self.path.exists() else []

def distribution_shift(reference, recent, threshold=0.25):
    a=np.asarray(reference,dtype=float);b=np.asarray(recent,dtype=float)
    if len(a)<5 or len(b)<5:return {'status':'INSUFFICIENT_SAMPLE','shift':None,'threshold':threshold}
    ref_mean,cur_mean=float(np.nanmean(a)),float(np.nanmean(b));ref_std=float(np.nanstd(a) or 1.0)
    shift=abs(cur_mean-ref_mean)/ref_std
    return {'status':'DRIFT' if shift>=threshold else 'STABLE','shift':shift,'threshold':threshold}
