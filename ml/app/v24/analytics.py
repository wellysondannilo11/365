from __future__ import annotations
import math, statistics

def clv(entry_odds,closing_odds):
    if entry_odds and closing_odds and entry_odds>1 and closing_odds>1:
        return float(entry_odds/closing_odds-1)
    return None

def bootstrap_mean(values,iterations=2000,seed=42):
    vals=[float(x) for x in values if x is not None]
    if len(vals)<2:return {"status":"INSUFFICIENT_SAMPLE","n":len(vals)}
    import random
    rng=random.Random(seed);means=[]
    for _ in range(iterations):means.append(statistics.mean(rng.choice(vals) for _ in vals))
    means.sort();return {"status":"OK","n":len(vals),"mean":statistics.mean(vals),"ci95":[means[int(.025*len(means))],means[int(.975*len(means))-1]]}

def bucket(value,bounds):
    v=float(value)
    for lo,hi,name in bounds:
        if lo<=v<hi:return name
    return bounds[-1][2] if bounds else "UNKNOWN"
