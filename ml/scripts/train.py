import argparse,json,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pathlib import Path
import pandas as pd,numpy as np
from app.layer_training import ThreeLayerTrainer
from app.leakage import validate_temporal_dataset
from app.mlops.registry import ModelRegistry

def prepare(df,allow_demo=False):
 df=df.sort_values('kickoff').reset_index(drop=True)
 required={'event_id','decision_time','available_at','event_time','source_time','ingested_at'}
 if not required.issubset(df.columns):
  if not allow_demo:raise ValueError('REAL_TRAINING_REQUIRES_POINT_IN_TIME_COLUMNS')
  df['event_id']=np.arange(len(df)).astype(str);df['event_time']=pd.to_datetime(df['kickoff'],utc=True);df['decision_time']=df['event_time']-pd.Timedelta(hours=1);df['available_at']=df['decision_time'];df['source_time']=df['decision_time'];df['ingested_at']=df['decision_time']
 validate_temporal_dataset(df);return df

def main():
 p=argparse.ArgumentParser();p.add_argument('--csv',required=True);p.add_argument('--market',default='GENERIC');p.add_argument('--allow-demo-synthetic-timestamps',action='store_true');a=p.parse_args();df=prepare(pd.read_csv(a.csv),a.allow_demo_synthetic_timestamps)
 sport=['home_xg','away_xg','home_elo','away_elo','home_form','away_form'];market=['odds']
 if len(df)<8:raise SystemExit('INSUFFICIENT_DATA_FOR_SERIOUS_TRAINING')
 result=ThreeLayerTrainer().fit(df,sport,market);rid=hashlib.sha256((str(len(df))+a.market).encode()).hexdigest()[:16]
 meta={'run_id':rid,'market':a.market,'layers':{k:{'metrics':v.metrics,'features':v.feature_names,'oos_sample':len(v.probability)} for k,v in result.items()},'rows':len(df),'point_in_time_validated':True,'final_holdout_used':False,'status':'CHALLENGER'}
 ModelRegistry().register('challenger',meta);print(json.dumps(meta,indent=2))
if __name__=='__main__':main()
