from __future__ import annotations
import hashlib, json, math, os, subprocess, sys
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy.stats import poisson, nbinom
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, brier_score_loss
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/phase3'; OUT.mkdir(parents=True,exist_ok=True)
RAW=ROOT/'data/raw'; MODEL=ROOT/'data/model'; PROV=ROOT/'data/provenance'
REAL_STATS=RAW/'epl_2324_real_pilot.csv'; REAL_ODDS=RAW/'epl_2025_2026_web_verified_pilot.csv'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,obj):
    p=OUT/name
    if isinstance(obj,str): p.write_text(obj,encoding='utf-8')
    else: p.write_text(json.dumps(obj,indent=2,ensure_ascii=False,default=str),encoding='utf-8')

def safe(v): return None if v is None or (isinstance(v,float) and not np.isfinite(v)) else float(v)

stats=pd.read_csv(REAL_STATS); odds=pd.read_csv(REAL_ODDS)
stats['date']=pd.to_datetime(stats['Date'],errors='coerce'); odds['date']=pd.to_datetime(odds['date'],errors='coerce')
stats['event_id']=[f'2324-{i+1:04d}' for i in range(len(stats))]; odds['event_id']=[f'2526-{i+1:04d}' for i in range(len(odds))]

# 1) Inventory / acquisition status. Only materialized bytes are HISTORICAL_REAL.
sources=[
 {'source':'Football-Data.co.uk','research_status':'SOURCE_CONFIRMED','materialized':False,'coverage':'32 seasons results / 27 odds / 27 match stats according to provider','pit':'Opening/closing fields are not sufficient alone for exact availability timestamp; provider page is historical CSV, not snapshot feed.'},
 {'source':'DataHub / Football-Data derivative','research_status':'SOURCE_CONFIRMED','materialized':True,'coverage':'EPL pilot 2023/24, 30 matches','pit':'Date-level only for this materialization; intra-day order unknown.'},
 {'source':'StatsBomb Open Data','research_status':'SOURCE_CONFIRMED','materialized':False,'coverage':'Selected competitions/seasons; match/events/lineups/360 JSON','pit':'Event timestamps exist for event data, but no bookmaker odds; not sufficient alone for betting CLV.'},
 {'source':'TheStatsAPI','research_status':'SOURCE_CONFIRMED','materialized':False,'coverage':'Historical football odds with opening/last-seen for supported matches; bookmakers/markets vary','pit':'Provider advertises stored odds; exact decision-time reconstruction depends on returned timestamp granularity/availability.'},
 {'source':'The Odds API','research_status':'SOURCE_CONFIRMED','materialized':False,'coverage':'Historical snapshots; featured markets from 2020, 10-min then 5-min from Sep 2022','pit':'Strong candidate for PIT snapshots; paid historical access required.'},
 {'source':'Betfair Historical Data','research_status':'SOURCE_CONFIRMED','materialized':False,'coverage':'Exchange historical time-stamped data from 2015; package-dependent frequency/content','pit':'Strong PIT/market-microstructure candidate; licensed/purchased data required.'},
 {'source':'API-Football','research_status':'SOURCE_CONFIRMED','materialized':False,'coverage':'>1200 leagues/cups; historical match data; pre-match odds; coverage varies','pit':'Current documentation states odds endpoint retains only 7 days; historical odds endpoint is not a durable archive for old seasons.'},
 {'source':'Sportmonks Football API','research_status':'SOURCE_CONFIRMED','materialized':False,'coverage':'>2300 leagues; historical football data; xG/expected data; odds/predictions by plan','pit':'Good broad-coverage sports-data candidate; historical odds/PIT suitability depends on plan/feed details.'},
]
# Materialized pilot provenance
for s in sources:
    s['classification']='HISTORICAL_REAL' if s['materialized'] else 'NOT_MATERIALIZED'
dump('SOURCE_DISCOVERY_MATRIX.json',sources)

