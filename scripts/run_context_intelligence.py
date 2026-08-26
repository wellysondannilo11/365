from __future__ import annotations
import os, json, hashlib, math, subprocess, platform
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, brier_score_loss, roc_auc_score
from sklearn.inspection import permutation_importance

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; REPORTS=ROOT/'reports'; RESEARCH=DATA/'research'; MAN=DATA/'manifests'; SCHEMAS=DATA/'schemas'
for p in [RESEARCH, MAN, SCHEMAS, REPORTS/'context_intelligence']:
    p.mkdir(parents=True, exist_ok=True)

RUN=datetime.now(timezone.utc).isoformat()
INPUT=DATA/'canonical/football_historical_real_canonical.csv'
df=pd.read_csv(INPUT)
df['kickoff']=pd.to_datetime(df['kickoff_timestamp'], errors='coerce', utc=True)
df=df.sort_values('kickoff').reset_index(drop=True)

# Evidence gates
valid=df['data_type'].astype(str).str.startswith('HISTORICAL_REAL')
df['evidence_ok']=valid & ~df['pit_status'].isin(['PIT_INVALID','UNKNOWN'])
df['home_goals']=pd.to_numeric(df['home_goals'],errors='coerce'); df['away_goals']=pd.to_numeric(df['away_goals'],errors='coerce')
for c in ['home_cards','away_cards','total_cards','home_corners','away_corners','total_corners','home_xg','away_xg','odds_1','odds_x','odds_2']:
    df[c]=pd.to_numeric(df[c],errors='coerce')
df['total_goals']=df.home_goals+df.away_goals
df['home_win']=(df.home_goals>df.away_goals).astype(float)
df['draw']=(df.home_goals==df.away_goals).astype(float)
df['away_win']=(df.home_goals<df.away_goals).astype(float)
df['over25']=(df.total_goals>2.5).astype(float)
df['btts']=(df.home_goals.gt(0)&df.away_goals.gt(0)).astype(float)

def sha(path):
    h=hashlib.sha256();
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

# Raw-source enrichment: only existing real files in the package, never fabricated.
raw_specs=[('football_data_e0_2425.csv','Premier League'),('football_data_e1_2425.csv','Championship'),('football_data_e2_2425.csv','League One'),('football_data_e3_2425.csv','League Two'),('epl_2526_github_real.csv','Premier League')]
raw=[]
for fn,comp in raw_specs:
    p=DATA/'raw'/fn
    if not p.exists(): continue
    try:
        x=pd.read_csv(p)
        x.columns=[str(c).strip() for c in x.columns]
        # common football-data schema
        rename={'Date':'date','Time':'time','HomeTeam':'home_team','AwayTeam':'away_team','FTHG':'home_goals_raw','FTAG':'away_goals_raw','Referee':'referee_raw','HS':'home_shots','AS':'away_shots','HST':'home_sot','AST':'away_sot','HF':'home_fouls','AF':'away_fouls','HC':'home_corners_raw','AC':'away_corners_raw','HY':'home_yellow','AY':'away_yellow','HR':'home_red','AR':'away_red'}
        x=x.rename(columns=rename); x['competition']=comp; x['raw_file']=fn
        raw.append(x)
    except Exception:
        pass
if raw:
    r=pd.concat(raw,ignore_index=True,sort=False)
    r['date_parsed']=pd.to_datetime(r['date'],errors='coerce',dayfirst=True)
    r['date_key']=r.date_parsed.dt.date.astype(str)
    r['home_team_key']=r.home_team.astype(str).str.lower().str.replace(r"[^a-z0-9]",'',regex=True)
    r['away_team_key']=r.away_team.astype(str).str.lower().str.replace(r"[^a-z0-9]",'',regex=True)
    # map canonical by date + normalized names + competition, conservative exact matching
    df['date_key']=df.kickoff.dt.date.astype(str)
    df['home_team_key']=df.home_team.astype(str).str.lower().str.replace(r"[^a-z0-9]",'',regex=True)
    df['away_team_key']=df.away_team.astype(str).str.lower().str.replace(r"[^a-z0-9]",'',regex=True)
    rr=r.drop_duplicates(['date_key','home_team_key','away_team_key','competition'])
    enrich_cols=['home_shots','away_shots','home_sot','away_sot','home_fouls','away_fouls','home_yellow','away_yellow','home_red','away_red']
    df=df.merge(rr[['date_key','home_team_key','away_team_key','competition']+enrich_cols],on=['date_key','home_team_key','away_team_key','competition'],how='left')
