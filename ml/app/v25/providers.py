from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime,timezone
@dataclass
class ProviderStatus:
    name:str;configured:bool=False;status:str='UNKNOWN';last_success:str|None=None;errors:int=0;latency_ms:float|None=None
class ProviderRegistry:
    def __init__(self):self.providers={}
    def register(self,provider):self.providers[provider.name]=provider;return provider
    def health(self):
        out={}
        for name,p in self.providers.items():
            h=getattr(p,'health',None);out[name]={"configured":bool(getattr(p,'configured',False)),"status":getattr(h,'status','UNKNOWN'),"last_success":getattr(h,'last_success',None),"errors":getattr(h,'failures',0),"latency_ms":getattr(h,'last_latency_ms',None)}
        return out
