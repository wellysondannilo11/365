from __future__ import annotations
import json, os, time, urllib.error, urllib.request
from pathlib import Path
from .provider_base import SportsDataProvider, ProviderSpec

class HttpProvider(SportsDataProvider):
    def __init__(self, spec: ProviderSpec, daily_limit=0, rpm=0):
        self.spec=spec; self.daily_limit=int(daily_limit); self.rpm=int(rpm); self.counter=0; self._last=0.0
    def _request(self, url, headers=None, timeout=30):
        if self.daily_limit and self.counter >= self.daily_limit: raise RuntimeError(f'{self.spec.source_id}: daily free limit reached')
        if self.rpm:
            min_gap=60.0/self.rpm
            wait=min_gap-(time.monotonic()-self._last)
            if wait>0: time.sleep(wait)
        req=urllib.request.Request(url,headers=headers or {'User-Agent':'RoboDaBet-FreeAcquisition/3.0'})
        self.counter += 1; self._last=time.monotonic()
        with urllib.request.urlopen(req,timeout=timeout) as r: return r.read(), dict(r.headers)
    def save_json(self, url, dest: Path, headers=None):
        raw, meta=self._request(url,headers=headers); dest.parent.mkdir(parents=True,exist_ok=True); tmp=dest.with_suffix(dest.suffix+'.part'); tmp.write_bytes(raw); tmp.replace(dest); return meta
