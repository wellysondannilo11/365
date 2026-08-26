from __future__ import annotations
import hashlib, json, re
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, mannwhitneyu
from statsmodels.stats.multitest import multipletests
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, brier_score_loss, roc_auc_score

STAGES = {
    'preliminary round':'PRELIMINARY','round 1':'ROUND_1','round 2':'ROUND_2','round 3':'ROUND_3',
    'group stage':'GROUP_STAGE','group':'GROUP_STAGE','playoffs':'PLAYOFF','round of 16':'ROUND_OF_16',
    'quarterfinals':'QUARTERFINAL','semifinals':'SEMIFINAL','final':'FINAL'
}

def canonical_id(competition, season, date, home, away):
    s='|'.join([str(competition),str(season),str(date)[:10],str(home).strip().lower(),str(away).strip().lower()])
    return hashlib.sha256(s.encode()).hexdigest()[:24]

def parse_score(s):
    if not s: return (np.nan,np.nan,np.nan,np.nan)
    s=s.strip()
    # Remove penalty annotation; preserve 90-minute score as first score in parentheses when available.
    m=re.search(r'(?P<a>\d+)\s*-\s*(?P<b>\d+)\s*pen\.\s*(?P<ha>\d+)\s*-\s*(?P<hb>\d+)\s*a\.e\.t\.',s)
    if m:
        return int(m.group('ha')),int(m.group('hb')),int(m.group('a')),int(m.group('b'))
    m=re.search(r'(?P<a>\d+)\s*-\s*(?P<b>\d+)\s*pen\.\s*\((?P<ha>\d+)\s*-\s*(?P<hb>\d+)\)',s)
    if m:
        return int(m.group('ha')),int(m.group('hb')),int(m.group('a')),int(m.group('b'))
    m=re.search(r'(\d+)\s*-\s*(\d+)',s)
    if m: return int(m.group(1)),int(m.group(2)),np.nan,np.nan
    return np.nan,np.nan,np.nan,np.nan

def parse_sudamericana_txt(path, season):
    rows=[]; stage='UNKNOWN'; group=None; cur_date=None
    date_re=re.compile(r'^\s*(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+([A-Z][a-z]{2})\s+(\d{1,2})(?:\s+(\d{4}))?')
    match_re=re.compile(r'^\s*(?:\d{1,2}:\d{2}\s+)?(.+?)\s+v\s+(.+?)\s+(\d+\s*-\s*\d+(?:\s+pen\.\s+\d+\s*-\s*\d+\s+a\.e\.t\.)?(?:\s+pen\.)?(?:\s*\(.*?\))?)\s*$')
    for raw in Path(path).read_text(encoding='utf-8').splitlines():
        line=raw.rstrip()
        if line.startswith('▪ '):
            label=line[2:].strip()
            stage=STAGES.get(label.lower(), label.upper().replace(' ','_'))
            group=label if label.lower().startswith('group ') else None
            continue
        dm=date_re.match(line)
        if dm:
            yr=int(dm.group(3)) if dm.group(3) else int(season)
            cur_date=f"{yr}-{pd.to_datetime(dm.group(1),format='%b').month:02d}-{int(dm.group(2)):02d}"
            continue
        m=match_re.match(line)
        if not m or cur_date is None or 'N.N.' in m.group(0): continue
        home=m.group(1).strip(); away=m.group(2).strip(); hs,as_,ps,pa=parse_score(m.group(3))
        rows.append(dict(competition='Copa Sudamericana',season=int(season),gender='MEN',country='South America',stage=stage,group=group,match_date=cur_date,home_team=home,away_team=away,home_goals=hs,away_goals=as_,penalty_home=ps,penalty_away=pa,source='openfootball/south-america',source_url=f'https://raw.githubusercontent.com/openfootball/south-america/master/copa-libertadores/{season}_copas.txt',pit_status='UNKNOWN',data_type='HISTORICAL_REAL'))
    return pd.DataFrame(rows)