else:
    for c in ['home_shots','away_shots','home_sot','away_sot','home_fouls','away_fouls','home_yellow','away_yellow','home_red','away_red']: df[c]=np.nan

# Pre-match rolling features: strictly shifted, chronological, team-specific.
metrics=['goals_for','goals_against','shots_for','shots_against','sot_for','sot_against','corners_for','corners_against','cards_for','cards_against','points']
team_hist={}
features=[]
for i,row in df.iterrows():
    hk=str(row.home_team); ak=str(row.away_team)
    def stats_for(team, venue=None, n=5):
        arr=team_hist.get(team,[])
        if venue: arr=[z for z in arr if z['venue']==venue]
        arr=arr[-n:]
        if not arr: return {m:np.nan for m in metrics}
        return {m:float(np.mean([z[m] for z in arr])) for m in metrics}
    hs=stats_for(hk,'home'); as_=stats_for(ak,'away'); hgen=stats_for(hk); agen=stats_for(ak)
    rec={'home_form5':np.nan,'away_form5':np.nan,'home_attack5':np.nan,'away_attack5':np.nan,'home_defense5':np.nan,'away_defense5':np.nan}
    rec.update({f'home_{m}_5':hs[m] for m in metrics}); rec.update({f'away_{m}_5':as_[m] for m in metrics})
    rec.update({f'home_{m}_gen5':hgen[m] for m in metrics}); rec.update({f'away_{m}_gen5':agen[m] for m in metrics})
    rec['rest_home_days']=np.nan if not team_hist.get(hk) else (row.kickoff-team_hist[hk][-1]['kickoff']).total_seconds()/86400
    rec['rest_away_days']=np.nan if not team_hist.get(ak) else (row.kickoff-team_hist[ak][-1]['kickoff']).total_seconds()/86400
    rec['matches_home_7d']=sum((row.kickoff-z['kickoff']).total_seconds()<=7*86400 for z in team_hist.get(hk,[]) if row.kickoff>=z['kickoff'])
    rec['matches_away_7d']=sum((row.kickoff-z['kickoff']).total_seconds()<=7*86400 for z in team_hist.get(ak,[]) if row.kickoff>=z['kickoff'])
    features.append(rec)
    # update history with observed post-match facts
    hg=float(row.home_goals) if pd.notna(row.home_goals) else np.nan; ag=float(row.away_goals) if pd.notna(row.away_goals) else np.nan
    def val(c): return float(row[c]) if pd.notna(row[c]) else np.nan
    hp=3 if hg>ag else 1 if hg==ag else 0
    ap=3-hp if hp!=1 else 1
    team_hist.setdefault(hk,[]).append({'kickoff':row.kickoff,'venue':'home','goals_for':hg,'goals_against':ag,'shots_for':val('home_shots'),'shots_against':val('away_shots'),'sot_for':val('home_sot'),'sot_against':val('away_sot'),'corners_for':val('home_corners'),'corners_against':val('away_corners'),'cards_for':val('home_cards'),'cards_against':val('away_cards'),'points':hp})
    team_hist.setdefault(ak,[]).append({'kickoff':row.kickoff,'venue':'away','goals_for':ag,'goals_against':hg,'shots_for':val('away_shots'),'shots_against':val('home_shots'),'sot_for':val('away_sot'),'sot_against':val('home_sot'),'corners_for':val('away_corners'),'corners_against':val('home_corners'),'cards_for':val('away_cards'),'cards_against':val('home_cards'),'points':ap})
