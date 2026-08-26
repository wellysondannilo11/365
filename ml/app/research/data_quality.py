import pandas as pd

def report(df):
    issues=[]
    for c in df.columns:
        n=int(df[c].isna().sum())
        if n: issues.append({'type':'missing','column':c,'count':n})
    if 'event_id' in df:
        dup=int(df.event_id.duplicated().sum())
        if dup:issues.append({'type':'duplicate_event_id','count':dup})
    if 'odds' in df:
        bad=int((pd.to_numeric(df.odds,errors='coerce')<=1).fillna(True).sum())
        if bad:issues.append({'type':'invalid_odds','count':bad})
    if {'available_at','decision_time'}.issubset(df.columns):
        a=pd.to_datetime(df.available_at,utc=True);d=pd.to_datetime(df.decision_time,utc=True);bad=int((a>d).sum())
        if bad:issues.append({'type':'pit_violation','count':bad})
    return {'rows':len(df),'issues':issues,'status':'PASS' if not issues else 'FAIL'}
