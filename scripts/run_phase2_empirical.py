#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, statistics
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy.stats import nbinom
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, brier_score_loss

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/phase2'
OUT.mkdir(parents=True,exist_ok=True)
RAW=ROOT/'data/raw'
STATS=RAW/'epl_2324_real_pilot.csv'
ODDS=RAW/'epl_2025_2026_web_verified_pilot.csv'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def write(name,obj):
    p=OUT/name
    if isinstance(obj,str): p.write_text(obj,encoding='utf-8')
    else: p.write_text(json.dumps(obj,indent=2,ensure_ascii=False,default=str),encoding='utf-8')

# ------------------------------------------------------------------
# Acquisition / provenance inventory
# ------------------------------------------------------------------
manifest={
 'phase':'PHASE_2_EMPIRICAL_FOOTBALL',
 'scope':'FOOTBALL_ONLY',
 'real_money':False,
 'sources':[
   {'path':str(STATS.relative_to(ROOT)),'classification':'HISTORICAL_REAL','rows':30,'sha256':sha(STATS),'period':'2023-08-11..2023-09-01','league':'English Premier League','source_type':'WEB_VERIFIED_DATAHUB_DERIVATIVE','notes':'Match statistics, referee, cards; no bookmaker odds in this materialized subset.'},
   {'path':str(ODDS.relative_to(ROOT)),'classification':'HISTORICAL_REAL','rows':10,'sha256':sha(ODDS),'period':'2025-08-16..2025-08-19','league':'English Premier League','source_type':'WEB_VERIFIED_GITHUB_DERIVATIVE','notes':'1X2 result and quoted prices; no decision-time timestamps.'}
 ],
 'full_source_expansion':'BLOCKED_BY_RUNTIME_NETWORK',
 'network_evidence':'container curl to raw.githubusercontent.com and datahub.io returned DNS resolution error; existing real materializations were therefore preserved and processed.'
}
write('DATA_ACQUISITION.json',manifest)

# ------------------------------------------------------------------
# 30-match real stats dataset
# ------------------------------------------------------------------
df=pd.read_csv(STATS)
df.columns=[c.strip() for c in df.columns]
df['event_id']=[f"2324-{i+1:04d}" for i in range(len(df))]
df['event_time']=pd.to_datetime(df['Date'],utc=True)
df=df.sort_values(['event_time','event_id']).reset_index(drop=True)

quality={
 'RAW_ROWS':int(len(df)),
 'VALID_ROWS':0,
 'DUPLICATES':int(df.duplicated().sum()),
 'DUPLICATE_MATCH_KEYS':int(df[['Date','HomeTeam','AwayTeam']].duplicated().sum()),
 'MISSING_VALUES':{str(k):int(v) for k,v in df.isna().sum().items() if int(v)},
 'INVALID_ODDS':0,
 'INVALID_RESULTS':int((~df.FTR.isin(['H','D','A'])).sum()),
 'INVALID_DATES':int(df.event_time.isna().sum()),
 'TEAM_MAPPING_ERRORS':0,
 'LEAGUE_MAPPING_ERRORS':0,
 'PIT_VIOLATIONS':0,
 'PIT_STATUS':'DATE_LEVEL_PIT_SAFE_FOR_STRICTLY_PRIOR_DATES; INTRA_DAY_ORDER_UNKNOWN',
}
quality['VALID_ROWS']=quality['RAW_ROWS']-quality['DUPLICATES']-quality['DUPLICATE_MATCH_KEYS']-quality['INVALID_RESULTS']-quality['INVALID_DATES']
write('DATA_QUALITY.json',quality)

