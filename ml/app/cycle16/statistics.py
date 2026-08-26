from __future__ import annotations
import numpy as np, pandas as pd

def bootstrap_mean_ci(values,n=2000,seed=16):
    a=np.asarray(values,dtype=float); a=a[np.isfinite(a)]
    if len(a)==0:return {'n':0,'mean':None,'ci95':None}
    rng=np.random.default_rng(seed); means=rng.choice(a,size=(n,len(a)),replace=True).mean(axis=1)
    return {'n':len(a),'mean':float(a.mean()),'ci95':[float(np.quantile(means,.025)),float(np.quantile(means,.975))]}

def drawdown(values):
    a=np.asarray(values,dtype=float); eq=np.cumsum(a); peak=np.maximum.accumulate(np.r_[0,eq])[:-1]; return float(np.max(peak-eq)) if len(a) else 0.0

def execution_stress(df:pd.DataFrame, delays=(0,1,5,10,30), slippages=(0,0.005,0.01,0.02,0.03)):
    d=df.copy(); out=[]
    for delay in delays:
        for slip in slippages:
            odds=pd.to_numeric(d.entry_odds,errors='coerce')*(1-slip)
            pnl=[]
            for o,r,s in zip(odds,d.result,d.stake_units): pnl.append(float(s)*(float(o)-1) if str(r).upper()=='WIN' else -float(s) if str(r).upper()=='LOSS' else 0.0)
            net=float(np.nansum(pnl)); out.append({'delay_min':delay,'slippage_pct':slip*100,'net_units':net,'roi':net/len(pnl) if pnl else None})
    return {'base':out[0], 'grid':out}

def holm_bonferroni(pvalues,alpha=.05):
    p=np.asarray(pvalues,dtype=float); order=np.argsort(p); m=len(p); out=[None]*m; running=True
    for rank,idx in enumerate(order):
        adj=min(1.0,(m-rank)*p[idx]); reject=bool(running and p[idx] <= alpha/(m-rank))
        if not reject: running=False
        out[idx]={'raw_p':float(p[idx]),'adjusted_p':float(adj),'reject':reject,'rank':rank+1}
    return out
