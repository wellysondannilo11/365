from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import pandas as pd, json, hashlib
from ml.app.research.empirical import run_real_research
from ml.app.research.data_quality_v16 import profile
root=ROOT
df=pd.read_csv(root/'data.csv')
# DEMO fixture is explicitly not promoted to real research evidence.
q=profile(df.assign(event_id=[f'demo-{i}' for i in range(len(df))],event_time=pd.to_datetime(df.kickoff,utc=True),decision_time=pd.to_datetime(df.kickoff,utc=True),available_at=pd.to_datetime(df.kickoff,utc=True)))
report={'status':'BLOCKED','reason':'ONLY_DEMO_ROWS_PRESENT','events':int(len(df)),'quality':q,'real_backtest':False,'real_oos':False,'real_roi':None,'real_clv':None}
path=root/'reports/v17/V17_RESEARCH_EXECUTION.json'; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8'); print(json.dumps(report,indent=2,default=str))
