from __future__ import annotations
from dataclasses import dataclass,asdict
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path
@dataclass
class Experiment:
    experiment_id:str; code_hash:str; dataset_hash:str; feature_version:str; model:str; hyperparameters:dict; markets:list; leagues:list; period:str; threshold:float|None; stake_policy:str; seed:int; result:dict; status:str='REGISTERED'; holdout_status:str='LOCKED'; created_at:str=''
    def __post_init__(self):
        if not self.created_at:self.created_at=datetime.now(timezone.utc).isoformat()

def make_id(payload): return hashlib.sha256(json.dumps(payload,sort_keys=True,default=str).encode()).hexdigest()[:20]

class ExperimentRegistry:
    def __init__(self,root='artifacts/experiments'): self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True)
    def register(self,experiment:Experiment):
        if experiment.holdout_status not in ('LOCKED','NOT_USED','FINAL_EVALUATION'):
            raise ValueError('INVALID_HOLDOUT_STATUS')
        p=self.root/f'{experiment.experiment_id}.json';
        if p.exists(): raise FileExistsError('EXPERIMENT_IMMUTABLE')
        p.write_text(json.dumps(asdict(experiment),indent=2,sort_keys=True,default=str),encoding='utf-8');return str(p)
    def list(self):
        return [json.loads(p.read_text()) for p in sorted(self.root.glob('*.json'))]
