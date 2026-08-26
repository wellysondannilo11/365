from __future__ import annotations
import requests

class StatsBombOpenDataAdapter:
    name='statsbomb-open-data'
    base='https://raw.githubusercontent.com/statsbomb/open-data/master/data'
    def __init__(self,timeout=30): self.timeout=timeout
    def competitions(self): return self._get('competitions.json')
    def matches(self,competition_id,season_id): return self._get(f'matches/{competition_id}/{season_id}.json')
    def events(self,match_id): return self._get(f'events/{match_id}.json')
    def lineups(self,match_id): return self._get(f'lineups/{match_id}.json')
    def _get(self,path):
        r=requests.get(f'{self.base}/{path}',timeout=self.timeout,headers={'User-Agent':'RoboDaBet-research/14.1'}); r.raise_for_status(); return r.json()