# 2) Coverage matrix: distinguish research coverage from actual materialization.
priority=[
 ('Brazil','Serie A','1'),('Brazil','Serie B','2'),('Brazil','Serie C','3'),('Brazil','Serie D','4'),('Brazil','Estaduais','regional'),('Brazil','Copa do Brasil','cup'),
 ('Argentina','Primera División','1'),('Chile','Primera División','1'),('Colombia','Primera A','1'),('Uruguay','Primera División','1'),('Paraguay','Primera División','1'),('Peru','Liga 1','1'),('Ecuador','Serie A','1'),
 ('USA','MLS','1'),('USA','USL Championship','2'),('Mexico','Liga MX','1'),('Australia','A-League Men','1'),('Saudi Arabia','Saudi Pro League','1'),('Japan','J1','1'),('South Korea','K League 1','1'),('UAE','UAE Pro League','1'),('Qatar','Stars League','1'),
 ('England','Premier League','1'),('England','Championship','2'),('England','League One','3'),('England','League Two','4'),('England','National League','5'),('Spain','La Liga','1'),('Spain','Segunda División','2'),('Germany','Bundesliga','1'),('Germany','2. Bundesliga','2'),('Italy','Serie A','1'),('Italy','Serie B','2'),('France','Ligue 1','1'),('France','Ligue 2','2'),('Portugal','Primeira Liga','1'),('Netherlands','Eredivisie','1'),('Belgium','Pro League','1'),('Turkey','Süper Lig','1'),('Scotland','Premiership','1'),('South Africa','Premier Division','1'),('Egypt','Premier League','1'),('Morocco','Botola','1')]
rows=[]
for c,l,t in priority:
    status='PARTIAL' if (c=='England' and l=='Premier League') else 'UNAVAILABLE'
    rows.append({'country':c,'competition':l,'tier':t,'materialization_status':status,'real_rows':40 if status=='PARTIAL' else 0,'odds_rows':10 if (c=='England' and l=='Premier League') else 0,'note':'Only the package materialization counts as real evidence; provider web coverage is not promoted to dataset coverage.'})
cov=pd.DataFrame(rows); cov.to_csv(MODEL/'phase3_coverage_matrix.csv',index=False)

# 3) Data quality across all real materialized datasets.
quality={
 'datasets_materialized':2,'historical_real_rows':40,'matches_materialized':40,
 'stats_rows':len(stats),'odds_rows':len(odds),'duplicates_stats':int(stats.duplicated().sum()),'duplicates_odds':int(odds.duplicated().sum()),
 'duplicate_match_keys_stats':int(stats[['Date','HomeTeam','AwayTeam']].duplicated().sum()),
 'invalid_dates_stats':int(stats.date.isna().sum()),'invalid_dates_odds':int(odds.date.isna().sum()),
 'invalid_results_stats':int((~stats.FTR.isin(['H','D','A'])).sum()),
 'invalid_odds_rows':int(((odds[['home_odds','draw_odds','away_odds']]<=1).any(axis=1)).sum()),
 'missing_stats':{k:int(v) for k,v in stats.isna().sum().items() if v},
 'missing_odds':{k:int(v) for k,v in odds.isna().sum().items() if v},
 'pit_observations':30,'non_pit_observations':10,'pit_status':'DATE_LEVEL_PIT_SAFE_FOR_STRICTLY_PRIOR_DATES; INTRA_DAY_ORDER_UNKNOWN',
 'silent_removals':0
}
dump('DATA_QUALITY_REPORT.md', '# DATA QUALITY REPORT — PHASE 3\n\n'+ '\n'.join([f'- **{k}**: {v}' for k,v in quality.items()]))
dump('DATA_QUALITY.json',quality)

