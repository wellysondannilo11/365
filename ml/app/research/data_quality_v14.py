from __future__ import annotations
import pandas as pd

def report_v14(df):
    d=df.copy(); issues=[]
    for c in d.columns:
        n=int(d[c].isna().sum())
        if n: issues.append({'type':'missing','column':c,'count':n})
    if 'event_id' in d:
        n=int(d.event_id.duplicated().sum())
        if n: issues.append({'type':'duplicate_event_id','count':n})
    if {'event_id','event_time'}.issubset(d):
        n=int(d.duplicated(subset=['event_id','event_time']).sum())
        if n: issues.append({'type':'duplicate_event_time','count':n})
    if 'odds' in d:
        p=pd.to_numeric(d.odds,errors='coerce'); n=int((p.isna()|(p<=1)).sum())
        if n: issues.append({'type':'invalid_odds','count':n})
    if 'price' in d:
        p=pd.to_numeric(d.price,errors='coerce'); n=int((p.isna()|(p<=1)).sum())
        if n: issues.append({'type':'invalid_price','count':n})
    for c in ('event_time','source_time','available_at','ingested_at','decision_time','captured_at'):
        if c in d and pd.to_datetime(d[c],utc=True,errors='coerce').isna().any():
            issues.append({'type':'invalid_timestamp','column':c})
    if {'available_at','decision_time'}.issubset(d):
        a=pd.to_datetime(d.available_at,utc=True); t=pd.to_datetime(d.decision_time,utc=True); n=int((a>t).sum())
        if n: issues.append({'type':'future_data','count':n})
    if {'source_time','decision_time'}.issubset(d):
        n=int((pd.to_datetime(d.source_time,utc=True)>pd.to_datetime(d.decision_time,utc=True)).sum())
        if n: issues.append({'type':'source_after_decision','count':n})
    if {'ingested_at','source_time'}.issubset(d):
        n=int((pd.to_datetime(d.ingested_at,utc=True)<pd.to_datetime(d.source_time,utc=True)).sum())
        if n: issues.append({'type':'ingested_before_source','count':n})
    if {'event_time','decision_time'}.issubset(d):
        n=int((pd.to_datetime(d.decision_time,utc=True)>pd.to_datetime(d.event_time,utc=True)).sum())
        if n: issues.append({'type':'decision_after_event','count':n})
    return {'rows':len(d),'issues':issues,'status':'PASS' if not issues else 'FAIL'}
