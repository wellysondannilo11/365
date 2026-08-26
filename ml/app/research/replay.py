from __future__ import annotations
import json,hashlib
from pathlib import Path

def decision_hash(snapshot):
    payload=json.dumps(snapshot,sort_keys=True,default=str,separators=(',',':'))
    return hashlib.sha256(payload.encode()).hexdigest()

def replay(snapshot, feature_builder, model_fn):
    decision_time=snapshot['decision_time'];features=feature_builder(snapshot,decision_time)
    prediction=model_fn(features)
    result={'decision_id':snapshot['decision_id'],'features':features,'prediction':prediction}
    result['replay_hash']=decision_hash(result);return result