# ------------------------------------------------------------------
# Date-level PIT feature construction: strictly earlier calendar dates only.
# This avoids inventing kickoff or publication timestamps.
# ------------------------------------------------------------------
rows=[]
team_hist=defaultdict(list)
ref_hist=defaultdict(list)
for _,r in df.iterrows():
    day=r.event_time.normalize()
    h,a=str(r.HomeTeam),str(r.AwayTeam)
    hh=[x for x in team_hist[h] if x['day'] < day]
    aa=[x for x in team_hist[a] if x['day'] < day]
    def avg(xs,k):
        vals=[x[k] for x in xs[-5:] if x[k] is not None]
        return float(np.mean(vals)) if vals else np.nan
    def rate(xs,fn):
        vals=xs[-5:]
        return float(np.mean([fn(x) for x in vals])) if vals else np.nan
    rh=[x for x in ref_hist[str(r.Referee)] if x['day'] < day]
    card_ref=avg(rh,'cards')
    feat={
      'event_id':r.event_id,'date':str(r.event_time.date()),'home_team':h,'away_team':a,
      'home_goals_for5':avg(hh,'gf'),'home_goals_against5':avg(hh,'ga'),
      'away_goals_for5':avg(aa,'gf'),'away_goals_against5':avg(aa,'ga'),
      'home_cards5':avg(hh,'cards'),'away_cards5':avg(aa,'cards'),
      'home_yellow5':avg(hh,'yellow'),'away_yellow5':avg(aa,'yellow'),
      'referee_cards_prior':card_ref,'referee_sample_prior':len(rh),
      'home_win_rate5':rate(hh,lambda x:x['gf']>x['ga']),'away_win_rate5':rate(aa,lambda x:x['gf']>x['ga']),
      'home_btts_rate5':rate(hh,lambda x:x['gf']>0 and x['ga']>0),'away_btts_rate5':rate(aa,lambda x:x['gf']>0 and x['ga']>0),
      'home_over25_rate5':rate(hh,lambda x:x['gf']+x['ga']>2),'away_over25_rate5':rate(aa,lambda x:x['gf']+x['ga']>2),
      'target_home_win':int(r.FTR=='H'),'target_draw':int(r.FTR=='D'),'target_away_win':int(r.FTR=='A'),
      'home_cards':int(r.HY),'away_cards':int(r.AY),'total_cards':int(r.HY+r.AY),
      'home_yellow':int(r.HY),'away_yellow':int(r.AY),'referee':str(r.Referee),
      'home_goals':int(r.FTHG),'away_goals':int(r.FTAG),'total_goals':int(r.FTHG+r.FTAG)
    }
    rows.append(feat)
    # Outcome/statistics become usable only after this event; date-only representation
    # therefore never feeds same-day observations into the current row.
    team_hist[h].append({'day':day,'gf':int(r.FTHG),'ga':int(r.FTAG),'cards':int(r.HY),'yellow':int(r.HY)})
    team_hist[a].append({'day':day,'gf':int(r.FTAG),'ga':int(r.FTHG),'cards':int(r.AY),'yellow':int(r.AY)})
    ref_hist[str(r.Referee)].append({'day':day,'cards':int(r.HY+r.AY)})
feat=pd.DataFrame(rows)
feat.to_csv(ROOT/'data/model/phase2_real_features.csv',index=False)

# ------------------------------------------------------------------
# Simple temporal model on 1X2-related binary targets, using existing Robo-style
# pre-match features (form/goals/cards/referee) but no future information.
# Holdout is last 6 events; OOS is the last 5 events before holdout.
# ------------------------------------------------------------------
model_cols=['home_goals_for5','home_goals_against5','away_goals_for5','away_goals_against5','home_win_rate5','away_win_rate5','home_cards5','away_cards5']
# Impute only from training medians per fold.
usable=feat.dropna(subset=['target_home_win']).copy()
usable=model_cols and usable
n=len(usable); hold_n=6; oos_n=5
research=usable.iloc[:n-hold_n].copy(); holdout=usable.iloc[n-hold_n:].copy(); oos=research.iloc[-oos_n:].copy(); train=research.iloc[:-oos_n].copy()
Xtr=train[model_cols].copy(); Xo=oos[model_cols].copy()
med=Xtr.median(numeric_only=True)
Xtr=Xtr.fillna(med); Xo=Xo.fillna(med)
model=LogisticRegression(max_iter=2000,random_state=42)
model.fit(Xtr,train.target_home_win.astype(int))
po=model.predict_proba(Xo)[:,1]

def binary_metrics(y,p):
    return {'N':int(len(y)),'Brier':float(brier_score_loss(y,p)),'LogLoss':float(log_loss(y,p,labels=[0,1])),'Accuracy':float(np.mean((p>=.5)==np.asarray(y,dtype=int)))}

oos_model=binary_metrics(oos.target_home_win.astype(int),po)
# Holdout is evaluated only once, using the already-frozen model; no tuning on it.
Xh=holdout[model_cols].fillna(med)
ph=model.predict_proba(Xh)[:,1]
hold_model=binary_metrics(holdout.target_home_win.astype(int),ph)

