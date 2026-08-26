from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json
from datetime import datetime, timezone

@dataclass(frozen=True)
class Experiment:
    experiment_id: str
    hypothesis: str
    baseline: str
    change: str
    dataset: str
    train_period: str
    validation_period: str
    oos_period: str
    metrics: dict
    result: str
    promotion_status: str
    created_at: str

class ExperimentRegistry:
    def __init__(self, path='artifacts/v16/experiments.jsonl'):
        self.path=Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
    def record(self, *, experiment_id, hypothesis, baseline, change, dataset, train_period='', validation_period='', oos_period='', metrics=None, result='', promotion_status='RESEARCH_ONLY'):
        e=Experiment(experiment_id,hypothesis,baseline,change,dataset,train_period,validation_period,oos_period,metrics or {},result,promotion_status,datetime.now(timezone.utc).isoformat())
        with self.path.open('a',encoding='utf-8') as f: f.write(json.dumps(asdict(e),sort_keys=True)+'\n')
        return asdict(e)
