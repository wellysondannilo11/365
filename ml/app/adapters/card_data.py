from __future__ import annotations
"""Provider-neutral card data contract plus API-Football implementation.

The implementation is optional. It is never used as a fake source and never
claims exact historical PIT availability when the provider does not expose it.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol, Any
import requests

@dataclass(frozen=True)
class CardDataSnapshot:
    event_id: str
    referee_id: str | None
    referee_name: str | None
    home_cards: int | None
    away_cards: int | None
    total_cards: int | None
    source: str
    source_timestamp: str
    captured_at: str
    availability_evidence: str
    payload: dict[str,Any]

class CardDataProvider(Protocol):
    name: str
    @property
    def configured(self) -> bool: ...
    def match_card_snapshot(self, event_id: str) -> CardDataSnapshot: ...

class APIFootballCardProvider:
    name='api-football-cards'
    base_url='https://v3.football.api-sports.io'
    def __init__(self,key=None,timeout=20,session=None):
        import os
        self.key=key or os.getenv('API_FOOTBALL_KEY','')
        self.timeout=timeout; self.session=session or requests.Session()
    @property
    def configured(self): return bool(self.key)
    def _get(self,path,params):
        if not self.configured: raise RuntimeError('CREDENTIALS_UNAVAILABLE')
        r=self.session.get(self.base_url+path,params=params,headers={'x-apisports-key':self.key,'User-Agent':'RoboDaBet/CardData'},timeout=self.timeout)
        r.raise_for_status(); return r.json()
    def match_card_snapshot(self,event_id):
        captured=datetime.now(timezone.utc).isoformat()
        payload=self._get('/fixtures',{'id':event_id})
        rows=payload.get('response') or []
        if not rows: raise RuntimeError('EVENT_NOT_FOUND')
        fixture=rows[0]
        ref=(fixture.get('fixture') or {}).get('referee')
        teams=fixture.get('teams') or {}
        home_id=(teams.get('home') or {}).get('id'); away_id=(teams.get('away') or {}).get('id')
        events=self._get('/fixtures/events',{'fixture':event_id}).get('response') or []
        hc=ac=0
        for e in events:
            if str(e.get('type','')).lower() != 'card': continue
            team_id=(e.get('team') or {}).get('id')
            detail=str(e.get('detail') or '').lower()
            # Count yellow/red cards conservatively. Provider-specific details are preserved.
            if 'yellow' in detail or 'red' in detail:
                if team_id==home_id: hc+=1
                elif team_id==away_id: ac+=1
        return CardDataSnapshot(str(event_id),None if not ref else str(ref),ref,hc,ac,hc+ac,'api-football',captured,captured,'CAPTURED_AT_ONLY',{'fixture':fixture,'events':events})