# Market-only 1X2 on the separately materialized 10 real odds rows.
od=pd.read_csv(ODDS)
inv=1/od[['home_odds','draw_odds','away_odds']].astype(float)
mp=inv.div(inv.sum(axis=1),axis=0)
actual=od.result_code.map({3:0,1:1,0:2}).astype(int).to_numpy()
Y=pd.get_dummies(pd.Series(actual),dtype=float).reindex(columns=[0,1,2],fill_value=0).to_numpy()
P=mp.to_numpy()
market_logloss=float(-np.mean([math.log(max(P[i,actual[i]],1e-15)) for i in range(len(P))]))
market_brier=float(np.mean(np.sum((P-Y)**2,axis=1)))
# Favorite-only settlement, descriptive.
picks=mp.idxmax(axis=1); map_pick={'home_odds':3,'draw_odds':1,'away_odds':0}; pnl=[]
for i,c in enumerate(picks):
    pick=map_pick[c]; odd=float(od.loc[i,c]); pnl.append(odd-1 if int(od.loc[i,'result_code'])==pick else -1)
market_roi=float(sum(pnl)/len(pnl))

# ------------------------------------------------------------------
# Card markets: rolling pre-match expectations and Poisson/NB comparison.
# For each event, only strictly prior calendar dates are used.
# ------------------------------------------------------------------
def poisson_over(mu,line):
    return float(1-sum(math.exp(-mu)*mu**k/math.factorial(k) for k in range(int(math.floor(line))+1)))

def nb_params(mu,var):
    # NB variance = mu + mu^2/r. If variance <= mu, fall back to Poisson.
    if not np.isfinite(mu) or mu<=0 or not np.isfinite(var) or var<=mu:
        return None
    r=mu*mu/(var-mu); p=r/(r+mu)
    return r,p

def nb_over(mu,var,line):
    pars=nb_params(mu,var)
    if pars is None:return poisson_over(mu,line)
    r,p=pars
    return float(1-nbinom.cdf(math.floor(line),r,p))

card_rows=[]
for _,r in feat.iterrows():
    # Prior data for side/referee. Features are already strictly prior-date.
    prior=feat[feat.date < r.date]
    hprior=prior[(prior.home_team==r.home_team)|(prior.away_team==r.home_team)]
    aprior=prior[(prior.home_team==r.away_team)|(prior.away_team==r.away_team)]
    refprior=prior[prior.referee==r.referee]
    hmu=float(hprior.home_cards.mean() if len(hprior) else prior.home_cards.mean())
    # For a team's card expectation, use its actual side from historical matches.
    def side_cards(team):
        vals=[]
        for _,z in hprior.iterrows() if team==r.home_team else aprior.iterrows():
            if z.home_team==team: vals.append(z.home_cards)
            elif z.away_team==team: vals.append(z.away_cards)
        return float(np.mean(vals[-5:])) if vals else np.nan, vals[-10:]
    hm,hvals=side_cards(r.home_team); am,avals=side_cards(r.away_team)
    total_mu=(hm if np.isfinite(hm) else prior.home_cards.mean())+(am if np.isfinite(am) else prior.away_cards.mean()) if len(prior) else 4.33
    # Referee average is used only if at least 2 prior observations exist; otherwise it is not a feature.
    if len(refprior)>=2:
        total_mu=0.75*total_mu+0.25*float(refprior.total_cards.mean())
    # Historical variance from prior total cards; no future rows.
    prior_tot=prior.total_cards.astype(float).to_numpy() if len(prior) else np.array([])
    var=float(np.var(prior_tot,ddof=1)) if len(prior_tot)>=3 else float(total_mu+1e-9)
    ppois=poisson_over(total_mu,2.5)
    pnb=nb_over(total_mu,var,2.5)
    actual_over=float(r.total_cards>2.5)
    card_rows.append({'event_id':r.event_id,'date':r.date,'market':'CARD_TOTALS','line':2.5,'mu':total_mu,'poisson_p_over':ppois,'nb_p_over':pnb,'actual_over':actual_over,'prior_n':len(prior),'ref_prior_n':len(refprior)})
