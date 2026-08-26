from __future__ import annotations
import numpy as np
import pandas as pd
from .calibration import calibration_report
from .statistics import cluster_bootstrap


def betting_metrics(records, bankroll=100.0):
    if not records:
        return {'bets':0,'profit':0.0,'yield':0.0,'roi':0.0,'bankroll_return':0.0,'hit_rate':None,'max_drawdown':0.0,'volatility':None,'sharpe_like':None,'sortino_like':None,'avg_odds':None,'clv':None,'roi_ci':None}
    d=pd.DataFrame(records); pnl=d.pnl.astype(float); stake=d.stake.astype(float)
    equity=bankroll+pnl.cumsum(); peak=equity.cummax(); dd=peak-equity
    ret=pnl/stake.replace(0,np.nan)
    vol=float(ret.std(ddof=1)) if len(ret)>1 else None
    sharpe=float(ret.mean()/vol*np.sqrt(len(ret))) if vol and vol>0 else None
    downside=ret[ret<0].std(ddof=1) if (ret<0).sum()>1 else None
    sortino=float(ret.mean()/downside*np.sqrt(len(ret))) if downside and downside>0 else None
    total_stake=float(stake.sum()); profit=float(pnl.sum())
    roi=profit/total_stake if total_stake else 0.0
    cluster=cluster_bootstrap(d[['event_id','pnl','stake']],iterations=2000,seed=42)
    return {'bets':int(len(d)),'profit':profit,'yield':roi,'roi':roi,'bankroll_return':float(profit/bankroll) if bankroll else None,'hit_rate':float(d.result.mean()),'max_drawdown':float(dd.max()),'volatility':vol,'sharpe_like':sharpe,'sortino_like':sortino,'avg_odds':float(d.odds.mean()),'clv':float(d.clv.dropna().mean()) if d.clv.notna().any() else None,'roi_ci':cluster['roi_ci']}


def prediction_metrics(y,p):
    y=np.asarray(y); p=np.clip(np.asarray(p,float),1e-9,1-1e-9)
    r=calibration_report(y,p)
    if len(p)>=2:
        try:
            x=np.log(p/(1-p)); z=np.polyfit(x,y,1); slope=float(z[0]); intercept=float(z[1])
        except Exception: slope=intercept=None
    else: slope=intercept=None
    return {**r,'calibration_slope':slope,'calibration_intercept':intercept,'n':int(len(p))}