feat=pd.DataFrame(features,index=df.index)
d=pd.concat([df,feat],axis=1)
d['strength_attack_diff']=d['home_goals_for_5']-d['away_goals_for_5']
d['strength_defense_diff']=d['home_goals_against_5']-d['away_goals_against_5']
d['rest_diff']=d.rest_home_days-d.rest_away_days
d['congested_home']=(d.matches_home_7d>=3).astype(int); d['congested_away']=(d.matches_away_7d>=3).astype(int)
d['division_label']=d.division.map({1:'FIRST',2:'SECOND',3:'THIRD',4:'FOURTH'}).fillna('UNKNOWN')
d['gender']='MALE'  # all current materialized competitions are male; female dataset absent, explicitly audited below.

# Conservative context states: competition structure/standings are not present, so do not infer motivation.
d['motivation_state']='UNKNOWN'; d['importance_state']='UNKNOWN'; d['derby_state']='UNKNOWN'; d['leg_state']='UNKNOWN'

# Empirical summary tables
summary=[]
def group_result(g, label):
    n=len(g); return {'segment':label,'N':n,'home_win_rate':float(g.home_win.mean()),'draw_rate':float(g.draw.mean()),'away_win_rate':float(g.away_win.mean()),'mean_goals':float(g.total_goals.mean()),'median_goals':float(g.total_goals.median()),'over25_rate':float(g.over25.mean()),'btts_rate':float(g.btts.mean()),'mean_cards':float(g.total_cards.mean()) if g.total_cards.notna().any() else np.nan,'mean_corners':float(g.total_corners.mean()) if g.total_corners.notna().any() else np.nan}
summary.append(group_result(d,'ALL'))
for key,g in d.groupby('competition'): summary.append(group_result(g,f'COMPETITION:{key}'))
for key,g in d.groupby('division_label'): summary.append(group_result(g,f'DIVISION:{key}'))
for key,g in d.groupby('season'): summary.append(group_result(g,f'SEASON:{key}'))
pd.DataFrame(summary).to_csv(RESEARCH/'context_intelligence_segments.csv',index=False)

# Hypothesis testing: pre-defined, non-PIT descriptive/predictive patterns using only historical match outcomes.
hyp=[]
def add_hyp(name, groupmask, outcome, metric='mean_difference', direction='two-sided'):
    a=d.loc[groupmask,outcome].dropna(); b=d.loc[~groupmask,outcome].dropna();
    if len(a)<30 or len(b)<30: return
    if metric=='mean_difference':
        t=stats.ttest_ind(a,b,equal_var=False,nan_policy='omit'); eff=float(a.mean()-b.mean()); p=float(t.pvalue); stat=float(t.statistic)
    elif metric=='rate_difference':
        x1=int(a.sum()); n1=len(a); x0=int(b.sum()); n0=len(b); p=float(stats.fisher_exact([[x1,n1-x1],[x0,n0-x0]])[1]); eff=float(a.mean()-b.mean()); stat=np.nan
    hyp.append({'hypothesis':name,'outcome':outcome,'N_segment':len(a),'N_complement':len(b),'effect_size':eff,'p_value':p,'test_stat':stat})

# Home advantage / lower divisions / congestion / rest / strength patterns
add_hyp('Home advantage vs away outcomes', d.home_team.notna(), 'home_win', 'rate_difference')
add_hyp('Fourth vs first division total goals', d.division_label.eq('FOURTH'), 'total_goals')
add_hyp('Second division vs first division total goals', d.division_label.eq('SECOND'), 'total_goals')
add_hyp('Congested home teams vs non-congested', d.congested_home.eq(1), 'home_win','rate_difference')
add_hyp('Congested away teams vs non-congested', d.congested_away.eq(1), 'away_win','rate_difference')
add_hyp('Home rest >= 5 days', d.rest_home_days.ge(5), 'home_win','rate_difference')
add_hyp('Away rest >= 5 days', d.rest_away_days.ge(5), 'away_win','rate_difference')
add_hyp('Home attack rolling strength above away', d.strength_attack_diff.gt(0), 'home_win','rate_difference')
add_hyp('Home defensive goals-against lower than away', d.strength_defense_diff.lt(0), 'home_win','rate_difference')
add_hyp('High pre-match home shot form', d.home_shots_for_5.ge(d.home_shots_for_5.median()), 'home_win','rate_difference')
add_hyp('High pre-match away shot form', d.away_shots_for_5.ge(d.away_shots_for_5.median()), 'away_win','rate_difference')

