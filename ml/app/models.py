from __future__ import annotations
from dataclasses import dataclass
import numpy as np, math
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier,HistGradientBoostingClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import log_loss,brier_score_loss
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
@dataclass
class ModelResult:
    name:str;oos_logloss:float;oos_brier:float;sample:int;model:object|None=None
class ModelSuite:
    def __init__(self,include_optional=True,seed=42):self.models={};self.results=[];self.include_optional=include_optional;self.seed=seed
    def candidates(self):
        out={'logistic':make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000,random_state=self.seed)),'random_forest':RandomForestClassifier(n_estimators=300,min_samples_leaf=8,random_state=self.seed,n_jobs=-1),'gradient_boosting':GradientBoostingClassifier(random_state=self.seed,n_estimators=150,max_depth=2),'hist_gradient_boosting':HistGradientBoostingClassifier(random_state=self.seed,max_iter=150,max_leaf_nodes=15)}
        if self.include_optional:
            try:
                from xgboost import XGBClassifier;out['xgboost']=XGBClassifier(n_estimators=250,max_depth=3,learning_rate=.04,subsample=.8,colsample_bytree=.8,eval_metric='logloss',random_state=self.seed,n_jobs=2)
            except Exception:pass
            try:
                from lightgbm import LGBMClassifier;out['lightgbm']=LGBMClassifier(n_estimators=250,max_depth=4,learning_rate=.03,num_leaves=15,random_state=self.seed,verbosity=-1)
            except Exception:pass
            try:
                from catboost import CatBoostClassifier;out['catboost']=CatBoostClassifier(iterations=250,depth=5,learning_rate=.04,verbose=False,random_seed=self.seed)
            except Exception:pass
        return out
    def fit_oos(self,X,y,split=.7):
        X=np.asarray(X);y=np.asarray(y);cut=max(1,int(len(y)*split));
        if cut>=len(y) or len(np.unique(y[:cut]))<2:raise ValueError('INSUFFICIENT_TRAINING_CLASSES')
        res=[]
        for name,m in self.candidates().items():
            try:m.fit(X[:cut],y[:cut]);p=m.predict_proba(X[cut:])[:,1];res.append(ModelResult(name,float(log_loss(y[cut:],p,labels=[0,1])),float(brier_score_loss(y[cut:],p)),len(y[cut:]),m))
            except Exception:continue
        res.sort(key=lambda r:(r.oos_logloss,r.oos_brier));self.results=res;self.models={r.name:r.model for r in res};return res
    def ensemble_probability(self,X,top_k=4):
        rs=self.results[:top_k]
        if not rs:raise RuntimeError('models not trained')
        ps=np.array([r.model.predict_proba(X)[:,1] for r in rs]);return ps.mean(axis=0),ps.std(axis=0)
class DixonColes:
    def __init__(self):self.attack={};self.defense={};self.home_adv=0.;self.mu=1.35
    def fit(self,matches,decay=.002):
        w=[];vals=[]
        for i,m in enumerate(matches):w.append(math.exp(-decay*(len(matches)-1-i)));vals.append(m)
        self.mu=float(np.average([(m['hg']+m['ag'])/2 for m in vals],weights=w)) if vals else 1.35;self.home_adv=float(np.average([m['hg']-m['ag'] for m in vals],weights=w)) if vals else 0.;return self
    def predict_total_over(self,line,remaining=False):
        lam=max(.05,self.mu*2);k=int(line)+1;return 1-sum(math.exp(-lam)*lam**i/math.factorial(i) for i in range(k))
def calibrate(y,p,method='isotonic'):
    y=np.asarray(y);p=np.asarray(p)
    if len(y)<30 or len(np.unique(y))<2:return {'method':'none','reason':'INSUFFICIENT_SAMPLE','transform':lambda x:np.asarray(x)}
    if method=='isotonic':return {'method':'isotonic','transform':IsotonicRegression(out_of_bounds='clip').fit(p,y)}
    z=np.log(np.clip(p,1e-6,1-1e-6)/(1-np.clip(p,1e-6,1-1e-6))).reshape(-1,1);return {'method':'platt','transform':LogisticRegression(max_iter=1000).fit(z,y)}
def apply_calibrator(cal,p):
    p=np.asarray(p);t=cal['transform']
    if cal['method']=='platt':
        z=np.log(np.clip(p,1e-6,1-1e-6)/(1-np.clip(p,1e-6,1-1e-6))).reshape(-1,1);return t.predict_proba(z)[:,1]
    return t.predict(p)
def calibration_metrics(y,p,bins=10):
    y=np.asarray(y);p=np.asarray(p);ece=mce=0.
    for lo,hi in zip(np.linspace(0,1,bins,endpoint=False),np.linspace(0,1,bins+1)[1:]):
        mask=(p>=lo)&(p<(hi if hi<1 else 1.00001))
        if mask.any():gap=abs(float(p[mask].mean())-float(y[mask].mean()));ece+=gap*mask.mean();mce=max(mce,gap)
    return {'logloss':float(log_loss(y,p,labels=[0,1])),'brier':float(brier_score_loss(y,p)),'ece':float(ece),'mce':float(mce)}
