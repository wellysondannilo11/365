from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping
import os

@dataclass(frozen=True)
class ProviderSpec:
    name: str
    base_url: str
    api_key_env: str | None = None

class SportsDataProvider:
    """Common adapter contract; implementations must preserve provider provenance."""
    def get_matches(self, **kwargs) -> Any: raise NotImplementedError
    def get_match_stats(self, **kwargs) -> Any: raise NotImplementedError
    def get_xg(self, **kwargs) -> Any: raise NotImplementedError
    def get_events(self, **kwargs) -> Any: raise NotImplementedError
    def get_players(self, **kwargs) -> Any: raise NotImplementedError
    def get_lineups(self, **kwargs) -> Any: raise NotImplementedError
    def get_injuries(self, **kwargs) -> Any: raise NotImplementedError
    def get_suspensions(self, **kwargs) -> Any: raise NotImplementedError
    def get_odds(self, **kwargs) -> Any: raise NotImplementedError

class StatsBombOpenDataProvider(SportsDataProvider):
    spec=ProviderSpec('statsbomb-open-data','https://raw.githubusercontent.com/statsbomb/open-data/master/data')
    def url(self, resource: str, *parts: str) -> str:
        return '/'.join([self.spec.base_url.rstrip('/'), resource, *[str(p).strip('/') for p in parts]])
    def get_matches(self, competition_id, season_id, **kwargs): return self.url('matches', competition_id, f'{season_id}.json')
    def get_events(self, match_id, **kwargs): return self.url('events', f'{match_id}.json')
    def get_lineups(self, match_id, **kwargs): return self.url('lineups', f'{match_id}.json')
    def get_players(self, **kwargs): return None  # player identity is embedded in events/lineups; no synthetic endpoint
    def get_xg(self, match_id, **kwargs): return self.get_events(match_id)

class ApiFootballProvider(SportsDataProvider):
    spec=ProviderSpec('api-football','https://v3.football.api-sports.io', 'API_FOOTBALL_KEY')
    def headers(self):
        key=os.getenv(self.spec.api_key_env or '')
        return {'x-apisports-key':key} if key else {}
    def endpoint(self, path, **params):
        from urllib.parse import urlencode
        q={k:v for k,v in params.items() if v is not None}
        return self.spec.base_url.rstrip('/')+'/'+path.lstrip('/')+('?' + urlencode(q) if q else '')
    def get_matches(self, **kwargs): return self.endpoint('/fixtures', **kwargs)
    def get_match_stats(self, **kwargs): return self.endpoint('/fixtures/statistics', **kwargs)
    def get_events(self, **kwargs): return self.endpoint('/fixtures/events', **kwargs)
    def get_lineups(self, **kwargs): return self.endpoint('/fixtures/lineups', **kwargs)
    def get_players(self, **kwargs): return self.endpoint('/players', **kwargs)
    def get_injuries(self, **kwargs): return self.endpoint('/injuries', **kwargs)
    def get_suspensions(self, **kwargs): return self.endpoint('/players/squads', **kwargs)
    def get_odds(self, **kwargs): return self.endpoint('/odds', **kwargs)

class OpenMeteoProvider(SportsDataProvider):
    spec=ProviderSpec('open-meteo','https://api.open-meteo.com/v1')
    def historical_url(self, latitude, longitude, start_date, end_date, **kwargs):
        from urllib.parse import urlencode
        q={'latitude':latitude,'longitude':longitude,'start_date':start_date,'end_date':end_date,'hourly':'temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,wind_direction_10m,surface_pressure,cloud_cover,visibility,weather_code'}
        return self.spec.base_url+'/forecast?'+urlencode(q)

class FootballDataFilesProvider(SportsDataProvider):
    spec=ProviderSpec('football-data.co.uk','https://www.football-data.co.uk')
    def season_csv(self, country_code: str, season_code: str) -> str:
        return f'{self.spec.base_url}/{season_code}/{country_code}.csv'