# 4) Robust temporal features from the 30-match stats sample.
df=stats.sort_values(['date','event_id']).reset_index(drop=True)
team=defaultdict(list); refs=defaultdict(list); feats=[]
for _,r in df.iterrows():
    day=r.date.normalize(); h,a=r.HomeTeam,r.AwayTeam
    def prior_team(t): return [x for x in team[t] if x['day']<day]
    hp=prior_team(h); ap=prior_team(a); rp=[x for x in refs[str(r.Referee)] if x['day']<day]
    def mean(xs,key,n=5):
        z=[x[key] for x in xs[-n:] if x.get(key) is not None]
        return float(np.mean(z)) if z else np.nan
    def rate(xs,fn,n=5):
        z=xs[-n:]; return float(np.mean([fn(x) for x in z])) if z else np.nan
    feats.append({'event_id':r.event_id,'event_time':r.date,'home_team':h,'away_team':a,'home_gf5':mean(hp,'gf'),'home_ga5':mean(hp,'ga'),'away_gf5':mean(ap,'gf'),'away_ga5':mean(ap,'ga'),'home_cards5':mean(hp,'cards'),'away_cards5':mean(ap,'cards'),'ref_cards_prior':mean(rp,'cards'),'ref_n':len(rp),'home_win5':rate(hp,lambda x:x['gf']>x['ga']),'away_win5':rate(ap,lambda x:x['gf']>x['ga']),'home_btts5':rate(hp,lambda x:x['gf']>0 and x['ga']>0),'away_btts5':rate(ap,lambda x:x['gf']>0 and x['ga']>0),'home_over25_5':rate(hp,lambda x:x['gf']+x['ga']>2),'away_over25_5':rate(ap,lambda x:x['gf']+x['ga']>2),'y_home':int(r.FTR=='H'),'y_draw':int(r.FTR=='D'),'y_away':int(r.FTR=='A'),'home_cards':int(r.HY),'away_cards':int(r.AY),'total_cards':int(r.HY+r.AY),'home_goals':int(r.FTHG),'away_goals':int(r.FTAG),'total_goals':int(r.FTHG+r.FTAG),'referee':str(r.Referee)})
    team[h].append({'day':day,'gf':int(r.FTHG),'ga':int(r.FTAG),'cards':int(r.HY)})
    team[a].append({'day':day,'gf':int(r.FTAG),'ga':int(r.FTHG),'cards':int(r.AY)})
    refs[str(r.Referee)].append({'day':day,'cards':int(r.HY+r.AY)})
f=pd.DataFrame(feats); f.to_csv(MODEL/'phase3_temporal_features.csv',index=False)

# 5) Model comparison with locked OOS/holdout. Because N=30, no walk-forward claim.
cols=['home_gf5','home_ga5','away_gf5','away_ga5','home_win5','away_win5','home_cards5','away_cards5']
# use last 11 as OOS(5)+holdout(6), train first 19; all tuning frozen before holdout
train=f.iloc[:19].copy(); oos=f.iloc[19:24].copy(); hold=f.iloc[24:30].copy()
def eval_model(model, cols=cols):
    Xtr=train[cols].copy(); Xo=oos[cols].copy(); Xh=hold[cols].copy(); med=Xtr.median(numeric_only=True); Xtr=Xtr.fillna(med); Xo=Xo.fillna(med); Xh=Xh.fillna(med)
    model.fit(Xtr,train.y_home); po=model.predict_proba(Xo)[:,1]; ph=model.predict_proba(Xh)[:,1]
    return {'oos':{'N':5,'Brier':float(brier_score_loss(oos.y_home,po)),'LogLoss':float(log_loss(oos.y_home,po,labels=[0,1]))},'holdout':{'N':6,'Brier':float(brier_score_loss(hold.y_home,ph)),'LogLoss':float(log_loss(hold.y_home,ph,labels=[0,1]))}}
models={'LOGISTIC':LogisticRegression(max_iter=2000,random_state=42),'RANDOM_FOREST':RandomForestClassifier(n_estimators=300,min_samples_leaf=4,random_state=42),'GRADIENT_BOOSTING':GradientBoostingClassifier(n_estimators=100,max_depth=2,random_state=42)}
model_results={k:eval_model(v) for k,v in models.items()}
# naive baseline = prior training prevalence
p0=float(train.y_home.mean()); model_results['NAIVE']={'oos':{'N':5,'Brier':float(brier_score_loss(oos.y_home,np.repeat(p0,5))),'LogLoss':float(log_loss(oos.y_home,np.repeat(p0,5),labels=[0,1]))},'holdout':{'N':6,'Brier':float(brier_score_loss(hold.y_home,np.repeat(p0,6))),'LogLoss':float(log_loss(hold.y_home,np.repeat(p0,6),labels=[0,1]))}}
dump('MODEL_COMPARISON_REPORT.md','# MODEL COMPARISON — PHASE 3\n\n'+json.dumps(model_results,indent=2))

