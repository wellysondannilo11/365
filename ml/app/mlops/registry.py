import json,hashlib
from pathlib import Path
class ModelRegistry:
 def __init__(self,root='artifacts/registry'):self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True)
 def register(self,model_id,metadata):
  payload=json.dumps(metadata,sort_keys=True,default=str).encode();m=dict(metadata);m['metadata_hash']=hashlib.sha256(payload).hexdigest();p=self.root/f'{model_id}.json';p.write_text(json.dumps(m,indent=2,default=str));return str(p)
 def load(self,model_id):return json.loads((self.root/f'{model_id}.json').read_text())
 def promote(self,champion,challenger,min_sample=100):
  if challenger.get('final_holdout_used'):raise ValueError('FINAL_HOLDOUT_MUST_REMAIN_LOCKED')
  ok=challenger.get('oos',{}).get('logloss',999)<champion.get('oos',{}).get('logloss',999) and challenger.get('oos_sample',0)>=min_sample
  return ok
