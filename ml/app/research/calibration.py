from __future__ import annotations
import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss,brier_score_loss

class OOSCalibrator:
    def __init__(self,method='isotonic'): self.method=method; self.model=None
    def fit(self,p,y):
        p=np.asarray(p,float);y=np.asarray(y,int)
        if len(y)<30 or len(np.unique(y))<2: raise ValueError('INSUFFICIENT_CALIBRATION_SAMPLE')
        if self.method=='isotonic': self.model=IsotonicRegression(out_of_bounds='clip').fit(p,y)
        elif self.method in ('platt','sigmoid'):
            z=np.log(np.clip(p,1e-6,1-1e-6)/(1-np.clip(p,1e-6,1-1e-6))).reshape(-1,1); self.model=LogisticRegression(max_iter=1000).fit(z,y)
        else: raise ValueError('UNKNOWN_CALIBRATOR')
        return self
    def predict(self,p):
        p=np.asarray(p,float)
        if self.model is None: raise RuntimeError('CALIBRATOR_NOT_FIT')
        if self.method in ('platt','sigmoid'):
            z=np.log(np.clip(p,1e-6,1-1e-6)/(1-np.clip(p,1e-6,1-1e-6))).reshape(-1,1);return self.model.predict_proba(z)[:,1]
        return self.model.predict(p)

def calibration_report(y,p,bins=10):
    y=np.asarray(y);p=np.asarray(p);ece=mce=0.;rows=[]
    for lo,hi in zip(np.linspace(0,1,bins,endpoint=False),np.linspace(0,1,bins+1)[1:]):
        mask=(p>=lo)&(p<(hi if hi<1 else 1.00001))
        if mask.any():
            gap=float(abs(p[mask].mean()-y[mask].mean()));ece+=gap*mask.mean();mce=max(mce,gap);rows.append({'lo':lo,'hi':hi,'n':int(mask.sum()),'pred':float(p[mask].mean()),'actual':float(y[mask].mean())})
    return {'logloss':float(log_loss(y,p,labels=[0,1])),'brier':float(brier_score_loss(y,p)),'ece':float(ece),'mce':float(mce),'reliability':rows}