def parse_libertadores_csv(path):
    df=pd.read_csv(path)
    df=df[df['season'].between(2020,2022)].copy()
    out=pd.DataFrame({
        'competition':'Copa Libertadores','season':df['season'].astype(int),'gender':'MEN','country':'South America',
        'stage':df['stage'].astype(str).str.lower().map(lambda x: STAGES.get(x,x.upper().replace(' ','_'))),'group':np.nan,
        'match_date':pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%d'),'home_team':df['home_team'],'away_team':df['away_team'],
        'home_goals':pd.to_numeric(df['home_goal'],errors='coerce'),'away_goals':pd.to_numeric(df['away_goal'],errors='coerce'),
        'penalty_home':np.nan,'penalty_away':np.nan,'source':'ricardo-mattoss/Brazilian-Soccer-Data',
        'source_url':'https://github.com/ricardo-mattoss/Brazilian-Soccer-Data/blob/master/Data/Libertadores_Matches.csv',
        'pit_status':'UNKNOWN','data_type':'HISTORICAL_REAL'})
    return out

def enrich(df):
    df=df.copy(); df['match_date']=pd.to_datetime(df['match_date']); df=df.sort_values(['match_date','home_team','away_team']).reset_index(drop=True)
    df['canonical_match_id']=[canonical_id(r.competition,r.season,r.match_date,r.home_team,r.away_team) for r in df.itertuples()]
    df['home_result']=np.where(df.home_goals>df.away_goals,'H',np.where(df.home_goals<df.away_goals,'A','D'))
    df['total_goals']=df.home_goals+df.away_goals; df['btts']=(df.home_goals>0)&(df.away_goals>0)
    df['home_win']=df.home_result.eq('H'); df['away_win']=df.home_result.eq('A'); df['draw']=df.home_result.eq('D')
    df['two_leg_candidate']=df.stage.isin(['ROUND_OF_16','QUARTERFINAL','SEMIFINAL'])
    df['final_flag']=df.stage.eq('FINAL')
    df['importance_score']=df.stage.map({'FINAL':1.0,'SEMIFINAL':.9,'QUARTERFINAL':.8,'ROUND_OF_16':.7,'PLAYOFF':.65,'GROUP_STAGE':.5}).fillna(.3)
    # Pre-match rolling team form; strictly prior observations only.
    teams=sorted(set(df.home_team.dropna())|set(df.away_team.dropna()))
    state={t:[] for t in teams}; last={t:None for t in teams}
    vals=[]
    for r in df.itertuples():
        h,a=r.home_team,r.away_team
        def feats(t):
            hist=state[t][-10:]
            return (np.mean(hist[-3:]) if len(hist)>=1 else np.nan,
                    np.mean(hist[-5:]) if len(hist)>=1 else np.nan,
                    np.mean(hist[-10:]) if len(hist)>=1 else np.nan,
                    (r.match_date-last[t]).days if last[t] is not None else np.nan)
        hf=feats(h); af=feats(a); vals.append(hf+af)
        state[h].append(3 if r.home_goals>r.away_goals else 1 if r.home_goals==r.away_goals else 0)
        state[a].append(3 if r.away_goals>r.home_goals else 1 if r.home_goals==r.away_goals else 0)
        last[h]=last[a]=r.match_date
    arr=np.array(vals,dtype=float)
    for i,n in enumerate(['home_form3','home_form5','home_form10','home_rest_days','away_form3','away_form5','away_form10','away_rest_days']): df[n]=arr[:,i]
    df['rest_advantage']=df.home_rest_days-df.away_rest_days
    return df

def bh(rows):
    if not rows: return pd.DataFrame(columns=['p_value','fdr_adjusted_p'])
    p=np.array([x['p_value'] for x in rows],dtype=float); q=multipletests(p,method='fdr_bh')[1]
    out=[]
    for x,qq in zip(rows,q): y=x.copy(); y['fdr_adjusted_p']=float(qq); out.append(y)
    return pd.DataFrame(out)

