from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import json, logging, threading

@dataclass
class Counter:
    name:str; value:float=0

class Metrics:
    def __init__(self): self._c={}; self._lock=threading.Lock()
    def inc(self,name,value=1):
        with self._lock: self._c[name]=self._c.get(name,0)+value
    def snapshot(self):
        with self._lock: return dict(self._c)
    def prometheus(self): return '\n'.join(f'{k} {v}' for k,v in sorted(self.snapshot().items()))+'\n'

metrics=Metrics()
logger=logging.getLogger('robo.v22')
if not logger.handlers:
    handler=logging.StreamHandler(); handler.setFormatter(logging.Formatter('%(message)s')); logger.addHandler(handler); logger.setLevel(logging.INFO)

def log_event(event,**fields):
    payload={'timestamp':datetime.now(timezone.utc).isoformat(),'event':event,**fields}; logger.info(json.dumps(payload,sort_keys=True,default=str)); return payload

class TraceContext:
    def __init__(self,trace_id): self.trace_id=trace_id
    def __enter__(self): return self
    def __exit__(self,*args): return False