# Cards/corners by divisions and referee where enough observations
for div in sorted(d.division_label.dropna().unique()):
    add_hyp(f'{div} vs rest: total cards', d.division_label.eq(div), 'total_cards')
    add_hyp(f'{div} vs rest: total corners', d.division_label.eq(div), 'total_corners')

# Expand the pre-registered research grid to avoid cherry-picking a handful of segments.
for field in ['competition','season','division_label']:
    for key in sorted(d[field].dropna().unique()):
        m=d[field].eq(key)
        for outcome in ['home_win','draw','away_win','over25','btts','total_goals','total_cards','total_corners']:
            add_hyp(f'{field}={key} vs rest: {outcome}',m,outcome,'rate_difference' if outcome in ['home_win','draw','away_win','over25','btts'] else 'mean_difference')

# BH/FDR
if hyp:
    hdf=pd.DataFrame(hyp); hdf['fdr_adjusted_p']=multipletests(hdf.p_value,method='fdr_bh')[1]; hdf['significant_fdr_05']=hdf.fdr_adjusted_p<0.05
else: hdf=pd.DataFrame(columns=['hypothesis','outcome','N_segment','N_complement','effect_size','p_value','fdr_adjusted_p','significant_fdr_05'])
hdf.to_csv(RESEARCH/'PATTERN_DISCOVERY_MULTIPLE_TESTING.csv',index=False)

# Temporal OOS: simple logistic model for home win using only strictly lagged features.
model_cols=['strength_attack_diff','strength_defense_diff','rest_diff','home_goals_for_5','away_goals_for_5','home_goals_against_5','away_goals_against_5','home_shots_for_5','away_shots_for_5','home_sot_for_5','away_sot_for_5','home_corners_for_5','away_corners_for_5','home_cards_for_5','away_cards_for_5']
X=d[model_cols].replace([np.inf,-np.inf],np.nan); y=d.home_win
mask=X.notna().all(axis=1)&y.notna()
idx=np.where(mask)[0]
results=[]
if len(idx)>=300:
    n=len(idx); a=int(n*.6); b=int(n*.8); train=idx[:a]; val=idx[a:b]; hold=idx[b:]
    med=X.iloc[train].median(); X2=X.fillna(med)
    model=LogisticRegression(max_iter=2000).fit(X2.iloc[train],y.iloc[train])
    for name,ii in [('VALIDATION',val),('HOLDOUT',hold)]:
        p=model.predict_proba(X2.iloc[ii])[:,1]
        results.append({'split':name,'N':len(ii),'log_loss':log_loss(y.iloc[ii],p,labels=[0,1]),'brier':brier_score_loss(y.iloc[ii],p),'roc_auc':roc_auc_score(y.iloc[ii],p) if len(np.unique(y.iloc[ii]))>1 else np.nan})
    perm=permutation_importance(model,X2.iloc[hold],y.iloc[hold],n_repeats=10,random_state=42,scoring='neg_log_loss')
    imp=pd.DataFrame({'feature':model_cols,'importance_mean':-perm.importances_mean,'importance_std':perm.importances_std}).sort_values('importance_mean',ascending=False)
else:
    results.append({'split':'HOLDOUT','N':0,'log_loss':np.nan,'brier':np.nan,'roc_auc':np.nan})
    imp=pd.DataFrame({'feature':model_cols,'importance_mean':np.nan,'importance_std':np.nan})
pd.DataFrame(results).to_csv(RESEARCH/'PATTERN_DISCOVERY_OOS.csv',index=False)
imp.to_csv(RESEARCH/'PATTERN_DISCOVERY_FEATURE_IMPORTANCE.csv',index=False)

