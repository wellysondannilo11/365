from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json

@dataclass(frozen=True)
class PaperSignal:
    event_id:str; signal_time:str; market:str; selection:str; odds:float; probability:float; ev:float; stake:float; decision:str; model_version:str; dataset_version:str

class PaperLedger:
    def __init__(self,path='artifacts/paper_trading/signals.jsonl'):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def append(self,signal:PaperSignal):
        with self.path.open('a',encoding='utf-8') as f:f.write(json.dumps(asdict(signal),sort_keys=True)+'\n')
        return asdict(signal)
