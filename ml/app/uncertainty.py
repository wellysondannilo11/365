import numpy as np

def ensemble_uncertainty(probabilities):
    p=np.asarray(probabilities,dtype=float)
    if p.ndim==1:return float(np.std(p)),max(0.,1-2*float(np.std(p)))
    s=p.std(axis=0); return s,float(np.clip(1-2*s,0,1).mean())

def bootstrap_interval(y,p,iterations=300,seed=42):
    rng=np.random.default_rng(seed); y=np.asarray(y);p=np.asarray(p); stats=[]
    for _ in range(iterations):
        idx=rng.integers(0,len(y),len(y)); stats.append(float(np.mean((p[idx]-.5)*(2*y[idx]-1))))
    return tuple(np.quantile(stats,[.025,.975]))
