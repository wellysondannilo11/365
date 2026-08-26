from __future__ import annotations
import json, sys
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'ml'))
from app.research.data_quality_v16 import profile
from app.v18.lineage import manifest, save_manifest

# Fail closed: only a strict PIT dataset can enter the betting research path.
candidates=list((ROOT/'data/research/v18').glob('*.csv')) + list((ROOT/'data/research/v18').glob('*.parquet'))
report={'version':'V18','status':'BLOCKED','reason':'NO_STRICT_PIT_RESEARCH_DATASET','real_backtest':False,'real_oos':False,'real_roi':None,'real_clv':None,'dataset':None}
if candidates:
    path=candidates[0]; df=pd.read_parquet(path) if path.suffix=='.parquet' else pd.read_csv(path)
    q=profile(df); report['dataset_quality']=q
    if q['status']=='PASS' and {'available_at','decision_time','source_timestamp'}.issubset(df.columns):
        report['status']='ELIGIBLE_FOR_RESEARCH'; report['dataset']=manifest(df,'local_research_dataset')
        save_manifest(report['dataset'],ROOT/'reports/v18/V18_DATASET_MANIFEST.json')
report['demo_rows']=int(pd.read_csv(ROOT/'data.csv').shape[0])
(ROOT/'reports/v18/V18_RESEARCH_EXECUTION.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
print(json.dumps(report,indent=2,default=str))
