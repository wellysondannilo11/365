from __future__ import annotations
from .http_provider import HttpProvider
from .provider_base import ProviderSpec
class StatsBombOpenProvider(HttpProvider):
    def __init__(self): super().__init__(ProviderSpec('statsbomb-open-data','https://raw.githubusercontent.com/statsbomb/open-data/master/data',None),0,0)
    def url(self, path): return self.spec.base_url.rstrip('/')+'/'+path.lstrip('/')
    def get_competitions(self): return self._request(self.url('competitions.json'))
    def get_matches(self, competition_id, season_id): return self._request(self.url(f'matches/{competition_id}/{season_id}.json'))
    def get_events(self, match_id): return self._request(self.url(f'events/{match_id}.json'))
    def get_lineups(self, match_id): return self._request(self.url(f'lineups/{match_id}.json'))
