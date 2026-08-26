from __future__ import annotations
import math
import pandas as pd

H005_ID='H005_CROSS_BOOK_DISPERSION_V1'


def evaluate_h005(df: pd.DataFrame, threshold: float=0.02) -> dict:
    d=df.copy()
    if d.empty:
        return {'hypothesis_id':H005_ID,'frozen_threshold':threshold,'eligible_bets':0,'net_units':0.0,'roi':None,'status':'NO_DATA'}
    d['odds']=pd.to_numeric(d['odds'],errors='coerce'); d['reference_odds']=pd.to_numeric(d['reference_odds'],errors='coerce')
    d['dispersion']=(d['odds']/d['reference_odds'])-1
    e=d[(d['pit_status']=='EXACT_PIT') & (d['dispersion']>=threshold) & (d['odds']>1)].copy()
    if e.empty:
        status='INSUFFICIENT_SAMPLE'
        return {'hypothesis_id':H005_ID,'frozen_threshold':threshold,'eligible_bets':0,'net_units':0.0,'roi':None,'status':status}
    e['profit_units']=e.apply(lambda r: r['odds']-1 if str(r.get('result')).upper()=='WIN' else -1 if str(r.get('result')).upper()=='LOSS' else 0,axis=1)
    net=float(e.profit_units.sum()); roi=net/len(e)
    status='INSUFFICIENT_SAMPLE' if len(e)<30 else 'RESEARCH_RESULT'
    return {'hypothesis_id':H005_ID,'frozen_threshold':threshold,'eligible_bets':int(len(e)),'net_units':net,'roi':roi,'status':status}


def bootstrap_roi(df: pd.DataFrame, n=2000, seed=15):
    if len(df)<2: return {'n':len(df),'ci95':None,'mean':None}
    import numpy as np
    rng=np.random.default_rng(seed); vals=df.to_numpy(dtype=float)
    means=[float(rng.choice(vals,size=len(vals),replace=True).mean()) for _ in range(n)]
    return {'n':len(df),'mean':float(np.mean(means)),'ci95':[float(np.quantile(means,.025)),float(np.quantile(means,.975))]}
