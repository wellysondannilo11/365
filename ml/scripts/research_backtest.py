import argparse,json,pandas as pd
from ml.app.backtest_engine import simulate
p=argparse.ArgumentParser();p.add_argument('--csv',required=True);p.add_argument('--probability',default='probability');p.add_argument('--odds',default='odds');p.add_argument('--result',default='result');a=p.parse_args();df=pd.read_csv(a.csv);print(json.dumps(simulate(df,a.probability,a.odds,a.result),indent=2,default=str))
