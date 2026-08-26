from __future__ import annotations
import hashlib,json
from datetime import datetime,timezone

def raw_hash(payload):
    return hashlib.sha256(json.dumps(payload,sort_keys=True,default=str,separators=(',',':')).encode()).hexdigest()

def immutable_record(provider,endpoint,payload,event_id=None,source_time=None,available_at=None):
    if source_time is None or available_at is None:
        raise ValueError('REAL_RAW_RECORD_REQUIRES_PROVIDER_TIMESTAMPS')
    now=datetime.now(timezone.utc)
    return {'provider':provider,'endpoint':endpoint,'event_id':event_id,'source_time':source_time,'available_at':available_at,'ingested_at':now,'raw_hash':raw_hash(payload),'payload':payload}
