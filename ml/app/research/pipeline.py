from __future__ import annotations
from dataclasses import dataclass,asdict
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier,HistGradientBoostingClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import log_loss,brier_score_loss
from .validation import nested_walk_forward,assert_no_event_overlap
from .calibration import OOSCalibrator,calibration_report
from .statistics import block_bootstrap

@dataclass
class FoldResult:
    fold:int; model:str; n_train:int; n_val:int; n_test:int; logloss:float; brier:float; ece:float; mce:float

class ResearchPipeline:
    def __init__(self,seed=42): self.seed=seed
    def candidates(self):
        models={'logistic':make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000,random_state=self.seed)),
        'random_forest':RandomForestClassifier(n_estimators=300,min_samples_leaf=8,random_state=self.seed,n_jobs=-1),
        'gradient_boosting':GradientBoostingClassifier(random_state=self.seed,n_estimators=150,max_depth=2),
        'hist_gradient_boosting':HistGradientBoostingClassifier(random_state=self.seed,max_iter=150,max_leaf_nodes=15)}
        for name,loader in [('xgboost','xgboost'),('lightgbm','lightgbm'),('catboost','catboost')]:
            try:
                if name=='xgboost':
                    from xgboost import XGBClassifier;models[name]=XGBClassifier(n_estimators=250,max_depth=3,learning_rate=.04,subsample=.8,colsample_bytree=.8,eval_metric='logloss',random_state=self.seed,n_jobs=2)
                elif name=='lightgbm':
                    from lightgbm import LGBMClassifier;models[name]=LGBMClassifier(n_estimators=250,max_depth=4,learning_rate=.03,num_leaves=15,random_state=self.seed,verbosity=-1)
                else:
                    from catboost import CatBoostClassifier;models[name]=CatBoostClassifier(iterations=250,depth=5,learning_rate=.04,verbose=False,random_seed=self.seed)
            except Exception: pass
        return models
    def run(self,df,feature_cols,label_col,min_train=100,validation=30,test=30,holdout=.15):
        """Walk-forward research with validation-only model selection.

        Each fold selects the champion using validation data only. The test window
        is evaluated exactly once by that champion, then discarded. The final
        holdout is never touched by selection, calibration or threshold tuning.
        """
        d=df.sort_values(['event_time','event_id']).reset_index(drop=True).copy()
        folds,research,final_holdout=nested_walk_forward(d,min_train,validation,test,holdout=holdout)
        if len(folds)==0: raise ValueError('INSUFFICIENT_DATA_FOR_WALK_FORWARD')
        assert_no_event_overlap({'research':research,'holdout':final_holdout})
        allres=[]; selections=[]; candidate_errors=[]
        for fi,f in enumerate(folds):
            # Use the fold's row boundaries, not timestamp predicates. Multiple events
            # can share a kickoff timestamp; timestamp-only slicing can duplicate them.
            tr=d.iloc[:f.train_end_idx]
            va=d.iloc[f.validation_start_idx:f.validation_end_idx]
            te=d.iloc[f.test_start_idx:f.test_end_idx]
            assert_no_event_overlap({'train':tr,'validation':va,'test':te})
            if len(tr)<min_train or len(va)<2 or len(te)<2 or tr[label_col].nunique()<2 or va[label_col].nunique()<2 or te[label_col].nunique()<2:
                continue
            validation_scores=[]; fitted={}
            for name,model in self.candidates().items():
                try:
                    model.fit(tr[feature_cols],tr[label_col].astype(int))
                    pv=model.predict_proba(va[feature_cols])[:,1]
                    validation_scores.append((float(log_loss(va[label_col],pv,labels=[0,1])),name,model,pv))
                except Exception as exc:
                    candidate_errors.append({'fold':fi,'model':name,'error':type(exc).__name__})
                    continue
            if not validation_scores: continue
            validation_scores.sort(key=lambda x:(x[0],x[1]))
            val_logloss,name,model,pv=validation_scores[0]
            # Calibration is fit only on validation predictions, never on test/holdout.
            calibrated=False
            pt=model.predict_proba(te[feature_cols])[:,1]
            if len(va)>=30:
                try:
                    cal=OOSCalibrator('isotonic').fit(pv,va[label_col])
                    pt=cal.predict(pt); calibrated=True
                except ValueError:
                    calibrated=False
            report=calibration_report(te[label_col],pt)
            allres.append(FoldResult(fi,name,len(tr),len(va),len(te),report['logloss'],report['brier'],report['ece'],report['mce']))
            selections.append({'fold':fi,'champion':name,'validation_logloss':val_logloss,'test_rows':len(te),'calibrated':calibrated})
        return {'folds':[asdict(x) for x in allres],'selections':selections,'candidate_errors':candidate_errors,'final_holdout_rows':len(final_holdout),'final_holdout_events':int(final_holdout.event_id.astype(str).nunique()) if 'event_id' in final_holdout else 0,'holdout_locked':True,'performance_claim':'NOT_AVAILABLE_WITHOUT_REAL_HISTORICAL_DATA'}
