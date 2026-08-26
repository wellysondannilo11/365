from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any
import os, time, requests
from ..v21.realtime import ResilientPoller, canonical_hash

class ProviderError(RuntimeError): pass
class ProviderDataQualityError(ProviderError): pass

@dataclass
class ProviderHealth:
    provider: str
    status: str='OFFLINE'
    last_success: str|None=None
    last_error: str|None=None
    requests: int=0
    failures: int=0
    rate_limit_remaining: str|None=None
    rate_limit_used: str|None=None
    last_provider_timestamp: str|None=None
    last_latency_ms: float|None=None
    last_status_code: int|None=None
    retry_count: int=0

class OddsAPIProvider:
    name='the_odds_api'; base_url='https://api.the-odds-api.com/v4'
    def __init__(self, api_key=None, sport_key=None, regions='eu', markets='h2h,spreads,totals', timeout=10, session=None, min_interval=1.0):
        self.api_key=api_key or os.getenv('THE_ODDS_API_KEY','')
        self.sport_key=sport_key or os.getenv('THE_ODDS_API_SPORT_KEY','soccer_brazil_serie_a')
        self.regions=regions or os.getenv('THE_ODDS_API_REGIONS','eu')
        self.markets=markets or os.getenv('THE_ODDS_API_MARKETS','h2h,spreads,totals')
        self.timeout=timeout; self.session=session or requests.Session(); self.poller=ResilientPoller(); self.min_interval=float(min_interval); self._last_request=0.0
        self.health=ProviderHealth(self.name)
    @property
    def configured(self): return bool(self.api_key)
    def _get(self,path,params):
        if not self.configured: raise ProviderError("CREDENTIALS_UNAVAILABLE")
        wait=self.min_interval-(time.monotonic()-self._last_request)
        if wait>0: time.sleep(wait)
        last=None
        for attempt in range(4):
            started=time.monotonic(); self._last_request=time.monotonic(); self.health.requests+=1
            try:
                r=self.session.get(self.base_url+path,params={**params,"apiKey":self.api_key},timeout=self.timeout)
                self.health.last_latency_ms=round((time.monotonic()-started)*1000,2)
                self.health.last_status_code=r.status_code
                self.health.rate_limit_remaining=r.headers.get("x-requests-remaining")
                self.health.rate_limit_used=r.headers.get("x-requests-used")
                if r.status_code < 400:
                    self.health.status="ONLINE"; self.health.last_success=datetime.now(timezone.utc).isoformat(); self.health.last_error=None
                    return r
                msg=f"HTTP_{r.status_code}:{r.text[:200]}"
                # Retry only transient provider conditions. Never burn quota on auth/config errors.
                transient=r.status_code in (408,429) or r.status_code>=500
                if not transient: raise ProviderError(msg)
                last=ProviderError(msg)
                self.health.retry_count+=1
                retry_after=r.headers.get("Retry-After")
                try: delay=float(retry_after) if retry_after is not None else min(8.0,0.5*(2**attempt))
                except ValueError: delay=min(8.0,0.5*(2**attempt))
                time.sleep(delay)
            except (requests.Timeout,requests.ConnectionError) as e:
                last=e; self.health.retry_count+=1
                if attempt>=3: break
                time.sleep(min(8.0,0.5*(2**attempt)))
            except ProviderError as e:
                last=e; break
            except requests.RequestException as e:
                last=e; break
        self.health.failures+=1; self.health.status="OFFLINE"; self.health.last_error=str(last); raise ProviderError(str(last))

    def fetch_events_odds(self):
        r=self._get(f'/sports/{self.sport_key}/odds',{'regions':self.regions,'markets':self.markets,'oddsFormat':'decimal'})
        return r.json(), {'request_remaining':r.headers.get('x-requests-remaining'),'request_used':r.headers.get('x-requests-used')}
    def fetch_odds(self,event_id):
        r=self._get(f'/sports/{self.sport_key}/events/{event_id}/odds',{'regions':self.regions,'markets':self.markets,'oddsFormat':'decimal'}); return r.json()
    def fetch_scores(self,days_from=1):
        r=self._get(f'/sports/{self.sport_key}/scores',{'daysFrom':days_from}); return r.json()

def _valid_iso(value):
    if not value: return None
    try:
        dt=datetime.fromisoformat(str(value).replace('Z','+00:00'))
        return dt if dt.tzinfo else None
    except Exception: return None

def normalize_odds_api(events:list[dict[str,Any]], captured_at:datetime|None=None)->list[dict[str,Any]]:
    captured_at=captured_at or datetime.now(timezone.utc)
    if captured_at.tzinfo is None: raise ProviderDataQualityError('CAPTURED_AT_MUST_BE_TZ_AWARE')
    rows=[]
    for e in events:
        event_id=str(e.get('id','')); league=e.get('sport_title') or e.get('sport_key',''); home=e.get('home_team',''); away=e.get('away_team','')
        for bm in e.get('bookmakers',[]) or []:
            for market in bm.get('markets',[]) or []:
                source_ts=market.get('last_update') or bm.get('last_update')
                provider_dt=_valid_iso(source_ts)
                # Never substitute commence_time for source/update timestamp.
                for out in market.get('outcomes',[]) or []:
                    price=out.get('price')
                    if price is None or float(price)<=1: continue
                    if provider_dt is None: continue
                    row={'event_id':event_id,'event_name':f'{home} x {away}','home_team':home,'away_team':away,'league':league,'sport_key':e.get('sport_key'),'commence_time':e.get('commence_time'),'bookmaker':bm.get('key') or bm.get('title'),'market':market.get('key'),'selection':out.get('name'),'side':('HOME' if out.get('name')==home else 'AWAY' if out.get('name')==away else str(out.get('name'))),'line':out.get('point'),'odds':float(price),'available_at':provider_dt.isoformat(),'captured_at':captured_at.isoformat(),'source':'the_odds_api','source_timestamp':provider_dt.isoformat(),'raw_hash':canonical_hash(out)}
                    rows.append(row)
    return rows
