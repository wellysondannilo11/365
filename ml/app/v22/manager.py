from __future__ import annotations
from datetime import datetime, timezone
from .providers import OddsAPIProvider, normalize_odds_api
from .dataset import ResearchDataset
from .replay import ReplayEngine
from .observability import metrics,log_event
from .persistence import V22Persistence
from ..v21.realtime import FeedHealth

class FeedManagerV22:
    def __init__(self,provider=None,dataset=None,replay=None,persistence=None):
        self.provider=provider or OddsAPIProvider(); self.dataset=dataset or ResearchDataset(); self.replay=replay or ReplayEngine(); self.persistence=persistence or V22Persistence(); self.health=FeedHealth(self.provider.name,max_age_seconds=30,delayed_after_seconds=10)
    def poll(self):
        metrics.inc('robo_v23_feed_polls_total')
        events,meta=self.provider.fetch_events_odds(); captured=datetime.now(timezone.utc); rows=normalize_odds_api(events,captured)
        for e in events:
            eid=str(e.get('id')); self.replay.add(eid,e,captured.isoformat()); self.persistence.record_event(eid,captured,e,self.provider.name)
        if rows:
            provider_times=[]
            for r in rows:
                try: provider_times.append(datetime.fromisoformat(r['source_timestamp'].replace('Z','+00:00')))
                except Exception: pass
                self.dataset.append({'type':'ODDS_SNAPSHOT',**r}); self.persistence.record_odds(r)
            newest=max(provider_times) if provider_times else None
            self.health.observe(newest,captured) if newest else setattr(self.health,'status',self.health.status.BLOCKED)
            age=max(0.0,(captured-newest).total_seconds()) if newest else None
            metrics.inc('robo_v23_odds_rows_total',len(rows));
            if age is not None and age>30: metrics.inc('robo_v23_stale_polls_total')
        else:
            self.health.status=self.health.status.STALE if events else self.health.status.OFFLINE
        log_event('FEED_POLL',provider=self.provider.name,events=len(events),odds_rows=len(rows),health=self.health.status.value,meta=meta)
        return {'events':events,'odds':rows,'health':self.health.status.value,'meta':meta,'captured_at':captured.isoformat()}
    def status(self):
        return {'provider':self.provider.name,'configured':getattr(self.provider,'configured',False),'status':self.health.status.value,'provider_health':self.provider.health.__dict__,'database':self.persistence.health()}
