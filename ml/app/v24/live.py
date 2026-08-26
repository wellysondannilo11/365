from __future__ import annotations
from dataclasses import dataclass,asdict
from datetime import datetime,timezone

@dataclass(frozen=True)
class LiveSnapshot:
    event_id:str; captured_at:str; minute:int; home_goals:int; away_goals:int
    home_xg:float=0; away_xg:float=0; shots:int=0; shots_on_target:int=0
    red_cards_home:int=0; red_cards_away:int=0; substitutions:int=0
    source_timestamp:str|None=None
    def to_dict(self): return asdict(self)

class LiveStateEngine:
    def __init__(self,max_age_seconds=20): self.max_age_seconds=max_age_seconds; self.history={}
    def ingest(self,snapshot,decision_time=None):
        decision_time=decision_time or datetime.now(timezone.utc)
        reasons=[]
        try:
            captured=datetime.fromisoformat(str(snapshot.get("captured_at")).replace("Z","+00:00"))
            source=datetime.fromisoformat(str(snapshot.get("source_timestamp")).replace("Z","+00:00"))
        except Exception:
            captured=source=None
        if not snapshot.get("event_id"): reasons.append("MISSING_EVENT_ID")
        if captured is None or captured.tzinfo is None: reasons.append("INVALID_CAPTURED_AT")
        if source is None or source.tzinfo is None: reasons.append("SOURCE_TIMESTAMP_REQUIRED")
        if captured and captured>decision_time: reasons.append("CAPTURED_AT_IN_FUTURE")
        if source and source>decision_time: reasons.append("SOURCE_TIMESTAMP_IN_FUTURE")
        if source and (decision_time-source).total_seconds()>self.max_age_seconds: reasons.append("STALE_SOURCE")
        if int(snapshot.get("minute",-1))<0: reasons.append("INVALID_MINUTE")
        quality={"status":"BLOCK" if reasons else "PASS","reasons":reasons,
                 "source_timestamp":source.isoformat() if source else None,
                 "captured_at":captured.isoformat() if captured else None}
        if reasons: return {"status":"BLOCK","quality":quality}
        self.history.setdefault(snapshot["event_id"],[]).append(dict(snapshot))
        self.history[snapshot["event_id"]].sort(key=lambda x:(int(x.get("minute",0)),x.get("captured_at","")))
        return {"status":"PASS","quality":quality,"snapshot":snapshot}
    def snapshots(self,event_id): return list(self.history.get(event_id,[]))
