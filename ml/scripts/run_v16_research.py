from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
from ml.app.research.data_quality_v16 import profile
from ml.app.research.empirical import build_real_features, run_real_research, dataset_fingerprint

p=argparse.ArgumentParser()
p.add_argument('--input',required=True)
p.add_argument('--out',default='artifacts/v16_research')
p.add_argument('--label',default='label')
p.add_argument('--features',default='')
p.add_argument('--min-train',type=int,default=100)
p.add_argument('--validation',type=int,default=30)
p.add_argument('--test',type=int,default=30)
p.add_argument('--holdout',type=float,default=.15)
a=p.parse_args()
out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
d=pd.read_csv(a.input)
q=profile(d); (out/'data_quality.json').write_text(json.dumps(q,indent=2,default=str),encoding='utf-8')
if q['status']!='PASS': raise SystemExit('DATA_QUALITY_GATE_FAILED')
if {'home_team','away_team','event_id','event_time','decision_time','available_at','outcome_available_at','home_goals','away_goals'}.issubset(d.columns):
    feats,lineage=build_real_features(d)
    feats.to_parquet(out/'features.parquet',index=False)
    lineage.to_json(out/'feature_lineage.json',orient='records',date_format='iso')
    d=d.merge(feats,on=['event_id','event_time','decision_time'],how='inner')
features=[x for x in a.features.split(',') if x] if a.features else [c for c in d.columns if c.startswith(('elo_','home_','away_')) and d[c].dtype.kind in 'biufc']
features=[c for c in features if c in d.columns]
if a.label not in d.columns: raise SystemExit(f'MISSING_LABEL:{a.label}')
r=run_real_research(d,features,a.label,a.min_train,a.validation,a.test,a.holdout)
result={'dataset_hash':dataset_fingerprint(d),'quality':q,'features':features,'result':r.__dict__}
(out/'empirical_result.json').write_text(json.dumps(result,indent=2,default=str),encoding='utf-8')
print(json.dumps(result,indent=2,default=str))
