from __future__ import annotations
import numpy as np
import pandas as pd
from .statistics import cluster_bootstrap


def group_performance(records: pd.DataFrame, group_cols=('season','league','market','odds_bucket','edge_bucket')) -> dict:
    d=records.copy()
    if d.empty:return {}
    out={}
    for c in group_cols:
        if c not in d.columns: continue
        rows=[]
        for key,g in d.groupby(c,dropna=False):
            stake=float(g.stake.sum()) if 'stake' in g else 0.0
            profit=float(g.pnl.sum()) if 'pnl' in g else 0.0
            rows.append({'group':str(key),'bets':len(g),'events':g.event_id.astype(str).nunique(),'profit':profit,'stake':stake,'roi':profit/stake if stake else None,'clv':float(g.clv.dropna().mean()) if 'clv' in g and g.clv.notna().any() else None})
        out[c]=rows
    return out


def sensitivity(records: pd.DataFrame, thresholds=(0.02,0.03,0.05,0.07,0.10)) -> list[dict]:
    d=records.copy(); out=[]
    if 'ev' not in d: return out
    for t in thresholds:
        g=d[d.ev.astype(float)>=t]
        stake=float(g.stake.sum()) if 'stake' in g else 0.0; profit=float(g.pnl.sum()) if 'pnl' in g else 0.0
        out.append({'threshold':t,'bets':len(g),'events':g.event_id.astype(str).nunique() if len(g) else 0,'roi':profit/stake if stake else None})
    return out
