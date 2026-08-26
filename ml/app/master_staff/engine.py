from __future__ import annotations
import hashlib, json, math
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, chi2_contingency
from statsmodels.stats.multitest import multipletests
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, brier_score_loss, roc_auc_score

MAIN_TARGETS = [
('England','Premier League','1'),('England','Championship','2'),('Germany','Bundesliga','1'),('Germany','2. Bundesliga','2'),
('Italy','Serie A','1'),('Italy','Serie B','2'),('Spain','La Liga','1'),('Spain','Segunda Division','2'),
('France','Ligue 1','1'),('France','Ligue 2','2'),('Netherlands','Eredivisie','1'),('Portugal','Primeira Liga','1'),
('Belgium','Belgian Pro League','1'),('Scotland','Scottish Premiership','1'),('Turkey','Super Lig','1'),
('Austria','Austrian Bundesliga','1'),('Switzerland','Swiss Super League','1'),('Brazil','Brasileirao Serie A','1'),
('Argentina','Liga Profesional Argentina','1'),('USA','MLS','1'),('Japan','J1 League','1'),('South Korea','K League 1','1'),('Mexico','Liga MX','1')]


def load_canonical(root: Path) -> pd.DataFrame:
    p=root/'data/canonical/football_historical_real_canonical.csv'
    d=pd.read_csv(p)
    d['kickoff_timestamp']=pd.to_datetime(d['kickoff_timestamp'], errors='coerce')
    d['home_goals']=pd.to_numeric(d['home_goals'], errors='coerce')
    d['away_goals']=pd.to_numeric(d['away_goals'], errors='coerce')
    if 'gender' not in d.columns:
        d['gender']='MEN'
    else:
        d['gender']=d['gender'].fillna('MEN').astype(str).str.upper()
    d['canonical_match_id']=d['match_id'].astype(str)
    return d.sort_values(['kickoff_timestamp','canonical_match_id']).reset_index(drop=True)


def h2h_features(d: pd.DataFrame) -> pd.DataFrame:
    pair_hist=defaultdict(list); rows=[]
    for r in d.sort_values(['kickoff_timestamp','canonical_match_id']).itertuples(index=False):
        key=tuple(sorted((str(r.home_team),str(r.away_team))))
        hist=pair_hist[key]
        recent=hist[-10:]
        def calc(n):
            h=hist[-n:]
            if not h:return (0,0,0,np.nan,np.nan)
            hw=sum(x['winner']==r.home_team for x in h); dr=sum(x['winner']=='DRAW' for x in h)
            goals=np.mean([x['hg']+x['ag'] for x in h]); btts=np.mean([x['hg']>0 and x['ag']>0 for x in h])
            return len(h),hw,dr,float(goals),float(btts)
        f3=calc(3); f5=calc(5); f10=calc(10)
        rows.append((f3,f5,f10))
        if pd.notna(r.home_goals) and pd.notna(r.away_goals):
            winner=r.home_team if r.home_goals>r.away_goals else r.away_team if r.away_goals>r.home_goals else 'DRAW'
            hist.append({'date':r.kickoff_timestamp,'home':r.home_team,'away':r.away_team,'hg':r.home_goals,'ag':r.away_goals,'winner':winner})
    out=pd.DataFrame({
      'h2h_n3':[x[0][0] for x in rows],'h2h_home_win_rate3':[x[0][1]/x[0][0] if x[0][0] else np.nan for x in rows],
      'h2h_draw_rate3':[x[0][2]/x[0][0] if x[0][0] else np.nan for x in rows],'h2h_goals3':[x[0][3] for x in rows],'h2h_btts3':[x[0][4] for x in rows],
      'h2h_n5':[x[1][0] for x in rows],'h2h_home_win_rate5':[x[1][1]/x[1][0] if x[1][0] else np.nan for x in rows],
      'h2h_draw_rate5':[x[1][2]/x[1][0] if x[1][0] else np.nan for x in rows],'h2h_goals5':[x[1][3] for x in rows],'h2h_btts5':[x[1][4] for x in rows],
      'h2h_n10':[x[2][0] for x in rows],'h2h_home_win_rate10':[x[2][1]/x[2][0] if x[2][0] else np.nan for x in rows],
      'h2h_draw_rate10':[x[2][2]/x[2][0] if x[2][0] else np.nan for x in rows],'h2h_goals10':[x[2][3] for x in rows],'h2h_btts10':[x[2][4] for x in rows],
    })
    return out


