from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.stats import norm

def block_bootstrap(values,iterations=2000,block=10,seed=42):
    x=np.asarray(values,float); n=len(x)
    if n==0:return {'estimate':0,'ci_low':0,'ci_high':0,'n':0}
    rng=np.random.default_rng(seed);stats=[]
    block=max(1,min(block,n)); starts=np.arange(n)
    for _ in range(iterations):
        sample=[]
        while len(sample)<n:
            s=int(rng.choice(starts));sample.extend(x[(s+np.arange(block))%n])
        stats.append(np.mean(sample[:n]))
    q=np.quantile(stats,[.025,.975]);return {'estimate':float(np.mean(x)),'ci_low':float(q[0]),'ci_high':float(q[1]),'n':n}

def holm(pvalues):
    p=np.asarray(pvalues,float);order=np.argsort(p);adj=np.empty(len(p));m=len(p)
    running=0
    for rank,idx in enumerate(order):
        val=min(1,(m-rank)*p[idx]);running=max(running,val);adj[idx]=running
    return adj.tolist()

def deflated_sharpe(sharpe,n_trials,n_obs):
    if n_obs<2:return None
    # Conservative multiple-testing adjustment using expected max Sharpe approximation.
    emax=norm.ppf(max(1-1/max(n_trials,1),1e-12))/np.sqrt(n_obs)
    return float(sharpe-emax)

def bootstrap_ci(values, stat='mean', iterations=2000, seed=42, block=10):
    x=np.asarray(values,float)
    if len(x)==0: return {'estimate':None,'ci_low':None,'ci_high':None,'n':0}
    rng=np.random.default_rng(seed); n=len(x); block=max(1,min(block,n)); vals=[]
    for _ in range(iterations):
        sample=[]
        while len(sample)<n:
            start=int(rng.integers(0,n)); sample.extend(x[(start+np.arange(block))%n])
        z=np.asarray(sample[:n]); vals.append(float(np.mean(z)))
    q=np.quantile(vals,[.025,.975]); return {'estimate':float(np.mean(x)),'ci_low':float(q[0]),'ci_high':float(q[1]),'n':n,'iterations':iterations}


def cluster_bootstrap(frame, iterations=2000, seed=42):
    """Bootstrap betting returns by event, preserving dependence among bets in one event."""
    required={'event_id','pnl','stake'}
    if not required.issubset(frame.columns):
        raise ValueError(f'MISSING_CLUSTER_BOOTSTRAP_COLUMNS:{sorted(required-set(frame.columns))}')
    d=frame.copy(); groups=[g for _,g in d.groupby(d.event_id.astype(str),sort=False)]
    if not groups:return {'estimate':0.0,'ci_low':0.0,'ci_high':0.0,'roi_ci':{'low':0.0,'high':0.0},'events':0}
    rng=np.random.default_rng(seed); rois=[]
    for _ in range(iterations):
        sample=rng.integers(0,len(groups),len(groups)); s=pd.concat([groups[i] for i in sample],ignore_index=True)
        denom=float(s.stake.sum()); rois.append(float(s.pnl.sum()/denom) if denom else 0.0)
    observed=float(d.pnl.sum()/d.stake.sum()) if d.stake.sum() else 0.0
    q=np.quantile(rois,[.025,.975])
    return {'estimate':observed,'ci_low':float(q[0]),'ci_high':float(q[1]),'roi_ci':{'low':float(q[0]),'high':float(q[1])},'events':len(groups),'iterations':iterations}
