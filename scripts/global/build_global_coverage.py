from pathlib import Path
import pandas as pd, json
ROOT=Path(__file__).resolve().parents[2]
d=pd.read_csv(ROOT/'data/canonical/football_historical_real_canonical.csv')
d['gender']='MEN' if 'gender' not in d else d['gender'].fillna('MEN').str.upper()
d['year']=pd.to_datetime(d.kickoff_timestamp,errors='coerce').dt.year
# global competition-season matrix
mat=d.groupby(['country','competition','gender','season']).agg(matches=('match_id','nunique'),teams=('home_team','nunique')).reset_index()
mat['stats_coverage_pct']=d.groupby(['country','competition','gender','season']).apply(lambda x: round(100*x[['home_cards','away_cards','home_corners','away_corners']].notna().any(axis=1).mean(),2)).values
mat.to_csv(ROOT/'data/global_dataset/reports/GLOBAL_COVERAGE_MATRIX.csv',index=False)
# team coverage
a=[]
for (team,gender),g in pd.concat([d[['home_team','gender']].rename(columns={'home_team':'team'}),d[['away_team','gender']].rename(columns={'away_team':'team'})]).groupby(['team','gender']):
 matches=d[(d.home_team==team)|(d.away_team==team)]
 a.append({'team':team,'gender':gender,'countries':';'.join(sorted(matches.country.dropna().astype(str).unique())),'competitions':';'.join(sorted(matches.competition.dropna().astype(str).unique())),'seasons':matches.season.nunique(),'matches':matches.match_id.nunique(),'cards_matches':int(matches[['home_cards','away_cards']].notna().any(axis=1).sum()),'corners_matches':int(matches[['home_corners','away_corners']].notna().any(axis=1).sum()),'xg_matches':int(matches[['home_xg','away_xg']].notna().any(axis=1).sum()),'odds_matches':int(matches[['odds_1','odds_x','odds_2']].notna().any(axis=1).sum()),'pit_exact':int(matches.pit_status.eq('PIT_EXACT').sum())})
pd.DataFrame(a).sort_values('matches',ascending=False).to_csv(ROOT/'data/global_dataset/reports/TEAM_COVERAGE_GLOBAL.csv',index=False)
# acquisition priority: explicit scientific scoring, transparent formula
targets=pd.read_csv(ROOT/'data/global_dataset/reports/GLOBAL_COVERAGE_MATRIX.csv')
targets['gap']=targets['matches'].apply(lambda x:max(0,300-x))
targets['scientific_value']=targets['competition'].map(lambda x: 10 if any(k in x.lower() for k in ['libert','sudamericana','premier','brasile','serie a','bundesliga','laliga','ligue 1']) else 6)
targets['priority_score']=targets['scientific_value']*2 + targets['gap']/50
cols=['country','competition','gender','season','matches','gap','scientific_value','priority_score']
targets.sort_values('priority_score',ascending=False)[cols].to_csv(ROOT/'data/global_dataset/reports/ACQUISITION_PRIORITY.csv',index=False)
print('coverage built',len(mat),len(a))