def form_features(d: pd.DataFrame) -> pd.DataFrame:
    state=defaultdict(list); last={}; rows=[]
    for r in d.itertuples(index=False):
        vals={}
        for side,team in [('home',r.home_team),('away',r.away_team)]:
            hist=state[team]
            for n in (3,5,10): vals[f'{side}_form{n}']=np.mean(hist[-n:]) if hist else np.nan
            vals[f'{side}_rest_days']=(r.kickoff_timestamp-last[team]).total_seconds()/86400 if team in last and pd.notna(r.kickoff_timestamp) else np.nan
        vals['rest_advantage']=vals['home_rest_days']-vals['away_rest_days'] if pd.notna(vals['home_rest_days']) and pd.notna(vals['away_rest_days']) else np.nan
        rows.append(vals)
        if pd.notna(r.home_goals) and pd.notna(r.away_goals):
            state[r.home_team].append(3 if r.home_goals>r.away_goals else 1 if r.home_goals==r.away_goals else 0)
            state[r.away_team].append(3 if r.away_goals>r.home_goals else 1 if r.home_goals==r.away_goals else 0)
            last[r.home_team]=last[r.away_team]=r.kickoff_timestamp
    return pd.DataFrame(rows)


def stage_importance(d: pd.DataFrame) -> pd.DataFrame:
    s=d['round'].fillna('').astype(str).str.lower()
    out=pd.DataFrame(index=d.index)
    out['importance_state']=np.select([
      s.str.contains('final',na=False),s.str.contains('semi',na=False),s.str.contains('quarter',na=False),s.str.contains('round of 16|playoff|knockout',regex=True,na=False),s.str.contains('group',na=False)
    ],['FINAL','VERY_HIGH','VERY_HIGH','HIGH','NORMAL'],default='UNKNOWN')
    out['importance_score']=out.importance_state.map({'FINAL':1.0,'VERY_HIGH':0.9,'HIGH':0.75,'NORMAL':0.5}).fillna(np.nan)
    out['importance_evidence']='stage_only; mathematical_table_state_not_available'
    out['motivation_state']='UNKNOWN'
    out['must_win']='UNKNOWN'; out['already_qualified']='UNKNOWN'; out['already_eliminated']='UNKNOWN'
    return out


def build_features(d: pd.DataFrame) -> pd.DataFrame:
    f=pd.concat([form_features(d),h2h_features(d),stage_importance(d)],axis=1)
    out=pd.concat([d.reset_index(drop=True),f.reset_index(drop=True)],axis=1)
    out['home_win']=np.where(out.home_goals.notna() & out.away_goals.notna(),(out.home_goals>out.away_goals).astype(int),np.nan)
    out['total_goals']=out.home_goals+out.away_goals
    out['btts']=np.where(out.total_goals.notna(),((out.home_goals>0)&(out.away_goals>0)).astype(int),np.nan)
    out['derby_status']='UNKNOWN'
    out['rivalry_status']='UNKNOWN'
    out['travel_status']='NOT_AVAILABLE'
    out['player_data_status']='NOT_AVAILABLE'
    out['injury_data_status']='NOT_AVAILABLE'
    out['lineup_status']='NOT_AVAILABLE'
    out['live_status']='NOT_AVAILABLE'
    out['market_pit_status']=np.where(out['pit_status'].astype(str).eq('PIT_VALIDATED'),'PIT_VALIDATED','NON_PIT')
    return out


def h2h_records(features):
    cols=['canonical_match_id','kickoff_timestamp','home_team','away_team','h2h_n3','h2h_n5','h2h_n10']
    return features[cols].copy()


def hypothesis_tests(d):
    rows=[]; x=d.dropna(subset=['home_win'])
    for name,mask in [('FINAL_STAGE',d.importance_state.eq('FINAL')),('HIGH_STAGE',d.importance_state.isin(['VERY_HIGH','HIGH'])),('H2H_AVAILABLE',d.h2h_n5.gt(0))]:
        a=x.loc[mask.loc[x.index],'home_win']; b=x.loc[~mask.loc[x.index],'home_win']
        if len(a)>=10 and len(b)>=30:
            tab=pd.crosstab(mask.loc[x.index],x.home_win)
            try:p=chi2_contingency(tab,correction=True)[1]
            except Exception:p=1.0
            rows.append({'hypothesis':name,'n_segment':len(a),'n_control':len(b),'effect_size':float(a.mean()-b.mean()),'p_value':float(p),'status':'EXPLORATORY'})
    for feat in ['home_form5','away_form5','rest_advantage']:
        z=d[[feat,'home_win']].dropna()
        if len(z)>=60:
            a=z.loc[z.home_win.eq(1),feat]; b=z.loc[z.home_win.eq(0),feat]
            if len(a)>=20 and len(b)>=20:
                p=mannwhitneyu(a,b,alternative='two-sided').pvalue
                rows.append({'hypothesis':feat+' -> HOME_WIN','n_segment':len(a),'n_control':len(b),'effect_size':float(a.median()-b.median()),'p_value':float(p),'status':'EXPLORATORY'})
    if rows:
        q=multipletests([r['p_value'] for r in rows],method='fdr_bh')[1]
        for r,qq in zip(rows,q):r['q_value']=float(qq);r['promotion_status']='PROMISING' if qq<0.05 else 'INCONCLUSIVE'
    return pd.DataFrame(rows)