def pattern_tests(df):
    rows=[]; d=df.copy(); d['over25']=d.total_goals>2.5
    # Valid comparisons only; never test a variable against itself.
    tests=[
        ('KNOCKOUT_HOME_WIN','two_leg_candidate','home_win'),
        ('FINAL_HOME_WIN','final_flag','home_win'),
        ('FINAL_BTTS','final_flag','btts'),
        ('FINAL_OVER25','final_flag','over25'),
    ]
    for pid,seg,outcome in tests:
        a=d[d[seg]==True][outcome].astype(float); b=d[d[seg]==False][outcome].astype(float)
        if len(a)<10 or len(b)<10: continue
        tab=pd.crosstab(d[seg],d[outcome])
        try: p=chi2_contingency(tab,correction=True)[1]
        except Exception: p=1.0
        rows.append({'pattern_id':pid,'description':f'{seg} vs {outcome}','sample_size_segment':len(a),'sample_size_control':len(b),'effect_size':float(a.mean()-b.mean()),'p_value':float(p),'status':'EXPLORATORY'})
    for feature in ['rest_advantage','home_form5','away_form5']:
        x=d[[feature,'home_win']].dropna(); a=x[x.home_win][feature]; b=x[~x.home_win][feature]
        if len(a)>=20 and len(b)>=20:
            try: p=mannwhitneyu(a,b,alternative='two-sided').pvalue
            except Exception: p=1.0
            rows.append({'pattern_id':f'{feature}_HOME_WIN','description':feature,'sample_size_segment':len(a),'sample_size_control':len(b),'effect_size':float(a.median()-b.median()),'p_value':float(p),'status':'EXPLORATORY'})
    return bh(rows)

def oos_model(df):
    d=df.dropna(subset=['home_form5','away_form5']).copy().sort_values('match_date')
    if len(d)<80: return {'status':'INSUFFICIENT_DATA','n':len(d)}
    X=d[['home_form5','away_form5','rest_advantage']].fillna(0); y=d['home_win'].astype(int)
    cut=int(len(d)*.7); hold=int(len(d)*.85)
    model=LogisticRegression(max_iter=500).fit(X.iloc[:cut],y.iloc[:cut])
    p=model.predict_proba(X.iloc[cut:hold])[:,1] if hold>cut else np.array([])
    ph=model.predict_proba(X.iloc[hold:])[:,1] if len(d)>hold else np.array([])
    yh=y.iloc[cut:hold].to_numpy(); yh2=y.iloc[hold:].to_numpy()
    def metrics(yy,pp):
        if len(pp)==0:return {}
        return {'log_loss':float(log_loss(yy,pp,labels=[0,1])),'brier':float(brier_score_loss(yy,pp)),'roc_auc':float(roc_auc_score(yy,pp)) if len(np.unique(yy))>1 else None}
    return {'status':'CALCULATED','n':len(d),'train_n':cut,'validation_n':len(yh),'holdout_n':len(yh2),'validation':metrics(yh,p),'holdout':metrics(yh2,ph),'features':X.columns.tolist()}

def coverage(df):
    g=df.groupby(['competition','season','gender'],dropna=False).agg(matches=('canonical_match_id','nunique'),dates_min=('match_date','min'),dates_max=('match_date','max')).reset_index()
    for c in ['events','shots','SOT','xG','corners','cards','lineups','players','injuries','suspensions','odds','timestamped_odds','PIT','LIVE','settlements']: g[c]=0
    return g


def walk_forward_model(df, min_train=300, step=100):
    d=df.dropna(subset=['home_form5','away_form5']).sort_values('match_date').copy()
    if len(d)<min_train+50: return {'status':'INSUFFICIENT_DATA','n':len(d)}
    X=d[['home_form5','away_form5','rest_advantage']].fillna(0); y=d.home_win.astype(int)
    folds=[]
    for end in range(min_train, len(d), step):
        test_end=min(end+step,len(d));
        if test_end<=end: break
        m=LogisticRegression(max_iter=500).fit(X.iloc[:end],y.iloc[:end]); p=m.predict_proba(X.iloc[end:test_end])[:,1]
        yy=y.iloc[end:test_end].to_numpy()
        folds.append({'train_n':end,'test_n':len(yy),'log_loss':float(log_loss(yy,p,labels=[0,1])),'brier':float(brier_score_loss(yy,p)),'roc_auc':float(roc_auc_score(yy,p)) if len(np.unique(yy))>1 else None})
    return {'status':'CALCULATED','folds':folds,'mean_log_loss':float(np.mean([x['log_loss'] for x in folds])),'mean_brier':float(np.mean([x['brier'] for x in folds]))}
