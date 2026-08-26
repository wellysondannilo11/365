from __future__ import annotations
import pandas as pd
import numpy as np


def _rate(x, n):
    return float(x / n) if n else 0.0


def profile(df: pd.DataFrame) -> dict:
    d=df.copy()
    n=len(d)
    out={
        'rows': int(n),
        'events': int(d.event_id.astype(str).nunique()) if 'event_id' in d else 0,
        'duplicate_rows': int(d.duplicated().sum()),
        'duplicate_event_ids': int(d.event_id.astype(str).duplicated().sum()) if 'event_id' in d else 0,
        'missing_by_column': {str(c): int(v) for c,v in d.isna().sum().items()},
        'invalid_odds': 0,
        'timestamp_invalid': 0,
        'pit_violations': 0,
        'event_time_inconsistency': 0,
        'status': 'PASS',
        'blocking_failures': [],
    }
    if 'price' in d:
        p=pd.to_numeric(d.price,errors='coerce')
        out['invalid_odds']=int(p.isna().sum()+(p<=1).sum())
    for c in ('event_time','decision_time','available_at','source_time','ingested_at'):
        if c in d:
            out['timestamp_invalid'] += int(pd.to_datetime(d[c],utc=True,errors='coerce').isna().sum())
    if {'available_at','decision_time'}.issubset(d.columns):
        a=pd.to_datetime(d.available_at,utc=True,errors='coerce'); t=pd.to_datetime(d.decision_time,utc=True,errors='coerce')
        out['pit_violations']=int((a>t).sum())
    if {'event_id','event_time'}.issubset(d.columns):
        x=pd.to_datetime(d.event_time,utc=True,errors='coerce')
        g=pd.DataFrame({'event_id':d.event_id.astype(str),'event_time':x}).groupby('event_id').event_time.agg(['min','max'])
        out['event_time_inconsistency']=int((g['min']!=g['max']).sum())
    checks={
        'duplicate_rows': out['duplicate_rows'],
        'invalid_odds': out['invalid_odds'],
        'timestamp_invalid': out['timestamp_invalid'],
        'pit_violations': out['pit_violations'],
        'event_time_inconsistency': out['event_time_inconsistency'],
    }
    out['blocking_failures']=[k for k,v in checks.items() if v]
    out['status']='FAIL' if out['blocking_failures'] else 'PASS'
    out['completeness_rate']=_rate(n-sum(out['missing_by_column'].values()), n*max(len(d.columns),1)) if n else 0.0
    return out


def assert_clean(df: pd.DataFrame) -> None:
    r=profile(df)
    if r['status']!='PASS':
        raise ValueError(f"DATA_QUALITY_GATE_FAILED:{r['blocking_failures']}")