def oos_walk_forward(d):
    z=d.dropna(subset=['home_form5','away_form5','rest_advantage','home_win']).sort_values('kickoff_timestamp').copy()
    if len(z)<200:return {'status':'INSUFFICIENT_DATA','n':len(z)}
    X=z[['home_form5','away_form5','rest_advantage']].fillna(0); y=z.home_win.astype(int)
    cut=int(len(z)*.7); hold=int(len(z)*.85)
    m=LogisticRegression(max_iter=1000).fit(X.iloc[:cut],y.iloc[:cut])
    pv=m.predict_proba(X.iloc[cut:hold])[:,1]; ph=m.predict_proba(X.iloc[hold:])[:,1]
    def met(yy,p):return {'log_loss':float(log_loss(yy,p,labels=[0,1])),'brier':float(brier_score_loss(yy,p)),'roc_auc':float(roc_auc_score(yy,p)) if len(np.unique(yy))>1 else None}
    folds=[]
    step=max(50,(len(z)-200)//4)
    for end in range(200,len(z),step):
        te=min(end+step,len(z));
        if te<=end:break
        mm=LogisticRegression(max_iter=1000).fit(X.iloc[:end],y.iloc[:end]); pp=mm.predict_proba(X.iloc[end:te])[:,1]
        folds.append({'train_n':end,'test_n':te-end,**met(y.iloc[end:te],pp)})
    return {'status':'CALCULATED','n':len(z),'train_n':cut,'validation_n':hold-cut,'holdout_n':len(z)-hold,'validation':met(y.iloc[cut:hold],pv),'holdout':met(y.iloc[hold:],ph),'walk_forward':folds}


def coverage(d):
    rows=[]
    for (c,s,g),x in d.groupby(['competition','season','gender'],dropna=False):
        rows.append({'competition':c,'season':s,'gender':g,'matches':len(x),'events':0,'shots':0,'SOT':0,'xG':int(x[['home_xg','away_xg']].notna().all(axis=1).sum()),'corners':int(x[['home_corners','away_corners']].notna().all(axis=1).sum()),'cards':int(x[['home_cards','away_cards']].notna().all(axis=1).sum()),'lineups':0,'players':0,'injuries':0,'suspensions':0,'referees':int(x.referee.notna().sum()),'odds':int(x[['odds_1','odds_x','odds_2']].notna().all(axis=1).sum()),'timestamped_odds':int(x.odds_timestamp.notna().sum()),'PIT_validated':int(x.pit_status.eq('PIT_VALIDATED').sum()),'LIVE':0,'settlements':0})
    return pd.DataFrame(rows)


def target_registry(d):
    have=set((str(a),str(b)) for a,b,_ in d[['country','competition','division']].drop_duplicates().itertuples(index=False))
    rows=[]
    for c,comp,tier in MAIN_TARGETS:
        status='MATERIALIZED' if (c,comp,tier) in have else 'NOT_MATERIALIZED'
        rows.append({'country':c,'competition':comp,'tier':tier,'status':status,'seasons_available':','.join(sorted(map(str,d.loc[(d.country==c)&(d.competition==comp),'season'].dropna().unique()))) if status=='MATERIALIZED' else '','matches_materialized':int(((d.country==c)&(d.competition==comp)).sum()),'data_quality':'REAL_CANONICAL' if status=='MATERIALIZED' else 'NOT_AVAILABLE'})
    return pd.DataFrame(rows)


def operational_manifest(root,d):
    files={
      'live_engine': bool((root/'ml/app/v20/live_engine.py').exists()), 'odds_engine': bool((root/'ml/app/v19/market_intelligence.py').exists()),
      'settlement_engine': bool((root/'ml/app/v19/settlement.py').exists()), 'paper_trading': bool((root/'ml/app/v19/paper.py').exists()),
      'risk_engine': bool((root/'ml/app/v20/risk.py').exists()), 'kill_switch': bool((root/'ml/app/v21/controls.py').exists()),
      'watchdog': bool((root/'ml/app/v21/live_monitor.py').exists()), 'champion_challenger': bool((root/'ml/app/mlops/champion_challenger.py').exists()),
      'drift_detection': bool((root/'ml/app/mlops/drift.py').exists()), 'feature_store': bool((root/'ml/app/features.py').exists()),
      'explainability': bool((root/'ml/app/v21/decision_trace.py').exists()), 'quality_gate': bool((root/'ml/app/selection.py').exists()),
      'no_bet_intelligence': bool((root/'ml/app/v25/policy.py').exists()),
    }
    return files