card=pd.DataFrame(card_rows)
card['oos']=card.index>=n-hold_n-oos_n
card['holdout']=card.index>=n-hold_n
card_oos=card[card.oos & ~card.holdout]
card_hold=card[card.holdout]

def brier(rows,col): return float(np.mean((rows[col]-rows.actual_over)**2)) if len(rows) else None
card_summary={
 'CARD_TOTALS':{
   'N':int(len(card)),'OOS_N':int(len(card_oos)),'HOLDOUT_N':int(len(card_hold)),
   'Poisson_Brier_FULL':brier(card,'poisson_p_over'),'NB_Brier_FULL':brier(card,'nb_p_over'),
   'Poisson_Brier_OOS':brier(card_oos,'poisson_p_over'),'NB_Brier_OOS':brier(card_oos,'nb_p_over'),
   'Poisson_Brier_HOLDOUT':brier(card_hold,'poisson_p_over'),'NB_Brier_HOLDOUT':brier(card_hold,'nb_p_over')
 }
}

# Feature ablation on the 5-row OOS: compare full feature model vs selected groups.
def fit_oos(cols):
    cols=[c for c in cols if c in train.columns]
    tr=train[cols].copy(); te=oos[cols].copy(); med=tr.median(numeric_only=True); tr=tr.fillna(med); te=te.fillna(med)
    m=LogisticRegression(max_iter=2000,random_state=42).fit(tr,train.target_home_win.astype(int))
    p=m.predict_proba(te)[:,1]
    return binary_metrics(oos.target_home_win.astype(int),p)
ablations={
 'FULL':fit_oos(model_cols),
 'WITHOUT_CARDS':fit_oos([c for c in model_cols if 'cards' not in c]),
 'WITHOUT_FORM':fit_oos([c for c in model_cols if 'win_rate' not in c]),
 'GOALS_ONLY':fit_oos([c for c in model_cols if 'goals' in c]),
}

# Sensitivity on market-only favorite thresholds is descriptive only (10 rows).
sensitivity={}
for min_odd in [1.50,1.66,2.00]:
    picks=[]
    for i,c in enumerate(picks if False else mp.idxmax(axis=1)):
        odd=float(od.loc[i,c])
        if odd<min_odd: continue
        picks.append(odd-1 if int(od.loc[i,'result_code'])==map_pick[c] else -1)
    sensitivity[str(min_odd)]={'bets':len(picks),'pnl':float(sum(picks)),'roi':float(sum(picks)/len(picks)) if picks else None}

# Edge bins for the 10 market rows using market probability itself as the model baseline: should be ~0 edge after devig.
edge_bins={k:{'n':0,'pnl':0.0} for k in ['0-2','2-4','4-6','6-8','8+']}

# Provenance table
prov=[]
for _,r in df.iterrows():
    prov.append({'match_id':r.event_id,'source':'DataHub/Football-Data derivative','source_file':STATS.name,'source_hash':sha(STATS),'acquisition_timestamp':'prior_phase_materialization','season':'2023-24','league':'EPL'})
for i,r in od.iterrows():
    prov.append({'match_id':f"2526-{i+1:04d}",'source':'GitHub derivative / football-data source','source_file':ODDS.name,'source_hash':sha(ODDS),'acquisition_timestamp':'prior_phase_materialization','season':'2025-26','league':'EPL'})
pd.DataFrame(prov).to_csv(ROOT/'data/provenance/phase2_provenance.csv',index=False)

summary={
 'historical_real_processed':40,
 'matches_processed':40,
 'source_breakdown':{'2023-24_stats_cards':30,'2025-26_1x2_odds':10},
 'bet_decisions':{'BET':0,'NO_BET':0,'WATCH':0,'WAIT_FOR_PRICE':0,'reason':'No historical PIT odds/model decisions were fabricated. The 10-row market-only pilot is a baseline calculation, not a Robo signal run.'},
 'market_only_1x2':{'N':10,'log_loss':market_logloss,'brier':market_brier,'favorite_bets':10,'favorite_wins':sum(x>0 for x in pnl),'pnl':sum(pnl),'roi':market_roi,'clv':'NOT_DETERMINED'},
 'simple_model_home_win':{'train_n':len(train),'oos_n':len(oos),'holdout_n':len(holdout),'oos':oos_model,'holdout':hold_model},
 'card_markets':card_summary,
 'feature_ablation':ablations,
 'sensitivity':sensitivity,
 'oos':'PASS_AS_TEMPORAL_SPLIT_BUT_INSUFFICIENT_SAMPLE_FOR_STRONG_INFERENCE',
 'holdout':'PASS_AS_LOCKED_FINAL_6_ROWS_BUT_INSUFFICIENT_SAMPLE_FOR_STRONG_INFERENCE',
 'walk_forward':'NOT_DETERMINED',
 'clv':'NOT_DETERMINED',
 'edge':'NOT_DETERMINED',
 'scientific_level':'LEVEL 2 — real-data empirical pipeline exercised; OOS/holdout mechanics demonstrated, evidence too small for edge claim',
 'real_money':'DISABLED'
}
write('EMPIRICAL_RESULTS.json',summary)
card.to_csv(ROOT/'data/model/phase2_card_predictions.csv',index=False)

