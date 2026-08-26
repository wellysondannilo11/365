from __future__ import annotations
import os
from .http_provider import HttpProvider
from .provider_base import ProviderSpec
class ApiFootballProvider(HttpProvider):
    def __init__(self, daily_limit=100, rpm=10):
        super().__init__(ProviderSpec('api-football','https://v3.football.api-sports.io', 'API_FOOTBALL_KEY'),daily_limit,rpm)
    def _h(self):
        key=os.getenv('API_FOOTBALL_KEY')
        if not key: raise RuntimeError('API_FOOTBALL_KEY not configured')
        return {'x-apisports-key':key,'User-Agent':'RoboDaBet-FreeAcquisition/3.0'}
    def get_matches(self, **params): return self._request(self.spec.base_url+'/fixtures?'+__import__('urllib.parse').parse.urlencode(params),headers=self._h())
    def get_match_stats(self, **params): return self._request(self.spec.base_url+'/fixtures/statistics?'+__import__('urllib.parse').parse.urlencode(params),headers=self._h())
    def get_events(self, **params): return self._request(self.spec.base_url+'/fixtures/events?'+__import__('urllib.parse').parse.urlencode(params),headers=self._h())
    def get_players(self, **params): return self._request(self.spec.base_url+'/players?'+__import__('urllib.parse').parse.urlencode(params),headers=self._h())
    def get_lineups(self, **params): return self._request(self.spec.base_url+'/fixtures/lineups?'+__import__('urllib.parse').parse.urlencode(params),headers=self._h())
    def get_injuries(self, **params): return self._request(self.spec.base_url+'/injuries?'+__import__('urllib.parse').parse.urlencode(params),headers=self._h())
    def get_odds(self, **params): return self._request(self.spec.base_url+'/odds?'+__import__('urllib.parse').parse.urlencode(params),headers=self._h())
