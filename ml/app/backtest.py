from __future__ import annotations
import pandas as pd, numpy as np
from .models import calibration_metrics

def temporal_splits(df, train_frac=.5, validation_frac=.2, gap=0, holdout_frac=.15):
    n=len(df); train_end=int(n*train_frac); val_end=int(n*(train_frac+validation_frac)); hold_start=int(n*(1-holdout_frac))
    if hold_start<=val_end: hold_start=val_end+1
    return {'train':(0,train_end),'validation':(train_end+gap,val_end),'test':(val_end+gap,hold_start),'final_holdout':(hold_start,n)}

def walk_forward(df, feature_cols, label_col, odds_col, min_odds=1.6, min_train=50, gap=0, embargo=0):
    df=df.sort_values('kickoff').reset_index(drop=True); rows=[]
    for i in range(min_train,len(df)):
        train_end=max(0,i-gap-embargo); train=df.iloc[:train_end]; test=df.iloc[i:i+1]
        if train.empty or float(test.iloc[0][odds_col])<min_odds: continue
        y=train[label_col].astype(int); p=float(y.mean()); odd=float(test.iloc[0][odds_col]); actual=int(test.iloc[0][label_col]); stake=.5
        pnl=stake*(odd-1) if actual else -stake
        rows.append({'index':i,'probability':p,'odds':odd,'result':actual,'pnl':pnl,'ev':p*odd-1})
    out=pd.DataFrame(rows)
    if out.empty:return {'bets':0,'pnl':0,'roi':0,'yield':0,'avg_ev':0,'final_holdout_protected':True}
    return {'bets':len(out),'pnl':float(out.pnl.sum()),'roi':float(out.pnl.sum()/50),'yield':float(out.pnl.sum()/(len(out)*.5)),'avg_ev':float(out.ev.mean()),'final_holdout_protected':True}

def ablation_report(results):
    # results: {name: {'y':...,'p':...,'clv':...,'roi':...}}
    out={}
    for name,r in results.items():
        metrics=calibration_metrics(r['y'],r['p'])
        out[name]={**metrics,'clv':r.get('clv'),'roi':r.get('roi'),'drawdown':r.get('drawdown')}
    return out