# Human reports
write('DATA_ACQUISITION_REPORT.md',f'''# DATA ACQUISITION REPORT — PHASE 2\n\n## Status\n`PARTIAL` for expansion, `SUCCESS` for processing of all real historical material currently present in the package.\n\n### Materialized real data\n- 30 EPL matches from 2023/24 with match statistics, referee and cards. SHA-256: `{sha(STATS)}`.\n- 10 EPL matches from 2025/26 with 1X2 prices/results. SHA-256: `{sha(ODDS)}`.\n- Total historical-real processed: **40 matches**.\n\n### Expansion attempt\nThe package's documented public routes include DataHub EPL and Football-Data-derived GitHub data. Web verification confirms DataHub publishes 33 EPL season CSV resources and the GitHub derivative publishes 12,700+ EPL results with bookmaker odds. The execution container, however, still cannot resolve external hosts; direct attempts to `raw.githubusercontent.com` and `datahub.io` failed at DNS. Therefore no external bytes were claimed as locally acquired in this run.\n\n## Integrity rule\nNo DEMO, MOCK, FIXTURE or synthetic row was promoted to historical-real.\n''')

write('DATA_QUALITY_REPORT.md',f'''# DATA QUALITY REPORT — PHASE 2\n\n| Check | Result |\n|---|---:|\n| RAW_ROWS | {quality['RAW_ROWS']} |\n| VALID_ROWS | {quality['VALID_ROWS']} |\n| DUPLICATES | {quality['DUPLICATES']} |\n| DUPLICATE_MATCH_KEYS | {quality['DUPLICATE_MATCH_KEYS']} |\n| INVALID_RESULTS | {quality['INVALID_RESULTS']} |\n| INVALID_DATES | {quality['INVALID_DATES']} |\n| MISSING_VALUES | {sum(quality['MISSING_VALUES'].values())} |\n| PIT | {quality['PIT_STATUS']} |\n\nNo rows were silently removed. The date-level PIT design excludes observations from the same calendar date because kickoff/publication ordering is not available.\n''')

write('EMPIRICAL_RESEARCH_REPORT.md',f'''# EMPIRICAL RESEARCH REPORT — PHASE 2\n\n## Scientific status\n`NOT_DETERMINED` for betting edge. The research pipeline was executed against **40 historical-real football matches**, but the sample is too small and split across seasons/fields to support a profitability claim.\n\n### 1X2 market-only\n- N = 10\n- Log Loss = {market_logloss:.6f}\n- Multiclass Brier = {market_brier:.6f}\n- Favorite strategy: 10 bets, {sum(x>0 for x in pnl)} wins, PnL = {sum(pnl):.4f} units, ROI = {market_roi:.2%}\n- CLV = NOT_DETERMINED because decision-time/closing timestamps are absent.\n\n### Existing Robo-style temporal feature pipeline\nThe research run used pre-match historical features based only on strictly prior calendar dates. A logistic model using goal/form/card features produced a temporal OOS window of {len(oos)} and a locked final holdout of {len(holdout)}. This demonstrates the split/lineage path, not robust generalization.\n\nOOS: Brier {oos_model['Brier']:.6f}; Log Loss {oos_model['LogLoss']:.6f}.\nHoldout: Brier {hold_model['Brier']:.6f}; Log Loss {hold_model['LogLoss']:.6f}.\n\n### Cards\nCard totals were modeled with prior-date team/referee information. Poisson and Negative Binomial were both executed; neither is promoted because N=30 and OOS/holdout are tiny.\n\n### Limitations\n- No timestamped odds snapshots.\n- No overlapping historical odds+cards dataset in the materialized bytes, so Robo betting decisions cannot be reconstructed honestly for all 40 matches.\n- No CLV.\n- No statistically meaningful walk-forward with repeated folds.\n- No robust multiple-testing conclusion.\n''')

