from __future__ import annotations
from datetime import datetime, timezone
from .quality import validate_live_state
from .realtime import FeedHealth, FeedStatus

class LiveMonitor:
    """Provider-agnostic live orchestration. Providers are injected; no scraping or execution is performed here."""
    def __init__(self, *, max_age_seconds=20.0):
        self.max_age_seconds=max_age_seconds
        self.health={}
    def observe(self, *, source, event_id, live_state, odds_rows, decision_time, decision_service):
        h=self.health.setdefault(source,FeedHealth(source,max_age_seconds=self.max_age_seconds))
        captured_at=live_state.get('captured_at')
        try: captured=datetime.fromisoformat(str(captured_at).replace('Z','+00:00'))
        except Exception: captured=None
        if captured is None:
            h.fail(); return {'status':'DATA QUALITY BLOCK','feed_status':h.status.value,'reasons':['INVALID_CAPTURED_AT'],'opportunities':[]}
        h.observe(captured,decision_time)
        quality=validate_live_state(live_state,decision_time,max_age_seconds=self.max_age_seconds)
        if not quality['ok'] or not h.can_decide():
            return {'status':'DATA QUALITY BLOCK','feed_status':h.status.value,'reasons':quality['reasons'] or [h.status.value],'opportunities':[]}
        enriched=[]
        for row in odds_rows:
            r=dict(row);r['event_id']=event_id;r['live']=True;r.setdefault('available_at',r.get('captured_at',captured.isoformat()));r.setdefault('data_quality',100);enriched.append(r)
        result=decision_service.select(enriched,decision_time,'SHADOW')
        return {'status':'FEED ONLINE','feed_status':h.status.value,'event_id':event_id,'decision_time':decision_time.isoformat(),'opportunities':result['opportunities'],'approved':result['approved'],'no_bet_count':result['no_bet_count']}
