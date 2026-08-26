from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

@dataclass(frozen=True)
class ProviderSpec:
    source_id: str
    base_url: str
    auth_env: str | None

class SportsDataProvider:
    spec: ProviderSpec
    def get_matches(self, **kwargs) -> Any: raise NotImplementedError
    def get_match_stats(self, **kwargs) -> Any: raise NotImplementedError
    def get_xg(self, **kwargs) -> Any: raise NotImplementedError
    def get_events(self, **kwargs) -> Any: raise NotImplementedError
    def get_players(self, **kwargs) -> Any: raise NotImplementedError
    def get_lineups(self, **kwargs) -> Any: raise NotImplementedError
    def get_injuries(self, **kwargs) -> Any: raise NotImplementedError
    def get_suspensions(self, **kwargs) -> Any: raise NotImplementedError
    def get_odds(self, **kwargs) -> Any: raise NotImplementedError
