from __future__ import annotations

import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'ml'))
from app.research.cycle2 import build_chronological_features, build_target, _feature_sets, _folds, _safe_metrics, dataset_fingerprint
from app.research.cycle3 import assign_selection, assign_stakes, simulate_portfolio, summarize_ev_buckets, summarize_divergence

BASELINE_SHA='608f587b628b8d09c961519e9ca3ec5a664dd68e3091de4c0371937a2adcd967'
CANDIDATE_SHA='c1b8b0ef76be571f5be479871cb6d385325e5546e7030a013f11c6dd7ea3db66'


def market_prob(row, target):
    if target == 'home_win': return row.get('market_home_prob', np.nan)
    if target == 'over_2_5': return row.get('market_over25_prob', np.nan)
    return np.nan


def market_odds(row, target):
    return row.get('odds_1', np.nan) if target == 'home_win' else row.get('over_2_5', np.nan)


def outcome(row, target):
    return int(row.home_goals > row.away_goals) if target == 'home_win' else int((row.home_goals + row.away_goals) > 2.5)


def build_oos(df, target, feature_set, min_train, validation, test, holdout_fraction, seed):
    d=df.sort_values(["kickoff_timestamp","match_id"],kind="stable").reset_index(drop=True).copy()
    d["target"]=build_target(d,target)
    # All four configurations are evaluated on the SAME anchor population (FULL feature availability).
    # This prevents row-population differences from masquerading as model/selection improvement.
    anchor_features=_feature_sets(d.columns)["FULL"]
    usable=d.dropna(subset=anchor_features+["target"]).reset_index(drop=True)
    folds,research_n,holdout_n=_folds(usable.match_id.nunique(),min_train,validation,test,holdout_fraction)
    rows=[]
    for fi,(tr_end,va_end,_,te_end) in enumerate(folds):
        tr=usable.iloc[:tr_end]; te=usable.iloc[va_end:te_end]
        if feature_set == 'MARKET_ONLY':
            p=(te["market_home_prob"] if target=='home_win' else te["market_over25_prob"]).to_numpy(float)
        else:
            features=_feature_sets(d.columns)[feature_set]
            model=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000,random_state=seed))
            model.fit(tr[features],tr.target)
            p=model.predict_proba(te[features])[:,1]
        for i,(_,r) in enumerate(te.iterrows()):
            o=float(market_odds(r,target)); mp=float(market_prob(r,target))
            rows.append({
                'target':target,'fold':fi,'match_id':r.match_id,'kickoff_timestamp':r.kickoff_timestamp,
                'configuration':feature_set,'probability':float(p[i]),'market_probability':mp,'odds':o,
                'outcome':outcome(r,target),'pit_status':str(r.get('pit_status','NON_PIT')),
                'data_quality':1.0,'uncertainty':float(1-2*abs(float(p[i])-.5)),
                'decision_status':'COUNTERFACTUAL_NON_PIT','research_holdout_locked':False,
            })
    return pd.DataFrame(rows), {'research_events':int(research_n),'holdout_events':int(holdout_n),'folds':len(folds),'anchor':'FULL'}