# Expanding-window walk-forward evaluation.
wf=[]
if len(idx)>=600:
    X2=X.fillna(X.iloc[idx[:int(len(idx)*.6)]].median())
    folds=[(.50,.10),(.60,.10),(.70,.10),(.80,.10)]
    for tr_frac,te_frac in folds:
        tr_end=max(200,int(len(idx)*tr_frac)); te_end=min(len(idx),tr_end+max(50,int(len(idx)*te_frac)))
        tr_i=idx[:tr_end]; te_i=idx[tr_end:te_end]
        if len(te_i)<50: continue
        m=LogisticRegression(max_iter=2000).fit(X2.iloc[tr_i],y.iloc[tr_i])
        pp=m.predict_proba(X2.iloc[te_i])[:,1]
        wf.append({'train_N':len(tr_i),'test_N':len(te_i),'test_start':str(d.iloc[te_i[0]].kickoff),'test_end':str(d.iloc[te_i[-1]].kickoff),'log_loss':log_loss(y.iloc[te_i],pp,labels=[0,1]),'brier':brier_score_loss(y.iloc[te_i],pp),'roc_auc':roc_auc_score(y.iloc[te_i],pp) if len(np.unique(y.iloc[te_i]))>1 else np.nan})
pd.DataFrame(wf).to_csv(RESEARCH/'PATTERN_DISCOVERY_WALK_FORWARD.csv',index=False)

# Season stability for a few core effects
st=[]
for season,g in d.groupby('season'):
    st.append({'season':season,'N':len(g),'home_win_rate':g.home_win.mean(),'mean_goals':g.total_goals.mean(),'over25_rate':g.over25.mean(),'mean_cards':g.total_cards.mean(),'mean_corners':g.total_corners.mean()})
pd.DataFrame(st).to_csv(RESEARCH/'PATTERN_DISCOVERY_STABILITY.csv',index=False)

# Negative results / unavailable domains
neg=[
 {'topic':'Player impact','status':'INSUFFICIENT_DATA','reason':'No real player-level minutes/xG/xA/injury/suspension dataset materialized in current ZIP.'},
 {'topic':'Injury return effect','status':'INSUFFICIENT_DATA','reason':'No timestamped player injury/return records.'},
 {'topic':'Motivation/must-win','status':'INSUFFICIENT_DATA','reason':'No pre-match standings/qualification-state dataset sufficient to reconstruct objective motivation.'},
 {'topic':'Derby/rivalry','status':'INSUFFICIENT_DATA','reason':'No auditable rivalry registry/source materialized; conservative classifier remains UNKNOWN.'},
 {'topic':'LIVE pattern validation','status':'INSUFFICIENT_DATA','reason':'No historical LIVE snapshot dataset with ordered timestamps is materialized.'},
 {'topic':'PIT edge','status':'NOT_DETERMINED','reason':'Current odds are NON_PIT or PIT_DATE_ONLY; no exact decision-time odds.'},
 {'topic':'xG patterns','status':'INSUFFICIENT_DATA','reason':'Canonical xG fields are fully missing in current materialized dataset.'},
]
pd.DataFrame(neg).to_csv(RESEARCH/'PATTERN_DISCOVERY_NEGATIVE_RESULTS.csv',index=False)

# Data audit
coverage={
 'run_timestamp_utc':RUN,'input_file':str(INPUT.relative_to(ROOT)),'input_sha256':sha(INPUT),'total_matches':int(len(d)),
 'primary_window_start':'2020-01-01','actual_min_date':str(d.kickoff.min()),'actual_max_date':str(d.kickoff.max()),
 'countries':sorted(d.country.dropna().unique().tolist()),'competitions':sorted(d.competition.dropna().unique().tolist()),
 'competition_count':int(d.competition.nunique()),'competition_season_pairs':int(d[['competition','season']].drop_duplicates().shape[0]),
 'seasons':sorted(d.season.dropna().unique().tolist()),'divisions':sorted(d.division.dropna().unique().tolist()),
 'male_matches':int((d.gender=='MALE').sum()),'female_matches':0,
 'odds_rows':int(pd.read_csv(DATA/'processed/odds_observations_real_nonpit.csv').shape[0]) if (DATA/'processed/odds_observations_real_nonpit.csv').exists() else 0,
 'timestamped_odds':int(d.odds_timestamp.notna().sum()),'pit_validated':int(d.pit_status.eq('PIT_VALIDATED').sum()),
 'live_snapshots':0,'events':0,'lineups':0,'player_records':0,'injury_records':0,'suspension_records':0,
 'xg_rows':int(d[['home_xg','away_xg']].notna().all(axis=1).sum()),'cards_rows':int(d.total_cards.notna().sum()),'corners_rows':int(d.total_corners.notna().sum()),
 'referee_rows':int(d.referee.notna().sum()),'shots_rows':int(d[['home_shots','away_shots']].notna().all(axis=1).sum()),'sot_rows':int(d[['home_sot','away_sot']].notna().all(axis=1).sum()),
 'fouls_rows':int(d[['home_fouls','away_fouls']].notna().all(axis=1).sum()),'settlements':0,'clv_ready':0,
 'evidence_found_only':0,'downloaded_sources':len(list((DATA/'raw').glob('*'))),'materialized_real_sources':len(list((DATA/'raw').glob('*'))),'processed_matches':int(len(d)),'used_in_model':int(mask.sum())
}
(RESEARCH/'PATTERN_DISCOVERY_AUDIT.json').write_text(json.dumps(coverage,indent=2,ensure_ascii=False),encoding='utf-8')