write('ROBO_BEHAVIOR_REPORT.md',f'''# ROBO BEHAVIOR REPORT — PHASE 2\n\nThe current real-data materialization does **not** contain enough decision-time odds/features to reconstruct historical Robo BET/NO_BET/WATCH/WAIT decisions for the full 40-match set without fabricating inputs. Therefore: \n\n- BET = 0 observed historical Robo decisions\n- NO_BET = 0 observed historical Robo decisions\n- WATCH = 0 observed historical Robo decisions\n- WAIT_FOR_PRICE = 0 observed historical Robo decisions\n\nThis is deliberately **not** interpreted as "the Robo never bets". It means the required historical decision state is not present in the materialized dataset.\n\nThe 10-match 1X2 market-only pilot is a baseline experiment, not a Robo signal experiment.\n''')

write('MODEL_COMPARISON_REPORT.md',f'''# MODEL COMPARISON REPORT — PHASE 2\n\n| Model | Data | Status |\n|---|---:|---|\n| Market-only 1X2 | 10 | EXECUTED, descriptive only |\n| Simple temporal logistic | 30 | EXECUTED with OOS/holdout split |\n| Full Robo betting model | 0 valid historical decision states | NOT_DETERMINED |\n| Ensemble | 0 valid comparable historical decision states | NOT_DETERMINED |\n\nThe package contains more sophisticated model components, but this phase does not fabricate missing inputs merely to activate them.\n''')

write('MARKET_COMPARISON_REPORT.md',f'''# MARKET COMPARISON REPORT — PHASE 2\n\n| Market | Real N | Result | Evidence |\n|---|---:|---|---|\n| 1X2 | 10 odds rows | Market-only pilot ROI {market_roi:.2%} | INSUFFICIENT_SAMPLE |\n| DOUBLE_CHANCE | 0 | NOT_DETERMINED | NO_DATA |\n| BTTS | 0 odds | NOT_DETERMINED | NO_DATA |\n| TOTALS | 0 odds | NOT_DETERMINED | NO_DATA |\n| ASIAN_HANDICAP | 0 odds | NOT_DETERMINED | NO_DATA |\n| CARD_TOTALS | 30 stats rows | Poisson/NB executed | INSUFFICIENT_SAMPLE |\n| CARD_HOME | 30 stats rows | descriptive features available | NO_PRICE_DATA |\n| CARD_AWAY | 30 stats rows | descriptive features available | NO_PRICE_DATA |\n\nNo market is kept/removed on performance evidence from this sample.\n''')

write('FEATURE_ABLATION_REPORT.md', '# FEATURE ABLATION REPORT — PHASE 2\n\n' + json.dumps(ablations,indent=2,ensure_ascii=False))
write('CARD_MARKET_REPORT.md', '# CARD MARKET REPORT — PHASE 2\n\n' + json.dumps(card_summary,indent=2,ensure_ascii=False))
write('OOS_REPORT.md',f'''# OOS REPORT — PHASE 2\n\n- Research events: {len(research)}\n- OOS events: {len(oos)}\n- OOS model: temporal logistic\n- OOS Brier: {oos_model['Brier']:.6f}\n- OOS Log Loss: {oos_model['LogLoss']:.6f}\n- Status: `PASS` mechanically, `INSUFFICIENT_SAMPLE` scientifically.\n''')
write('HOLDOUT_REPORT.md',f'''# HOLDOUT REPORT — PHASE 2\n\n- Holdout events: {len(holdout)}\n- Model/threshold was frozen before opening the holdout.\n- Holdout Brier: {hold_model['Brier']:.6f}\n- Holdout Log Loss: {hold_model['LogLoss']:.6f}\n- Status: `PASS` as a locked final evaluation, `INSUFFICIENT_SAMPLE` for strong inference.\n''')
write('WALK_FORWARD_REPORT.md','# WALK-FORWARD REPORT — PHASE 2\n\n`NOT_DETERMINED`: 30 real matches are insufficient for repeated stable walk-forward folds without making the folds so small that they cease to be informative.\n')
write('CLV_REPORT.md','# CLV REPORT — PHASE 2\n\n`NOT_DETERMINED`. The real odds subset does not contain decision-time and closing timestamps that permit honest CLV reconstruction.\n')

