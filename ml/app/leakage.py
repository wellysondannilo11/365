from __future__ import annotations
import pandas as pd

REQUIRED_TIME_COLUMNS=['event_time','source_time','available_at','ingested_at','decision_time']
META_COLUMNS=set(REQUIRED_TIME_COLUMNS)|{'event_id','entity_id','source','source_id','source_record_id','schema_version','dataset_version','feature_version'}
TARGET_COLUMNS={'label','result','outcome','home_goals','away_goals','goals','settled_result','pnl','profit'}
STATIC_COLUMNS={'home_team','away_team','team_id','league','season','competition','bookmaker','market','selection','line'}
ROW_LEVEL_PIT_COLUMNS={'price','odds','probability','p_sport','p_market','p_hybrid','p_raw','p_calibrated','p_final','closing_odds','opening_odds'}

def audit_point_in_time(df: pd.DataFrame, feature_columns=None, target_columns=None) -> pd.DataFrame:
    rows=[]; target_columns=set(target_columns or TARGET_COLUMNS)
    if feature_columns is None:
        feature_columns=[c for c in df.columns if c not in META_COLUMNS and not c.endswith('__available_at') and c not in target_columns]
    for idx,r in df.iterrows():
        decision=pd.to_datetime(r.get('decision_time'),utc=True,errors='coerce')
        for f in feature_columns:
            if f not in df.columns or f in STATIC_COLUMNS or f in ROW_LEVEL_PIT_COLUMNS: continue
            ac=f'{f}__available_at'
            if ac not in df.columns:
                rows.append({'row':idx,'feature':f,'event':r.get('event_id',idx),'decision_time':decision,'available_at':pd.NaT,'violation':True,'reason':'MISSING_FEATURE_AVAILABILITY'})
                continue
            available=pd.to_datetime(r.get(ac),utc=True,errors='coerce')
            violation=bool(pd.isna(decision) or pd.isna(available) or available>decision)
            if violation: rows.append({'row':idx,'feature':f,'event':r.get('event_id',idx),'decision_time':decision,'available_at':available,'violation':True,'reason':'AVAILABLE_AFTER_DECISION' if pd.notna(available) else 'INVALID_FEATURE_AVAILABILITY'})
    return pd.DataFrame(rows,columns=['row','feature','event','decision_time','available_at','violation','reason'])

def validate_temporal_dataset(df: pd.DataFrame, *, target_columns=None, allow_static=True) -> None:
    missing=[c for c in REQUIRED_TIME_COLUMNS if c not in df.columns]
    if missing: raise ValueError(f'MISSING_POINT_IN_TIME_COLUMNS:{missing}')
    d=pd.to_datetime(df.decision_time,utc=True,errors='coerce'); a=pd.to_datetime(df.available_at,utc=True,errors='coerce'); s=pd.to_datetime(df.source_time,utc=True,errors='coerce'); ing=pd.to_datetime(df.ingested_at,utc=True,errors='coerce')
    if any(x.isna().any() for x in (d,a,s,ing)): raise ValueError('INVALID_POINT_IN_TIME_TIMESTAMP')
    if (a>d).any(): raise ValueError('POINT_IN_TIME_LEAKAGE')
    if (s>d).any(): raise ValueError('SOURCE_TIME_AFTER_DECISION')
    if (ing<s).any(): raise ValueError('INGESTED_BEFORE_SOURCE')
    violations=audit_point_in_time(df,target_columns=target_columns)
    if not violations.empty: raise ValueError(f'FEATURE_LEVEL_LEAKAGE:{violations.head(10).to_dict(orient="records")}')

def validate_feature_lineage(lineage: pd.DataFrame) -> None:
    required={'feature_name','event_id','as_of','available_at','source_record_ids'}
    missing=required-set(lineage.columns)
    if missing: raise ValueError(f'MISSING_FEATURE_LINEAGE_COLUMNS:{sorted(missing)}')
    x=lineage.copy(); x['as_of']=pd.to_datetime(x.as_of,utc=True,errors='coerce'); x['available_at']=pd.to_datetime(x.available_at,utc=True,errors='coerce')
    if x[['as_of','available_at']].isna().any().any(): raise ValueError('INVALID_FEATURE_LINEAGE_TIMESTAMP')
    if (x.available_at>x.as_of).any(): raise ValueError('FEATURE_LINEAGE_LEAKAGE')
