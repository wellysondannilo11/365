from __future__ import annotations
from .http_provider import HttpProvider
from .provider_base import ProviderSpec
from urllib.parse import urlencode

class OpenMeteoProvider(HttpProvider):
    def __init__(self, daily_limit=10000, rpm=60):
        super().__init__(ProviderSpec('open-meteo','https://archive-api.open-meteo.com/v1/archive',None),daily_limit,rpm)
    def get_historical_weather(self, latitude, longitude, start_date, end_date, hourly=None, daily=None, timezone='UTC'):
        params={'latitude':latitude,'longitude':longitude,'start_date':start_date,'end_date':end_date,'timezone':timezone}
        if hourly: params['hourly']=','.join(hourly)
        if daily: params['daily']=','.join(daily)
        raw, headers=self._request(self.spec.base_url+'?'+urlencode(params))
        return raw, headers
