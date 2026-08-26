from __future__ import annotations
import math,statistics,random

def confidence_interval_mean(values,seed=42,iterations=4000):
    v=[float(x) for x in values if x is not None];n=len(v)
    if n<2:return {"status":"INSUFFICIENT_SAMPLE","n":n}
    rng=random.Random(seed);means=sorted(statistics.mean(rng.choice(v) for _ in v) for _ in range(iterations));return {"status":"OK","n":n,"mean":statistics.mean(v),"ci95":[means[int(.025*iterations)],means[int(.975*iterations)]]}

def calibration_metrics(rows):
    y=[];p=[]
    for r in rows:
        if r.get("outcome") is None or r.get("probability") is None:continue
        y.append(float(r["outcome"]));p.append(min(.999999,max(.000001,float(r["probability"]))))
    if len(y)<30:return {"status":"INSUFFICIENT_SAMPLE","n":len(y)}
    brier=sum((a-b)**2 for a,b in zip(y,p))/len(y);ll=-sum(a*math.log(b)+(1-a)*math.log(1-b) for a,b in zip(y,p))/len(y);return {"status":"OK","n":len(y),"brier":brier,"log_loss":ll}

def summary(dataset):
    rows=dataset.rows();settled=[r for r in rows if r.get("result") in {"WIN","LOSS"}];pnl=[float(r.get("pnl_units") or 0) for r in settled]
    return {"status":"NOT_DETERMINED" if len(settled)<100 else "EMPIRICAL_REVIEW","n":len(settled),"pnl_ci":confidence_interval_mean(pnl),"by_market":dataset.breakdown("market"),"by_league":dataset.breakdown("league"),"by_bookmaker":dataset.breakdown("bookmaker"),"edge_evidence":"NOT_DETERMINED" if len(settled)<100 else "REVIEW_REQUIRED"}
