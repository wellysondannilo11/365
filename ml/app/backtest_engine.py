from __future__ import annotations
from dataclasses import dataclass,asdict
import numpy as np,pandas as pd
from .market import fair_odds,edge,ev
from .research.statistics import block_bootstrap
from .research.metrics import betting_metrics

@dataclass
class BetRecord:
    event_id:str; decision_time:str; market:str|None; selection:str|None; bookmaker:str|None
    odds:float; probability:float; implied_probability:float; fair_probability:float; edge:float; stake:float
    result:int; pnl:float; ev:float; clv:float|None

def simulate(df,prob_col='probability',odds_col='odds',result_col='result',min_odds=1.6,min_edge=.05,stake_policy='fixed',unit=.5,bankroll=50,closing_col='closing_odds',decision_col='decision_time'):
    d=df.copy(); required={prob_col,odds_col,result_col,'event_id',decision_col}
    missing=required-set(d.columns)
    if missing: raise ValueError(f'MISSING_BACKTEST_COLUMNS:{sorted(missing)}')
    d=d.sort_values([decision_col,'event_id'],kind='stable'); bank=float(bankroll); rows=[]
    for _,r in d.iterrows():
        o=float(r[odds_col]); p=float(r[prob_col]); actual=int(r[result_col])
        if not (0<p<1) or o<=1: continue
        if o<min_odds or p*o-1<min_edge: continue
        stake=float(unit)
        if stake_policy=='kelly':
            b=o-1; k=max(0,(b*p-(1-p))/b)*.25; stake=min(2,max(0,k*bank))
        if stake<=0: continue
        pnl=stake*(o-1) if actual else -stake; bank+=pnl; clv=None
        if closing_col in r and pd.notna(r[closing_col]):
            close=float(r[closing_col]);
            if close>1: clv=o/close-1
        rows.append(asdict(BetRecord(str(r.event_id),str(r[decision_col]),str(r.get('market')) if pd.notna(r.get('market')) else None,str(r.get('selection')) if pd.notna(r.get('selection')) else None,str(r.get('bookmaker')) if pd.notna(r.get('bookmaker')) else None,o,p,1/o,p,p-1/o,stake,actual,pnl,p*o-1,clv)))
    metrics=betting_metrics(rows,bankroll=bankroll)
    if not rows: return {**metrics,'bootstrap':None,'records':[]}
    x=pd.DataFrame(rows)
    return {**metrics,'avg_ev':float(x.ev.mean()),'bootstrap':block_bootstrap(x.pnl.to_numpy()),'records':rows}
