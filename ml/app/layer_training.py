from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .models import ModelSuite,calibrate,apply_calibrator,calibration_metrics

@dataclass
class LayerResult:
    name:str; probability:np.ndarray; uncertainty:np.ndarray; metrics:dict; feature_names:list[str]

class ThreeLayerTrainer:
    """Explicit Sport-only, Market-only and Hybrid layers. Each is evaluated OOS on the same temporal cut."""
    def fit(self,df,sport_features,market_features,label_col='label',oos_start=None):
        y=df[label_col].astype(int).to_numpy();oos_start=oos_start or max(1,int(len(df)*.7));out={}
        for name,features in [('SPORT_ONLY',sport_features),('MARKET_ONLY',market_features),('HYBRID',sport_features+market_features)]:
            features=[f for f in features if f in df.columns]
            if not features:continue
            X=df[features].replace([np.inf,-np.inf],np.nan).fillna(0).to_numpy()
            suite=ModelSuite();results=suite.fit_oos(X,y,split=oos_start/len(df));p,unc=suite.ensemble_probability(X[oos_start:]);cal=calibrate(y[oos_start:],p,'isotonic');pc=apply_calibrator(cal,p) if cal['method']!='none' else p
            out[name]=LayerResult(name,pc,unc,calibration_metrics(y[oos_start:],pc),features)
        return out
