from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

FIELDS=('event_id','league','season','commence_time','event_name','market','selection','bookmaker','odds','fair_probability','fair_odds','market_probability','edge','ev','confidence','minute','home_goals','away_goals','decision','mode','decision_time','result','pnl_units','clv','model_version','feature_version','dataset_hash','data_snapshot_id','reason')
class ResearchDataset:
    def __init__(self,path='data/research/robo_bet_dataset_v23.jsonl'):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def append(self,record):
        row={k:record.get(k) for k in FIELDS}; row.update({k:v for k,v in record.items() if k not in row}); row.setdefault('created_at',datetime.now(timezone.utc).isoformat())
        prior=self._last_hash(); row['prev_hash']=prior
        raw=json.dumps(row,sort_keys=True,separators=(',',':'),default=str); row['row_hash']=hashlib.sha256(raw.encode()).hexdigest()
        with self.path.open('a',encoding='utf-8') as f:f.write(json.dumps(row,sort_keys=True,default=str)+'\n')
        return row
    def _last_hash(self):
        if not self.path.exists(): return None
        last=None
        with self.path.open(encoding='utf-8') as f:
            for line in f:
                if line.strip(): last=json.loads(line).get('row_hash')
        return last
    def rows(self): return [json.loads(x) for x in self.path.read_text(encoding='utf-8').splitlines() if x.strip()] if self.path.exists() else []
    def stats(self):
        rows=self.rows(); decisions=[r.get('decision') for r in rows]; return {'rows':len(rows),'bets':decisions.count('BET'),'no_bets':decisions.count('NO BET'),'paper':sum(r.get('mode')=='PAPER' for r in rows),'shadow':sum(r.get('mode')=='SHADOW' for r in rows),'path':str(self.path)}