def portfolio_matrix(preds, outdir):
    strategies=[]
    for config,g in preds.groupby('configuration',sort=False):
        for label,thr in [('ALL',-np.inf),('STRICT',0.05),('VERY_STRICT',0.10)]:
            x=g.copy()
            if np.isneginf(thr):
                x['selection_status']='APPROVED_RESEARCH'
                # pricing fields required by stake engine
                x['market_odds']=x['odds']; x['model_probability']=x['probability']; x['market_probability']=1/x['odds']; x['fair_odds']=1/x['probability']; x['edge']=x['probability']-1/x['odds']; x['raw_ev']=x['probability']*x['odds']-1
                x['scientific_status']='COUNTERFACTUAL_NON_PIT'
            else:
                x=assign_selection(x.rename(columns={'probability':'probability'}),ev_threshold=thr)
            for mode in ['flat_0.25','flat_0.50','flat_1.0','flat_1.5','dynamic']:
                y=assign_stakes(x,mode=mode)
                m=simulate_portfolio(y)
                strategies.append({'configuration':config,'selection':label,'stake_strategy':mode,**m})
    result=pd.DataFrame(strategies)
    result.to_csv(outdir/'CYCLE3_PORTFOLIO_MATRIX.csv',index=False)
    return result


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',default=str(ROOT/'data/enrichment/free_data/FOOTBALL_CANONICAL_ENRICHED_FREE.csv')); ap.add_argument('--output',default=str(ROOT/'reports/cycle3')); ap.add_argument('--seed',type=int,default=42); ap.add_argument('--min-train',type=int,default=1500); ap.add_argument('--validation',type=int,default=300); ap.add_argument('--test',type=int,default=500); ap.add_argument('--holdout-fraction',type=float,default=.15)
    a=ap.parse_args(); out=Path(a.output); out.mkdir(parents=True,exist_ok=True)
    raw=pd.read_csv(a.input); d=build_chronological_features(raw); fp=dataset_fingerprint(a.input)
    configs=['MARKET_ONLY','BASELINE','MARKET','FULL']
    allpred=[]; meta={}
    for target in ['home_win','over_2_5']:
        for cfg in configs:
            p,m=build_oos(d,target,cfg,a.min_train,a.validation,a.test,a.holdout_fraction,a.seed)
            allpred.append(p); meta[f'{target}:{cfg}']=m
    preds=pd.concat(allpred,ignore_index=True); preds.to_csv(out/'CYCLE3_OOS_DECISIONS.csv',index=False)
    preds['fair_odds']=1/preds['probability']; preds['edge']=preds['probability']-1/preds['odds']; preds['raw_ev']=preds['probability']*preds['odds']-1; preds['abs_divergence']=(preds['probability']-preds['market_probability']).abs(); preds['divergence']=preds['probability']-preds['market_probability']
    preds.to_csv(out/'CYCLE3_PRICED_OOS_DECISIONS.csv',index=False)
    ev_rows=[]; div_rows=[]
    for (cfg,target),g in preds.groupby(['configuration','target']):
        s=summarize_ev_buckets(g); s.insert(0,'configuration',cfg); s.insert(1,'target',target); ev_rows.append(s)
        if cfg!='MARKET_ONLY':
            z=summarize_divergence(g); z.insert(0,'configuration',cfg); z.insert(1,'target',target); div_rows.append(z)
    ev=pd.concat(ev_rows,ignore_index=True); ev.to_csv(out/'CYCLE3_EV_BUCKETS.csv',index=False)
    div=pd.concat(div_rows,ignore_index=True) if div_rows else pd.DataFrame(); div.to_csv(out/'CYCLE3_DIVERGENCE_BUCKETS.csv',index=False)
    raw_common=preds[(preds.target=='home_win') & (preds.fold==0)].copy()
    ids=(raw_common.groupby('match_id')['configuration'].nunique())
    common_ids=ids[ids==4].index
    common_home=raw_common[raw_common.match_id.isin(common_ids)].copy()
    portfolio=portfolio_matrix(common_home,out)
    common_home.to_csv(out/'CYCLE3_COMMON_SAMPLE_HOME_WIN.csv',index=False)
    # Model-level OOS diagnostics, without reusing final holdout.
    model_rows=[]
    for (cfg,target),g in preds.groupby(['configuration','target']):
        met=_safe_metrics(g.outcome,g.probability); model_rows.append({'configuration':cfg,'target':target,'n':len(g),**met,'status':'RESEARCH_OOS_NON_PIT'})
    model=pd.DataFrame(model_rows); model.to_csv(out/'CYCLE3_MODEL_DIAGNOSTICS.csv',index=False)
    # Threshold comparison for primary home-win candidate.
    sel=[]
    for cfg,g in common_home.groupby('configuration'):
        for label,thr in [('ALL',-np.inf),('EV>0',0.0),('EV>2%',0.02),('EV>5%',0.05),('EV>10%',0.10)]:
            x=g.copy(); x['market_odds']=x.odds; x['model_probability']=x.probability; x['market_probability']=x.market_probability; x['fair_odds']=x.fair_odds; x['edge']=x.edge; x['raw_ev']=x.raw_ev
            if np.isneginf(thr): x['selection_status']='APPROVED_RESEARCH'
            else: x['selection_status']=np.where(x.raw_ev>=thr,'APPROVED_RESEARCH','REJECT')
            x['stake']=np.where(x.selection_status=='APPROVED_RESEARCH',1.0,0.0)
            m=simulate_portfolio(x); sel.append({'configuration':cfg,'threshold':label,**m})
    pd.DataFrame(sel).to_csv(out/'CYCLE3_SELECTION_THRESHOLDS.csv',index=False)
    registry={'experiment_id':'V16_CYCLE3_2026-08-24','dataset':a.input,'dataset_sha256':fp,'baseline_sha256':BASELINE_SHA,'candidate_start_sha256':CANDIDATE_SHA,'configurations':configs,'targets':['home_win','over_2_5'],'min_train':a.min_train,'validation':a.validation,'test':a.test,'holdout_fraction':a.holdout_fraction,'exact_pit_count':0,'real_money':'DISABLED','scientific_status':'COUNTERFACTUAL_NON_PIT','final_holdout_used':False,'selection_strict_threshold':0.05,'selection_very_strict_threshold':0.10}
    (out/'CYCLE3_EXPERIMENT_REGISTRY.json').write_text(json.dumps(registry,indent=2),encoding='utf-8')
    report=[]; report += ['# ROBO DA BET V16+ — CYCLE 3 EXECUTIVE QUANT REPORT','',f'Dataset SHA-256: `{fp}`',f'Baseline SHA: `{BASELINE_SHA}`',f'Candidate start SHA: `{CANDIDATE_SHA}`','', 'EXACT_PIT = 0','REAL_MONEY = DISABLED','EDGE = NOT_PROVEN','All price/selection/portfolio results = COUNTERFACTUAL_NON_PIT','', '## OOS model diagnostics', model.to_markdown(index=False), '', '## Primary home-win selection thresholds — common fold-0 sample', pd.DataFrame(sel).to_markdown(index=False), '', '## Portfolio matrix — common fold-0 home-win sample (all four configurations)', portfolio.to_markdown(index=False), '', '## EV discrimination buckets', ev[ev.target.eq('home_win')].to_markdown(index=False)]
    if not div.empty: report += ['', '## Robo vs market divergence', div[div.target.eq('home_win')].to_markdown(index=False)]
    report += ['', '## Scientific interpretation','Selection and sizing results are counterfactual because the local odds are not Exact PIT. Positive theoretical ROI/Units, if observed, cannot be promoted to betting edge. The final holdout was excluded from optimization and simulation.','', '## Promotion','`RESEARCH_ONLY` unless an independent PIT-valid OOS population later confirms the same selection behavior.']
    (out/'CYCLE3_EXECUTIVE_REPORT.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    print(json.dumps({'rows':len(preds),'model_rows':len(model),'portfolio_rows':len(portfolio),'ev_rows':len(ev),'divergence_rows':len(div),'output':str(out)},indent=2))

if __name__=='__main__': main()