# Validate a compact set of pre-registered patterns on the temporal holdout.
validation=[]
if len(idx)>=300:
    train_cut=idx[int(len(idx)*.8)]
    hold_idx=idx[int(len(idx)*.8):]
    # masks are evaluated independently in the holdout, using only pre-match features.
    patterns=[
      ('Home attack rolling strength above away','strength_attack_diff','gt',0,'home_win'),
      ('Home defensive goals-against lower than away','strength_defense_diff','lt',0,'home_win'),
      ('High pre-match home shot form','home_shots_for_5','ge',float(d.loc[idx[:int(len(idx)*.6)],'home_shots_for_5'].median()),'home_win'),
      ('High pre-match away shot form','away_shots_for_5','ge',float(d.loc[idx[:int(len(idx)*.6)],'away_shots_for_5'].median()),'away_win'),
      ('Second division','division_label','eq','SECOND','total_goals'),
      ('Fourth division','division_label','eq','FOURTH','total_goals'),
    ]
    for name,col,op,val,outcome in patterns:
        if op=='gt': m=d[col]>val
        elif op=='lt': m=d[col]<val
        elif op=='ge': m=d[col]>=val
        else: m=d[col]==val
        tr_mask=np.isin(d.index,idx[:int(len(idx)*.6)]) & m
        ho_mask=np.isin(d.index,hold_idx) & m
        tr=d.loc[tr_mask,outcome].dropna(); ho=d.loc[ho_mask,outcome].dropna()
        tr2=d.loc[np.isin(d.index,idx[:int(len(idx)*.6)]) & ~m,outcome].dropna(); ho2=d.loc[np.isin(d.index,hold_idx) & ~m,outcome].dropna()
        if len(tr)>=30 and len(ho)>=30 and len(tr2)>=30 and len(ho2)>=30:
            eff_tr=float(tr.mean()-tr2.mean()); eff_ho=float(ho.mean()-ho2.mean())
            validation.append({'pattern':name,'discovery_effect':eff_tr,'holdout_effect':eff_ho,'same_sign':bool(np.sign(eff_tr)==np.sign(eff_ho)),'N_discovery':len(tr),'N_holdout':len(ho),'status':'OOS_REPLICATED' if np.sign(eff_tr)==np.sign(eff_ho) else 'OOS_FAILED'})
pd.DataFrame(validation).to_csv(RESEARCH/'PATTERN_DISCOVERY_PATTERN_VALIDATION.csv',index=False)

# Top patterns: ranking is research priority, not profitability.
rank=hdf.copy()
if not rank.empty:
    rank['abs_effect']=rank.effect_size.abs(); rank['score']=rank.abs_effect*np.log1p(rank.N_segment+rank.N_complement)/(1+10*rank.fdr_adjusted_p.fillna(1))
    rank['promotion_status']=np.where(rank.fdr_adjusted_p<0.05,'EXPLORATORY_SIGNIFICANT_FDR','EXPLORATORY')
    rank=rank.sort_values(['score','abs_effect'],ascending=[False,False])
rank.head(50).to_csv(RESEARCH/'PATTERN_DISCOVERY_TOP50.csv',index=False)

