from __future__ import annotations
from datetime import datetime,timezone
class LiveStateEngine:
    def __init__(self,max_age_seconds=20):self.max_age_seconds=max_age_seconds;self.history={}
    def ingest(self,s):
        reasons=[];now=datetime.now(timezone.utc)
        def dt(v):
            try:
                x=datetime.fromisoformat(str(v).replace('Z','+00:00'));return x if x.tzinfo else None
            except Exception:return None
        src=dt(s.get('source_timestamp'));cap=dt(s.get('captured_at'))
        if not s.get('event_id'):reasons.append('MISSING_EVENT_ID')
        if src is None:reasons.append('SOURCE_TIMESTAMP_REQUIRED')
        if cap is None:reasons.append('CAPTURED_AT_REQUIRED')
        if src and src>now:reasons.append('SOURCE_TIMESTAMP_IN_FUTURE')
        if cap and cap>now:reasons.append('CAPTURED_AT_IN_FUTURE')
        if src and (now-src).total_seconds()>self.max_age_seconds:reasons.append('STALE_SOURCE')
        if int(s.get('minute',-1))<0 or int(s.get('minute',-1))>130:reasons.append('INVALID_MINUTE')
        if reasons:return {'status':'BLOCK','reasons':reasons}
        self.history.setdefault(str(s['event_id']),[]).append(dict(s));self.history[str(s['event_id'])].sort(key=lambda x:(int(x.get('minute',0)),x.get('captured_at','')));return {'status':'PASS','snapshot':s}
    def snapshots(self,event_id):return list(self.history.get(event_id,[]))
