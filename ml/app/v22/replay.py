from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib, json

@dataclass(frozen=True)
class Snapshot:
    event_id:str; sequence:int; captured_at:str; payload:dict; payload_hash:str

def make_snapshot(event_id,sequence,captured_at,payload):
    raw=json.dumps(payload,sort_keys=True,separators=(',',':'),default=str)
    return Snapshot(str(event_id),int(sequence),str(captured_at),payload,hashlib.sha256(raw.encode()).hexdigest())

class ReplayEngine:
    def __init__(self,snapshots=None): self.snapshots=list(snapshots or [])
    def add(self,event_id,payload,captured_at=None,sequence=None):
        captured_at=captured_at or datetime.now(timezone.utc).isoformat(); sequence=len(self.snapshots) if sequence is None else sequence
        s=make_snapshot(event_id,sequence,captured_at,payload); self.snapshots.append(s); return s
    def replay(self, callback):
        return [callback(asdict(s)) for s in sorted(self.snapshots,key=lambda x:(x.event_id,x.sequence))]
    def export(self): return [asdict(x) for x in self.snapshots]