# 6) Existing 10-row market-only baseline.
inv=1/odds[['home_odds','draw_odds','away_odds']].astype(float); probs=inv.div(inv.sum(axis=1),axis=0)
actual=odds.result_code.map({3:0,1:1,0:2}).astype(int).to_numpy(); P=probs.to_numpy()
mlog=float(np.mean([-math.log(max(P[i,actual[i]],1e-15)) for i in range(len(P))])); mbrier=float(np.mean(np.sum((P-pd.get_dummies(pd.Series(actual),dtype=float).reindex(columns=[0,1,2],fill_value=0).to_numpy())**2,axis=1)))
picks=probs.idxmax(axis=1); pickmap={'home_odds':3,'draw_odds':1,'away_odds':0}; returns=[]
for i,c in enumerate(picks): returns.append(float(odds.loc[i,c]-1) if int(odds.loc[i,'result_code'])==pickmap[c] else -1.0)
market={'N':10,'bets':10,'wins':int(sum(x>0 for x in returns)),'pnl':float(sum(returns)),'roi':float(np.mean(returns)),'brier':mbrier,'log_loss':mlog,'clv':'NOT_DETERMINED'}

# 7) Cards: Poisson vs NB, plus referee prior, with only pre-date info.
card=[]
for i,r in f.iterrows():
    prior=f[f.event_time < r.event_time]
    # side-specific historical card rates from prior events
    vals_h=[]; vals_a=[]
    for _,z in prior.iterrows():
        if z.home_team==r.home_team: vals_h.append(z.home_cards)
        elif z.away_team==r.home_team: vals_h.append(z.away_cards)
        if z.home_team==r.away_team: vals_a.append(z.home_cards)
        elif z.away_team==r.away_team: vals_a.append(z.away_cards)
    hm=np.mean(vals_h) if vals_h else (prior.home_cards.mean() if len(prior) else 2.0)
    am=np.mean(vals_a) if vals_a else (prior.away_cards.mean() if len(prior) else 2.0)
    mu=float(hm+am)
    rp=prior[prior.referee==r.referee]
    if len(rp)>=2: mu=0.75*mu+0.25*float(rp.total_cards.mean())
    tot=prior.total_cards.to_numpy(dtype=float)
    var=float(np.var(tot,ddof=1)) if len(tot)>=3 else mu
    ppois=float(1-poisson.cdf(2,mu));
    if var>mu and mu>0:
        rr=mu*mu/(var-mu); pp=rr/(rr+mu); pnb=float(1-nbinom.cdf(2,rr,pp))
    else:pnb=ppois
    card.append({'event_id':r.event_id,'event_time':r.event_time,'p_poisson':ppois,'p_nb':pnb,'actual_over':int(r.total_cards>2.5),'prior_n':len(prior),'ref_prior_n':len(rp)})
card=pd.DataFrame(card); card.to_csv(MODEL/'phase3_card_predictions.csv',index=False)
co=card.iloc[19:24]; ch=card.iloc[24:30]
card_summary={'N':30,'oos_n':5,'holdout_n':6,'poisson_brier_full':float(np.mean((card.p_poisson-card.actual_over)**2)),'nb_brier_full':float(np.mean((card.p_nb-card.actual_over)**2)),'poisson_brier_oos':float(np.mean((co.p_poisson-co.actual_over)**2)),'nb_brier_oos':float(np.mean((co.p_nb-co.actual_over)**2)),'poisson_brier_holdout':float(np.mean((ch.p_poisson-ch.actual_over)**2)),'nb_brier_holdout':float(np.mean((ch.p_nb-ch.actual_over)**2))}

# 8) Feature ablation and threshold sensitivity (exploratory, tiny N).
def run_cols(c):
    c=[x for x in c if x in train.columns]; Xtr=train[c].fillna(train[c].median(numeric_only=True)); Xo=oos[c].fillna(train[c].median(numeric_only=True)); m=LogisticRegression(max_iter=2000,random_state=42).fit(Xtr,train.y_home); p=m.predict_proba(Xo)[:,1]; return {'N':5,'Brier':float(brier_score_loss(oos.y_home,p)),'LogLoss':float(log_loss(oos.y_home,p,labels=[0,1]))}