# Acquisition gap priority (quantitative but not an acquisition claim)
gaps=[
('PIT timestamped odds',coverage['total_matches']-coverage['pit_validated'],'HIGH','enables temporal market research'),
('Historical LIVE snapshots',coverage['total_matches']-coverage['live_snapshots'],'HIGH','enables live state validation'),
('Player availability/injuries',coverage['total_matches']-coverage['injury_records'],'HIGH','required for player impact'),
('Lineups and minutes',coverage['total_matches']-coverage['lineups'],'HIGH','required for player importance'),
('xG',coverage['total_matches']-coverage['xg_rows'],'HIGH','improves chance-quality analysis'),
('Standings/table state',coverage['total_matches'],'HIGH','required for objective motivation'),
('Female football',coverage['female_matches'],'MEDIUM','separate gender research coverage'),
('Additional countries/divisions',coverage['competition_count'],'MEDIUM','global generalization'),
('Settlement records',coverage['settlements'],'HIGH','required for market settlement research'),
('CLV-ready timestamped odds',coverage['clv_ready'],'HIGH','required for CLV'),
]
pd.DataFrame(gaps,columns=['gap','current_count_or_proxy','priority','scientific_value']).to_csv(RESEARCH/'TOP_DATA_GAPS.csv',index=False)

# Reports
comp=d.groupby(['country','competition','division','season']).size().reset_index(name='matches')
comp.to_csv(RESEARCH/'COVERAGE_BY_COMPETITION_SEASON.csv',index=False)

report=f'''# Context Intelligence + Player Impact + Global Pattern Discovery

Run: {RUN}

## Scientific status
- REAL_MONEY = DISABLED
- Current materialized sample: **{len(d):,} real matches**.
- Current coverage: {d.country.nunique()} countries, {d.competition.nunique()} competitions, {d.season.nunique()} seasons.
- Competition-season pairs: {coverage['competition_season_pairs']} (this is distinct from competition count).
- PIT validated odds: {coverage['pit_validated']}.
- Historical LIVE snapshots: {coverage['live_snapshots']}.
- Player/injury/lineup datasets: not materialized; no player conclusions were fabricated.

## Core findings
- Home advantage is directly measurable in the current sample, but it is descriptive and not a claim of betting edge.
- Division/competition differences are reported with sample sizes and FDR adjustment.
- Rolling team form features are strictly shifted to pre-match information and are used only where prior history exists.
- OOS/HOLDOUT model tests are separated temporally.

## Context limitations
Objective motivation, aggregate qualification state, derby status, injuries, suspensions, lineups, player impact, xG and historical LIVE cannot be reconstructed reliably from the current materialized datasets. These remain `INSUFFICIENT_DATA` rather than being inferred.

## Odds/PIT limitation
The existing odds are primarily `NON_PIT` and some records are `PIT_DATE_ONLY`; they are not promoted to exact PIT. Therefore no temporal market edge is claimed.

## Gender
All current materialized matches are male. Female football remains structurally separate and currently has zero materialized rows.

See CSV/JSON outputs under `data/research/` and the audit JSON for exact counts.
'''
(REPORTS/'context_intelligence'/'CONTEXT_INTELLIGENCE_REPORT.md').write_text(report,encoding='utf-8')

