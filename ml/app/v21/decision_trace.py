from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib, json

@dataclass(frozen=True)
class DecisionTrace:
    trace_id: str
    created_at: str
    decision: str
    why: str
    event_id: str
    market: str | None
    selection: str | None
    model_version: str
    feature_version: str
    pricing_version: str
    config_version: str
    data_snapshot_id: str | None
    pit_status: str
    inputs: dict
    outputs: dict
    reasons: list[str]

    @classmethod
    def create(cls, *, decision, why, event_id, market=None, selection=None, model_version='v21', feature_version='v21', pricing_version='v20', config_version='v21', data_snapshot_id=None, pit_status='PASS', inputs=None, outputs=None, reasons=None):
        created=datetime.now(timezone.utc).isoformat()
        raw=f'{created}|{event_id}|{market}|{selection}|{decision}|{json.dumps(outputs or {},sort_keys=True,default=str)}'
        tid=hashlib.sha256(raw.encode()).hexdigest()[:24]
        return cls(tid,created,decision,why,event_id,market,selection,model_version,feature_version,pricing_version,config_version,data_snapshot_id,pit_status,inputs or {},outputs or {},reasons or [])

    def to_dict(self): return asdict(self)