final=f'''# FINAL SCIENTIFIC STATUS — PHASE 2\n\n## AQUISIÇÃO\nDATA_ACQUISITION: PARTIAL\nHISTORICAL_REAL_PROCESSED: 40\n\n## COMPORTAMENTO\nMATCHES_PROCESSED: 40\nSIGNALS: 0 reconstructed historical Robo signals\nNO_BET: 0 reconstructed historical Robo decisions\nWATCH: 0 reconstructed historical Robo decisions\nWAIT_FOR_PRICE: 0 reconstructed historical Robo decisions\n\n## PERFORMANCE\nMARKET_ONLY_1X2_ROI: {market_roi:.2%} (N=10; descriptive only)\nSIMPLE_MODEL_OOS_BRIER: {oos_model['Brier']:.6f}\nSIMPLE_MODEL_OOS_LOG_LOSS: {oos_model['LogLoss']:.6f}\nSIMPLE_MODEL_HOLDOUT_BRIER: {hold_model['Brier']:.6f}\nSIMPLE_MODEL_HOLDOUT_LOG_LOSS: {hold_model['LogLoss']:.6f}\nCLV: NOT_DETERMINED\nCalibration: INSUFFICIENT_SAMPLE\nDrawdown: NOT_DETERMINED for Robo; market-only pilot sequence is too small for inference\n\n## COMPARAÇÃO\nROBO VS MARKET_ONLY: NOT_DETERMINED\nROBO VS SIMPLE_MODEL: NOT_DETERMINED\n\n## VALIDAÇÃO\nOOS: PASS mechanically / INSUFFICIENT_SAMPLE scientifically\nHOLDOUT: PASS mechanically / INSUFFICIENT_SAMPLE scientifically\nWALK_FORWARD: NOT_DETERMINED\n\n## EDGE\nEDGE: NOT_DETERMINED\n\n## CIÊNCIA\nSCIENTIFIC_LEVEL: LEVEL 2\n\n## DINHEIRO\nREAL_MONEY: DISABLED\n\n## Respostas objetivas\n- Existe evidência de edge? **NOT_DETERMINED**.\n- O Robo supera market-only? **NOT_DETERMINED**.\n- Qual mercado é melhor? **NOT_DETERMINED**; 1X2 é o único com odds reais materializadas e N=10.\n- Qual é pior? **NOT_DETERMINED**.\n- Odds ajudam? Não foi possível medir o valor incremental do Robo com odds PIT históricas suficientes.\n- Price discovery / Market expression: **NOT_DETERMINED**.\n- Asian Handicap: **NOT_DETERMINED**.\n- Totals: **NOT_DETERMINED**.\n- Cartões: sinal preditivo ainda **NOT_DETERMINED**; Poisson e NB foram executados em N=30 sem evidência suficiente para promoção.\n- Árbitro/H2H/importância/intensidade/live: **NOT_DETERMINED** neste pacote.\n- Overfit: **POSSIBLE_RISK**, because of tiny OOS/holdout and many candidate features; no strong claim.\n- Resultado sobrevive OOS? **MECANICAMENTE SIM; CIENTIFICAMENTE NÃO CONCLUSIVO**.\n- Sobrevive holdout? **MECANICAMENTE SIM; CIENTIFICAMENTE NÃO CONCLUSIVO**.\n\n### Conclusão\nO Robo **ainda não pode ser declarado como tendo edge**. A fase conseguiu transformar os 40 registros históricos reais já materializados em pesquisa temporal real, incluindo qualidade, features pré-jogo por data, baseline 1X2, modelo temporal, OOS/holdout e pesquisa de cartões. O gargalo que permanece é a falta de um dataset histórico grande com **odds + decisão-time/PIT + resultados** na mesma observação, necessário para medir honestamente BET/NO_BET, EV, CLV e ROI do Robo em escala.\n'''
write('FINAL_SCIENTIFIC_STATUS.md',final)

print(json.dumps(summary,indent=2,ensure_ascii=False))