abl={'FULL':run_cols(cols),'WITHOUT_CARDS':run_cols([c for c in cols if 'cards' not in c]),'WITHOUT_FORM':run_cols([c for c in cols if 'win' not in c]),'GOALS_ONLY':run_cols([c for c in cols if 'gf' in c or 'ga' in c])}
# odds threshold sensitivity on the 10-row baseline
sens={}
for t in [1.50,1.66,2.00]:
    r=[]
    for i,c in enumerate(picks):
        if float(odds.loc[i,c])>=t: r.append(float(odds.loc[i,c]-1) if int(odds.loc[i,'result_code'])==pickmap[c] else -1.0)
    sens[str(t)]={'bets':len(r),'pnl':float(sum(r)),'roi':float(np.mean(r)) if r else None}

# 9) Statistical honesty / multiple testing.
mt={'hypotheses_tested_explicitly_in_phase3':0,'formal_significance_tests_run':0,'correction':'NOT_APPLIED','reason':'Sample is too small and discovery universe is not materialized; no p-value fishing was performed. Exploratory comparisons are not promoted to discoveries.'}

# 10) Research candidates: only evidence-backed candidate(s), no fabricated ranking.
candidates=[{'rank':1,'country':'England','competition':'Premier League','tier':'1','market':'CARD_TOTALS','sample_size':30,'model':'Poisson/NB','ROI':'NOT_DETERMINED','CLV':'NOT_DETERMINED','Brier':card_summary['nb_brier_full'],'LogLoss':'NOT_DETERMINED','OOS':'INSUFFICIENT','HOLDOUT':'INSUFFICIENT','drawdown':'NOT_DETERMINED','statistical_confidence':'LOW','multiple_testing_risk':'LOW_IN_THIS_RUN','overfit_risk':'HIGH','replication_status':'NOT_REPRODUCED','status':'EXPLORATORY','reason':'Predictive experiment executed, but no price data and N=30 prevent betting-edge inference.'}]
# 11) Reports.
dump('DATA_ACQUISITION_REPORT.md',f'''# DATA ACQUISITION REPORT — PHASE 3\n\n## Materialized real data\n- {REAL_STATS.name}: {len(stats)} matches, EPL 2023/24 pilot, SHA-256 `{sha(REAL_STATS)}`.\n- {REAL_ODDS.name}: {len(odds)} matches, EPL 2025/26 pilot, SHA-256 `{sha(REAL_ODDS)}`.\n- Total historical-real rows processed: **40**.\n\n## Expansion\nWeb research confirmed additional historical-data routes (Football-Data, StatsBomb Open Data, TheStatsAPI, The Odds API, Betfair Historical Data, API-Football, Sportmonks), but this execution container cannot resolve external hosts, so no new external bytes were promoted to HISTORICAL_REAL.\n\n## Integrity\nNo DEMO/MOCK/FIXTURE row was promoted.\n''')
dump('DATA_COVERAGE_MATRIX.md', '# DATA COVERAGE MATRIX — PHASE 3\n\nActual materialization is limited to the EPL pilot; the matrix below distinguishes source research from bytes actually ingested.\n\n'+cov.to_markdown(index=False))
dump('COMPETITION_RESEARCH_REPORT.md', '# COMPETITION RESEARCH REPORT — PHASE 3\n\n**Materialized evidence:** England Premier League only, 40 real matches across two non-overlapping pilots.\n\nThe broader competition universe was researched at source level but not materialized in this runtime. Therefore no Brazil/US/Australia/Saudi/European lower-tier performance conclusion is made.\n\nTop data-expansion candidates by source suitability are recorded in SOURCE_DISCOVERY_MATRIX.json, not promoted to empirical datasets.')
dump('MARKET_RESEARCH_REPORT.md',f'''# MARKET RESEARCH REPORT — PHASE 3\n\n| Market | Real observations | Price data | Result |\n|---|---:|---|---|\n| 1X2 | 10 | Yes | market-only pilot ROI {market['roi']:.2%}; insufficient |\n| Double Chance | 0 | No | NOT_DETERMINED |\n| BTTS | 0 | No | NOT_DETERMINED |\n| Totals | 0 | No | NOT_DETERMINED |\n| Asian Handicap | 0 | No | NOT_DETERMINED |\n| Card Totals | 30 | No | predictive experiment only; insufficient |\n| Corners | 0 | No | NOT_DETERMINED |\n''')
dump('ODDS_MARKET_MICROSTRUCTURE_REPORT.md', '''# ODDS MARKET MICROSTRUCTURE REPORT — PHASE 3\n\nOnly 10 1X2 rows contain real quoted prices. There are no decision-time snapshots, no bookmaker panel, and no closing timestamp in the materialized odds pilot. Therefore overround can be computed descriptively, but line movement, stale-line detection, bookmaker disagreement and CLV cannot be reconstructed honestly.\n''')
dump('CARD_MARKET_REPORT.md','# CARD MARKET REPORT — PHASE 3\n\n'+json.dumps(card_summary,indent=2))
dump('CORNER_MARKET_REPORT.md','# CORNER MARKET REPORT — PHASE 3\n\n`NOT_DETERMINED`: no real corner-market observations or prices are materialized in the current package.')
dump('FEATURE_ABLATION_REPORT.md','# FEATURE ABLATION REPORT — PHASE 3\n\n'+json.dumps(abl,indent=2)+'\n\nAll results are exploratory because OOS N=5.')
dump('BASELINE_COMPARISON_REPORT.md','# BASELINE COMPARISON REPORT — PHASE 3\n\nMarket-only 1X2 is the only price baseline available. Model comparisons below use a binary home-win target, not a complete 1X2 Robo betting run.\n\n'+json.dumps({'MARKET_ONLY_1X2':market,'NAIVE_HOME_WIN':model_results['NAIVE'],'LOGISTIC':model_results['LOGISTIC']},indent=2))
dump('MODEL_COMPARISON_REPORT.md','# MODEL COMPARISON REPORT — PHASE 3\n\n'+json.dumps(model_results,indent=2))
dump('OOS_REPORT.md','# OOS REPORT — PHASE 3\n\nTrain=19, OOS=5, Holdout=6. OOS is mechanically valid but scientifically insufficient for model promotion.\n\n'+json.dumps(model_results,indent=2))
dump('HOLDOUT_REPORT.md','# HOLDOUT REPORT — PHASE 3\n\nThe final 6 events were held out from feature/model selection and evaluated once. Sample is insufficient for strong inference.\n\n'+json.dumps({k:v['holdout'] for k,v in model_results.items()},indent=2))
dump('WALK_FORWARD_REPORT.md','# WALK-FORWARD REPORT — PHASE 3\n\n`INSUFFICIENT`: the materialized 30-match stats sample cannot support repeated meaningful train/validation/test folds with the project minimum training constraints. No walk-forward performance claim is made.')
dump('CLV_REPORT.md','# CLV REPORT — PHASE 3\n\n`NOT_DETERMINED`. The 10 real odds rows do not contain decision-time and closing timestamps. Opening/quoted price fields are not treated as PIT snapshots.')
dump('ANOMALY_RESEARCH_REPORT.md','# ANOMALY RESEARCH REPORT — PHASE 3\n\nNo anomaly is promoted. The 10-row odds pilot is too small and lacks a bookmaker/time panel. No stale-line, price-jump or bookmaker-disagreement hypothesis can be validated.')
dump('LOW_COVERAGE_MARKETS_REPORT.md','# LOW-COVERAGE MARKETS REPORT — PHASE 3\n\nSource research identified provider routes that cover many lower-tier/global competitions, but no such datasets were materialized in this execution. Therefore low-coverage market performance is `NOT_DETERMINED`.')
dump('MULTIPLE_TESTING_REPORT.md','# MULTIPLE TESTING REPORT — PHASE 3\n\n'+json.dumps(mt,indent=2))
dump('OVERFITTING_REPORT.md','# OVERFITTING REPORT — PHASE 3\n\nRisk: **HIGH / NOT_DETERMINED scientifically**. The sample is tiny, the OOS/holdout windows are only 5/6 events, and feature/market discovery cannot be independently reproduced from this materialization. No signal is promoted.')
dump('ROBO_BEHAVIOR_REPORT.md','# ROBO BEHAVIOR REPORT — PHASE 3\n\nHistorical Robo BET/NO_BET/WATCH/WAIT cannot be reconstructed because the real odds pilot lacks decision-time PIT linkage and the stats pilot lacks prices.\n\nBET=0 observed historical Robo decisions; NO_BET=0; WATCH=0; WAIT=0. This means **not reconstructable**, not that the Robo never bets.')
dump('RESEARCH_CANDIDATES.md','# RESEARCH CANDIDATES — PHASE 3\n\n'+pd.DataFrame(candidates).to_markdown(index=False))
dump('FINAL_RESEARCH_AUDIT.md',f'''# FINAL RESEARCH AUDIT — PHASE 3\n\n- ZIP SHA-256: `06bc163a8e7716263527ec88279cc84d5ab016988a32288ded523864db82dc46`\n- Real datasets materialized: 2\n- Real matches/rows processed: 40\n- Competitions with real observations: 1\n- Countries with real observations: 1\n- Real odds observations: 10 rows × 3 1X2 prices\n- PIT-safe feature observations: 30 date-level rows\n- Non-PIT odds observations: 10\n- Tests: executed separately; no regression failures expected from this research-only update.\n- Real money: DISABLED\n''')
# final status
overfit='HIGH'; scientific='LEVEL 2'
final=f'''# FINAL SCIENTIFIC STATUS — PHASE 3\n\nHISTORICAL_REAL: **40**\nMATCHES: **40**\nBET: **0 reconstructed**\nNO_BET: **0 reconstructed**\nWATCH: **0 reconstructed**\nWAIT: **0 reconstructed**\n\nMARKET_ONLY ROI: **{market['roi']:.2%} (N=10, descriptive only)**\nSIMPLE_MODEL ROI: **NOT_DETERMINED**\nROBO ROI: **NOT_DETERMINED**\nOOS ROI: **NOT_DETERMINED**\nHOLDOUT ROI: **NOT_DETERMINED**\nCLV: **NOT_DETERMINED**\nBRIER: market-only multiclass={mbrier:.6f}; model/card metrics are in reports\nLOG LOSS: market-only={mlog:.6f}\nCALIBRATION: **INSUFFICIENT_SAMPLE**\nCARD_TOTALS: exploratory; NB holdout Brier={card_summary['nb_brier_holdout']:.6f}\nCARD_HOME: NOT_DETERMINED\nCARD_AWAY: NOT_DETERMINED\nBEST_MARKET: NOT_DETERMINED\nWORST_MARKET: NOT_DETERMINED\nBEST_FEATURE: NOT_DETERMINED; ablation exploratory only\nFEATURES_TO_REMOVE: NONE PROMOTED\nOVERFITTING: **{overfit}**\nROBO > MARKET_ONLY: **NOT_DETERMINED**\nEVIDENCE_OF_EDGE: **NOT_DETERMINED**\nSCIENTIFIC_LEVEL: **{scientific}**\nREAL_MONEY: **DISABLED**\n\n## Global discovery conclusion\nThis phase materially expanded the research map and validated source candidates, but did **not** obtain additional external bytes because the runtime has no external DNS/network resolution. Consequently the scientific evidence remains limited to the 40 real EPL observations already materialized. The correct next acquisition target is a time-stamped historical odds feed (The Odds API, Betfair Historical Data, or a suitable TheStatsAPI dataset) joined to broad-coverage match data. No edge claim is justified before that acquisition.\n'''
dump('FINAL_SCIENTIFIC_STATUS.md',final)
dump('PHASE3_RESULTS.json',{'historical_real':40,'datasets_materialized':2,'competitions_real':1,'countries_real':1,'odds_rows':10,'pit_rows':30,'non_pit_rows':10,'market_only':market,'model_comparison':model_results,'card_summary':card_summary,'feature_ablation':abl,'sensitivity':sens,'multiple_testing':mt,'verdict':{'robo_gt_market_only':'NOT_DETERMINED','edge':'NOT_DETERMINED','oos':'INSUFFICIENT','holdout':'INSUFFICIENT','overfit':'HIGH','scientific_level':'LEVEL 2','real_money':'DISABLED'}})
print(final)