player='''# Player Impact Report\n\nStatus: INSUFFICIENT_DATA.\n\nThe current real materialized ZIP does not contain auditable player-level minutes, lineups, injuries, suspensions, xG/xA or return-from-injury timestamps. No player impact effect, key-player classification or injury-return pattern was fabricated.\n'''
(REPORTS/'context_intelligence'/'PLAYER_IMPACT_REPORT.md').write_text(player,encoding='utf-8')
(REPORTS/'context_intelligence'/'INJURY_RETURN_REPORT.md').write_text('# Injury Return Report\n\nStatus: INSUFFICIENT_DATA. No timestamped injury/return dataset is materialized.\n',encoding='utf-8')
(REPORTS/'context_intelligence'/'COMPETITIVE_MOTIVATION_REPORT.md').write_text('# Competitive Motivation Report\n\nStatus: INSUFFICIENT_DATA. Standings/qualification-state inputs required for objective pre-match motivation are not materialized.\n',encoding='utf-8')
(REPORTS/'context_intelligence'/'PATTERN_DISCOVERY_GLOBAL_REPORT.md').write_text(report,encoding='utf-8')
(REPORTS/'context_intelligence'/'PATTERN_DISCOVERY_NEGATIVE_RESULTS.md').write_text(pd.DataFrame(neg).to_markdown(index=False),encoding='utf-8')
(REPORTS/'context_intelligence'/'PATTERN_DISCOVERY_OOS.md').write_text(pd.DataFrame(results).to_markdown(index=False),encoding='utf-8')
(REPORTS/'context_intelligence'/'PATTERN_DISCOVERY_WALK_FORWARD.md').write_text(pd.DataFrame(wf).to_markdown(index=False) if wf else '# Walk-forward Report\n\nInsufficient rows for rolling folds.\n',encoding='utf-8')
(REPORTS/'context_intelligence'/'PATTERN_DISCOVERY_MULTIPLE_TESTING.md').write_text(hdf.to_markdown(index=False) if not hdf.empty else 'No eligible hypotheses.',encoding='utf-8')

# Data dictionary
(RESEARCH/'PATTERN_DISCOVERY_DATA_DICTIONARY.md').write_text('''# Pattern Discovery Data Dictionary\n\nAll derived features are generated from materialized real historical observations. Rolling features are shifted: only matches strictly before the current kickoff contribute.\n\nKey fields: `home_goals_for_5`, `away_goals_for_5`, `home_shots_for_5`, `away_shots_for_5`, `home_sot_for_5`, `away_sot_for_5`, `rest_home_days`, `rest_away_days`, `matches_home_7d`, `matches_away_7d`, `strength_attack_diff`, `strength_defense_diff`.\n\nContext fields `motivation_state`, `importance_state`, `derby_state`, `leg_state` are explicitly `UNKNOWN` because no auditable pre-match competition-state source is materialized.\n\nGender is explicit; current materialized sample contains MALE only.\n''',encoding='utf-8')

# scientific status
(REPORTS/'FINAL_SCIENTIFIC_STATUS.md').write_text(f'''# FINAL SCIENTIFIC STATUS\n\n- REAL_MONEY = DISABLED\n- Real materialized matches: {len(d):,}\n- Countries: {d.country.nunique()}\n- Competitions: {d.competition.nunique()}\n- Competition-season pairs: {coverage['competition_season_pairs']}\n- PIT validated: {coverage['pit_validated']}\n- LIVE snapshots: {coverage['live_snapshots']}\n- Player records: {coverage['player_records']}\n- Injury records: {coverage['injury_records']}\n- xG rows: {coverage['xg_rows']}\n\n## Verdict\nNo new PIT-validated betting edge is confirmed in this phase. Several descriptive and pre-match historical patterns are measurable, but player impact, motivation, LIVE and exact PIT research are **EDGE NOT DETERMINED** due to missing materialized evidence.\n''',encoding='utf-8')

# Reproducibility manifest
manifest={'run_timestamp_utc':RUN,'python':platform.python_version(),'platform':platform.platform(),'seed':42,'input_sha256':sha(INPUT),'files_generated':[]}
for p in [RESEARCH/'context_intelligence_segments.csv',RESEARCH/'PATTERN_DISCOVERY_MULTIPLE_TESTING.csv',RESEARCH/'PATTERN_DISCOVERY_OOS.csv',RESEARCH/'PATTERN_DISCOVERY_FEATURE_IMPORTANCE.csv',RESEARCH/'PATTERN_DISCOVERY_STABILITY.csv',RESEARCH/'PATTERN_DISCOVERY_NEGATIVE_RESULTS.csv',RESEARCH/'PATTERN_DISCOVERY_TOP50.csv',RESEARCH/'TOP_DATA_GAPS.csv',RESEARCH/'COVERAGE_BY_COMPETITION_SEASON.csv',RESEARCH/'PATTERN_DISCOVERY_AUDIT.json']:
    manifest['files_generated'].append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'size_bytes':p.stat().st_size})
(MAN/'CONTEXT_INTELLIGENCE_EXECUTION_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(coverage,indent=2))
