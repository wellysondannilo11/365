from __future__ import annotations
import hashlib, json
import numpy as np
import pandas as pd

def create_paper_bets(df:pd.DataFrame)->pd.DataFrame:
    d=df[df.pit_status.eq('EXACT_PIT')].copy()
    if d.empty: return d.copy()
    if 'decision_id' not in d: d['decision_id']=[hashlib.sha256(f"{r.event_id}|{r.entry_timestamp}|{r.entry_odds}|{r.hypothesis_id}".encode()).hexdigest() for r in d.itertuples()]
    d['stake_units']=pd.to_numeric(d.get('stake_units',1.0),errors='coerce').fillna(1.0)
    return d

def settle_paper_bets(df:pd.DataFrame)->pd.DataFrame:
    d=df.copy()
    def p(r):
        res=str(r.get('result','')).upper(); stake=float(r.get('stake_units',1))
        if res=='WIN': return stake*(float(r.entry_odds)-1)
        if res=='LOSS': return -stake
        if res in {'VOID','PUSH'}: return 0.0
        return np.nan
    d['profit_units']=d.apply(p,axis=1); return d

def calculate_real_clv(df:pd.DataFrame)->dict:
    if df.empty or 'closing_odds' not in df: return {'valid_count':0,'mean':None,'status':'CLV_UNAVAILABLE'}
    d=df.copy(); d['entry_odds']=pd.to_numeric(d.entry_odds,errors='coerce'); d['closing_odds']=pd.to_numeric(d.closing_odds,errors='coerce')
    d=d[(d.entry_odds>1)&(d.closing_odds>1)].copy()
    if d.empty:return {'valid_count':0,'mean':None,'status':'CLV_UNAVAILABLE'}
    d['clv']=(d.entry_odds/d.closing_odds)-1
    return {'valid_count':len(d),'mean':float(d.clv.mean()),'median':float(d.clv.median()),'status':'CLV_REAL'}

def temporal_oos(df:pd.DataFrame, cutoff:str)->dict:
    d=df.copy(); t=pd.to_datetime(d.decision_timestamp,utc=True,errors='coerce'); c=pd.Timestamp(cutoff,tz='UTC')
    return {'train':d[t<=c].copy(),'test':d[t>c].copy()}

def walk_forward(df:pd.DataFrame, folds:int=5)->list[dict]:
    if len(df)<folds:return []
    d=df.sort_values('decision_timestamp').reset_index(drop=True); out=[]
    for i,part in enumerate(np.array_split(d,folds),1):
        net=float(pd.to_numeric(part.get('profit_units',0),errors='coerce').fillna(0).sum()); n=len(part)
        out.append({'fold':i,'bets':n,'net_units':net,'roi':net/n if n else None,'clv':None})
    return out
