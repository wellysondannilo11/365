from __future__ import annotations
import requests

class TheStatsAPIAdapter:
    name='thestatsapi'
    def __init__(self,key,base_url='https://api.thestatsapi.com',timeout=30):
        self.key=key; self.base_url=base_url.rstrip('/'); self.timeout=timeout
    def _get(self,path,**params):
        r=requests.get(f'{self.base_url}/{path.lstrip("/")}',params=params,headers={'Authorization':f'Bearer {self.key}','X-API-Key':self.key,'User-Agent':'RoboDaBet/V18'},timeout=self.timeout); r.raise_for_status(); return r.json()
    def matches(self,**params): return self._get('/api/football/matches',**params)
    def fixture(self,match_id,**params): return self._get(f'/api/football/matches/{match_id}',**params)
    def stats(self,match_id,**params): return self._get(f'/api/football/matches/{match_id}/stats',**params)
    def odds(self,match_id,**params): return self._get(f'/api/football/matches/{match_id}/odds',**params)
    def lineups(self,match_id,**params): return self._get(f'/api/football/matches/{match_id}/lineups',**params)
    def xg(self,match_id,**params): return self._get(f'/api/football/matches/{match_id}/xg',**params)
