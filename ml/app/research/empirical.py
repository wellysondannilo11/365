from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, brier_score_loss, accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from .features import HistoricalFeatureBuilder
from .validation import nested_walk_forward, assert_no_event_overlap
from .calibration import calibration_report
from .data_quality_v16 import profile

@dataclass
class EmpiricalResult:
    status:str
    evidence_type:str
    events:int
    folds:int
    predictions:int
    model:str
    metrics:dict
    limitations:list[str]


def dataset_fingerprint(df: pd.DataFrame) -> str:
    x=df.copy()
    cols=sorted(x.columns); x=x[cols]
    return hashlib.sha256(x.to_json(orient='records',date_format='iso',default_handler=str).encode()).hexdigest()


def build_real_features(df: pd.DataFrame, decision_col='decision_time'):
    builder=HistoricalFeatureBuilder()
    features,lineage=builder.build(df,decision_col=decision_col,source='real-data-v16')
    return features,pd.DataFrame([asdict(x) for x in lineage])


def run_binary(df: pd.DataFrame, feature_cols:list[str], label_col='label', min_train=100, validation=30, test=30, holdout=.15, seed=42):
    d=df.copy().sort_values(['event_time','event_id'],kind='stable').reset_index(drop=True)
    folds,research,hold=nested_walk_forward(d,min_train,validation,test,holdout=holdout)
    assert_no_event_overlap({'research':research,'holdout':hold})
    preds=[]; fold_metrics=[]
    for fi,f in enumerate(folds):
        tr=d.iloc[:f.train_end_idx]; va=d.iloc[f.validation_start_idx:f.validation_end_idx]; te=d.iloc[f.test_start_idx:f.test_end_idx]
        if tr[label_col].nunique()<2 or va[label_col].nunique()<2 or te[label_col].nunique()<2: continue
        model=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000,random_state=seed))
        model.fit(tr[feature_cols],tr[label_col].astype(int))
        pv=model.predict_proba(va[feature_cols])[:,1]
        pt=model.predict_proba(te[feature_cols])[:,1]
        rep=calibration_report(te[label_col].astype(int),pt)
        fold_metrics.append({'fold':fi,'n_train':len(tr),'n_validation':len(va),'n_test':len(te),**{k:rep[k] for k in ('logloss','brier','ece','mce')}})
        preds.append(pd.DataFrame({'event_id':te.event_id.astype(str),'event_time':te.event_time,'y':te[label_col].astype(int),'probability':pt,'fold':fi}))
    pred=pd.concat(preds,ignore_index=True) if preds else pd.DataFrame()
    if pred.empty:
        return {'status':'INSUFFICIENT_DATA','predictions':0,'folds':fold_metrics,'holdout_events':int(hold.event_id.astype(str).nunique()),'holdout_locked':True}
    rep=calibration_report(pred.y,pred.probability)
    return {'status':'PASS','predictions':len(pred),'folds':fold_metrics,'aggregate':rep,'accuracy':float(accuracy_score(pred.y,(pred.probability>=.5).astype(int))),'holdout_events':int(hold.event_id.astype(str).nunique()),'holdout_locked':True}


def run_real_research(df: pd.DataFrame, feature_cols:list[str], label_col='label', min_train=100, validation=30, test=30, holdout=.15):
    q=profile(df)
    if q['status']!='PASS':
        return EmpiricalResult('BLOCKED','REAL_DATA_RESEARCH',int(q['events']),0,0,'logistic',{},[f"DATA_QUALITY_GATE:{q['blocking_failures']}"])
    result=run_binary(df,feature_cols,label_col,min_train,validation,test,holdout)
    limitations=[]
    if 'odds' not in df.columns or 'available_at' not in df.columns:
        limitations.append('BETTING_VALUE_NOT_VALIDATED:historical_PIT_odds_missing')
    return EmpiricalResult(result['status'],'REAL_DATA_RESEARCH',int(q['events']),len(result.get('folds',[])),int(result.get('predictions',0)),'logistic',result.get('aggregate',{}),limitations)
