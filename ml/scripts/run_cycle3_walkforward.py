from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'ml'))
from app.research.cycle2 import build_chronological_features, build_target, _feature_sets, _folds, dataset_fingerprint
from app.research.cycle3 import simulate_portfolio


def run(df,target,cfg,min_train=1000,validation=200,test=300,holdout_fraction=.15,seed=42):
    d=df.sort_values(['kickoff_timestamp','match_id'],kind='stable').reset_index(drop=True).copy(); d['target']=build_target(d,target)
    features=_feature_sets(d.columns)['FULL']; u=d.dropna(subset=features+['target']).reset_index(drop=True)
    folds,research,holdout=_folds(u.match_id.nunique(),min_train,validation,test,holdout_fraction)
    rows=[]
    for fi,(tr_end,va_end,_,te_end) in enumerate(folds):
        tr=u.iloc[:tr_end]; te=u.iloc[va_end:te_end]
        if cfg=='MARKET_ONLY': p=(te.market_home_prob if target=='home_win' else te.market_over25_prob).to_numpy(float)
        else:
            fs=_feature_sets(d.columns)[cfg]; m=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000,random_state=seed)); m.fit(tr[fs],tr.target); p=m.predict_proba(te[fs])[:,1]
        odds=te.odds_1.to_numpy(float) if target=='home_win' else te.over_2_5.to_numpy(float); y=te.target.to_numpy(int)
        base=pd.DataFrame({'odds':odds,'outcome':y,'probability':p}); base['raw_ev']=base.probability*base.odds-1
        for label,thr in [('EV>0',0),('EV>5%',.05),('EV>10%',.10)]:
            x=base[base.raw_ev>=thr].copy(); x['stake']=1.0; m=simulate_portfolio(x)
            rows.append({'configuration':cfg,'target':target,'fold':fi,'train':len(tr),'validation':validation,'test':len(te),'threshold':label,**m})
    return pd.DataFrame(rows), {'folds':len(folds),'research_events':research,'holdout_events':holdout}


def main():
    inp=ROOT/'data/enrichment/free_data/FOOTBALL_CANONICAL_ENRICHED_FREE.csv'; out=ROOT/'reports/cycle3'; out.mkdir(parents=True,exist_ok=True)
    d=build_chronological_features(pd.read_csv(inp)); frames=[]; meta={}
    for cfg in ['MARKET_ONLY','BASELINE','MARKET','FULL']:
        f,m=run(d,'home_win',cfg); frames.append(f); meta[cfg]=m
    allf=pd.concat(frames,ignore_index=True); allf.to_csv(out/'CYCLE3_WALK_FORWARD_SELECTION.csv',index=False)
    summary=allf.groupby(['configuration','threshold'],as_index=False).agg(folds=('fold','nunique'),bets=('bets','sum'),units=('units','sum'),mean_fold_roi=('roi','mean'),median_fold_roi=('roi','median'),positive_folds=('roi',lambda x:int((x>0).sum())),max_fold_drawdown=('max_drawdown_u','max'))
    summary['status']='COUNTERFACTUAL_NON_PIT'; summary.to_csv(out/'CYCLE3_WALK_FORWARD_SUMMARY.csv',index=False)
    (out/'CYCLE3_WALK_FORWARD_META.json').write_text(json.dumps({'protocol':'secondary_exploratory','min_train':1000,'validation':200,'test':300,'holdout_fraction':.15,'dataset_sha256':dataset_fingerprint(inp),'exact_pit':0,'final_holdout_used':False,'meta':meta},indent=2),encoding='utf-8')
    print(summary.to_string(index=False))
if __name__=='__main__': main()
