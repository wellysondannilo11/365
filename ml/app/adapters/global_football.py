from __future__ import annotations
import os, time
from dataclasses import dataclass
from typing import Any
import requests

@dataclass
class FetchResult:
    provider:str; url:str; status:str; http_status:int|None; captured_at:str; bytes:int; reason:str; payload:Any=None

class BaseFootballProvider:
    name='base'
    def __init__(self, timeout=15): self.timeout=timeout
    def _get(self,url,**kwargs):
        started=time.perf_counter(); r=requests.get(url,timeout=self.timeout,headers={'User-Agent':'RoboDaBet/GlobalFootballResearch/1.0'},**kwargs); r.raise_for_status(); return r, (time.perf_counter()-started)*1000

class TheOddsAPIProvider(BaseFootballProvider):
    name='the-odds-api'
    base='https://api.the-odds-api.com/v4'
    def __init__(self,key=None,timeout=15): super().__init__(timeout); self.key=key or os.getenv('THE_ODDS_API_KEY')
    @property
    def configured(self): return bool(self.key)
    def odds(self,sport_key='soccer_epl',regions='eu',markets='h2h,spreads,totals'):
        if not self.key: raise RuntimeError('THE_ODDS_API_KEY_MISSING')
        r,_=self._get(f'{self.base}/sports/{sport_key}/odds',params={'apiKey':self.key,'regions':regions,'markets':markets,'oddsFormat':'decimal'})
        return r.json()
    def scores(self,sport_key='soccer_epl',days_from=1):
        if not self.key: raise RuntimeError('THE_ODDS_API_KEY_MISSING')
        r,_=self._get(f'{self.base}/sports/{sport_key}/scores',params={'apiKey':self.key,'daysFrom':days_from})
        return r.json()

class APIFootballProvider(BaseFootballProvider):
    name='api-football'
    base='https://v3.football.api-sports.io'
    def __init__(self,key=None,timeout=15): super().__init__(timeout); self.key=key or os.getenv('API_FOOTBALL_KEY')
    @property
    def configured(self): return bool(self.key)
    def _api(self,path,**params):
        if not self.key: raise RuntimeError('API_FOOTBALL_KEY_MISSING')
        r,_=self._get(f'{self.base}/{path.lstrip("/")}',headers={'x-apisports-key':self.key},params=params); return r.json()
    def live_fixtures(self): return self._api('fixtures',live='all')
    def fixture(self,fixture_id): return self._api('fixtures',id=fixture_id)
    def fixture_events(self,fixture_id): return self._api('fixtures/events',fixture=fixture_id)
    def fixture_statistics(self,fixture_id): return self._api('fixtures/statistics',fixture=fixture_id)

class SportmonksProvider(BaseFootballProvider):
    name='sportmonks'
    base='https://api.sportmonks.com/v3/football'
    def __init__(self,token=None,timeout=15): super().__init__(timeout); self.token=token or os.getenv('SPORTMONKS_API_TOKEN')
    @property
    def configured(self): return bool(self.token)
    def _api(self,path,**params):
        if not self.token: raise RuntimeError('SPORTMONKS_API_TOKEN_MISSING')
        params={'api_token':self.token,**params}
        r,_=self._get(f'{self.base}/{path.lstrip("/")}',params=params); return r.json()
    def livescores(self,includes='statistics;events'): return self._api('livescores',include=includes)
    def fixture(self,fixture_id,includes='statistics;events;lineups'): return self._api(f'fixtures/{fixture_id}',include=includes)
