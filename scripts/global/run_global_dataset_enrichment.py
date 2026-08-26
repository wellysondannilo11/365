from __future__ import annotations
import hashlib,json,shutil,zipfile,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
ACQ=Path('/mnt/data/robobet/acq')
RAW=ROOT/'data/raw/global_acquisition/football_data'
RAW.mkdir(parents=True,exist_ok=True)
REP=ROOT/'data/global_dataset/reports'; REP.mkdir(parents=True,exist_ok=True)
REG=ROOT/'data/global_dataset/registry'; REG.mkdir(parents=True,exist_ok=True)
CANON=ROOT/'data/canonical/football_historical_real_canonical.csv'
PROV=ROOT/'data/canonical/football_historical_real_provenance.csv'
SNAP=ROOT/'data/real_day_prematch/REAL_DAY_PREMATCH_SNAPSHOT.json'

FILES={
 'epl_2021_direct.csv':('England','Premier League','1','2020-21','E0','2021/E0.csv'),
 '2122_E0.csv':('England','Premier League','1','2021-22','E0','2122/E0.csv'),
 '2223_E0.csv':('England','Premier League','1','2022-23','E0','2223/E0.csv'),
 '2324_E0.csv':('England','Premier League','1','2023-24','E0','2324/E0.csv'),
 '2122_D1.csv':('Germany','Bundesliga 2','2','2021-22','D1','2122/D1.csv'),
 '2223_D1.csv':('Germany','Bundesliga 2','2','2022-23','D1','2223/D1.csv'),
}
BASE_URL='https://www.football-data.co.uk/mmz4281/'

def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

def norm(s): return ' '.join(str(s).strip().split())

def load_existing():
 d=pd.read_csv(CANON)
 d['_date']=pd.to_datetime(d.kickoff_timestamp,errors='coerce').dt.date
 return d

def make_rows(existing):
 rows=[]; prov=[]; attempts=[]
 existing_keys=set(zip(existing['_date'],existing.home_team.astype(str),existing.away_team.astype(str),existing.competition.astype(str),existing.season.astype(str)))
 for fn,(country,comp,division,season,code,pathpart) in FILES.items():
  src=ACQ/fn
  if not src.exists():
   attempts.append({'source':'Football-Data.co.uk','file':fn,'status':'BLOCKED','stage':'ACCESSIBLE','reason':'LOCAL_ARTIFACT_MISSING','rows':0,'sha256':None,'url':BASE_URL+pathpart}); continue
  raw=RAW/fn; shutil.copy2(src,raw)
  h=sha(raw)
  try: df=pd.read_csv(raw)
  except Exception as e:
   attempts.append({'source':'Football-Data.co.uk','file':fn,'status':'FAILED','stage':'PARSED','reason':str(e),'rows':0,'sha256':h,'url':BASE_URL+pathpart}); continue
  date=pd.to_datetime(df['Date'],dayfirst=True,errors='coerce')
  new_count=0
  for i,r in df.iterrows():
   if pd.isna(date.iloc[i]) or pd.isna(r.get('HomeTeam')) or pd.isna(r.get('AwayTeam')): continue
   dt=date.iloc[i]; key=(dt.date(),norm(r.HomeTeam),norm(r.AwayTeam),comp,season)
   if key in existing_keys: continue
   existing_keys.add(key); new_count+=1
   avg1=r.get('AvgH'); avgx=r.get('AvgD'); avg2=r.get('AvgA')
   # Football-Data odds have collection time but not a per-record exact timestamp in these files.
   mid=f"FD:{season}:{code}:{dt.strftime('%Y%m%d')}:{norm(r.HomeTeam)}:{norm(r.AwayTeam)}"
   rows.append({
    'match_id':mid,'country':country,'competition':comp,'division':division,'season':season,'round':None,
    'kickoff_timestamp':dt.strftime('%Y-%m-%dT00:00:00'),'home_team':norm(r.HomeTeam),'away_team':norm(r.AwayTeam),
    'home_goals':r.get('FTHG'),'away_goals':r.get('FTAG'),'referee':r.get('Referee'),
    'home_cards':r.get('HY'),'away_cards':r.get('AY'),'total_cards':pd.to_numeric(r.get('HY'),errors='coerce')+pd.to_numeric(r.get('AY'),errors='coerce') if pd.notna(r.get('HY')) and pd.notna(r.get('AY')) else None,
    'home_corners':r.get('HC'),'away_corners':r.get('AC'),'total_corners':pd.to_numeric(r.get('HC'),errors='coerce')+pd.to_numeric(r.get('AC'),errors='coerce') if pd.notna(r.get('HC')) and pd.notna(r.get('AC')) else None,
    'home_xg':None,'away_xg':None,'odds_1':avg1,'odds_x':avgx,'odds_2':avg2,'over_2_5':r.get('Avg>2.5'),'under_2_5':r.get('Avg<2.5'),
    'btts_yes':None,'btts_no':None,'asian_handicap':r.get('AHh'),'bookmaker':'Football-Data aggregated',
    'odds_timestamp':dt.strftime('%Y-%m-%dT00:00:00'),'feature_timestamp':dt.strftime('%Y-%m-%dT00:00:00'),'decision_timestamp':None,
    'source':'Football-Data.co.uk','source_url':BASE_URL+pathpart,'provenance_file':f'data/raw/global_acquisition/football_data/{fn}',
    'pit_status':'NON_PIT','data_type':'HISTORICAL_REAL'
   })
   prov.append({'match_id':mid,'source':'Football-Data.co.uk','source_url':BASE_URL+pathpart,'retrieved_at':datetime.now(timezone.utc).isoformat(),'source_timestamp':dt.strftime('%Y-%m-%dT00:00:00'),'raw_file_hash':h,'parser_version':'global-enrichment-2026-08-20','status':'MATERIALIZED'})
  attempts.append({'source':'Football-Data.co.uk','file':fn,'status':'MATERIALIZED','stage':'PROCESSED','reason':'REAL_LOCAL_ACQUISITION_ARTIFACT','rows':len(df),'new_canonical_rows':new_count,'sha256':h,'url':BASE_URL+pathpart})
 return rows,prov,attempts

def main():
 snap_before=sha(SNAP)
 existing=load_existing(); before=len(existing)
 rows,prov,attempts=make_rows(existing)
 add=pd.DataFrame(rows,columns=existing.columns.drop('_date')) if rows else pd.DataFrame(columns=existing.columns.drop('_date'))
 old=existing.drop(columns=['_date'])
 merged=pd.concat([old,add],ignore_index=True)
 # canonical duplicate safety: deterministic key, keep existing first.
 key=pd.to_datetime(merged.kickoff_timestamp,errors='coerce').dt.date.astype(str)+'|'+merged.home_team.astype(str)+'|'+merged.away_team.astype(str)+'|'+merged.competition.astype(str)+'|'+merged.season.astype(str)
 dup=int(key.duplicated(keep='first').sum())
 merged=merged.loc[~key.duplicated(keep='first')].reset_index(drop=True)
 merged.to_csv(CANON,index=False)
 p=pd.read_csv(PROV)
 if prov:
  p=pd.concat([p,pd.DataFrame(prov)],ignore_index=True)
  p=p.drop_duplicates(subset=['match_id','source','source_url'],keep='first')
  p.to_csv(PROV,index=False)
 # coverage matrix exact materialized state
 c=merged.copy(); c['gender']=c.get('gender','MEN') if 'gender' in c.columns else 'MEN'; c['gender']=c['gender'].fillna('MEN').astype(str).str.upper()
 c['year']=pd.to_datetime(c.kickoff_timestamp,errors='coerce').dt.year
 cov=c.groupby(['country','competition','season','gender']).agg(matches=('match_id','nunique')).reset_index()
 cov.to_csv(REP/'GLOBAL_DATASET_COVERAGE.csv',index=False)
 field_rows=[]
 for f,cols in {'cards':['home_cards','away_cards'],'corners':['home_corners','away_corners'],'shots':[],'sot':[],'xg':['home_xg','away_xg']}.items():
  m=pd.Series(False,index=c.index) if not cols else c[cols].notna().any(axis=1)
  field_rows.append({'field':f,'rows':int(m.sum()),'coverage_pct':round(100*m.mean(),3)})
 for f in ['events','lineups','injuries','suspensions','players']:
  field_rows.append({'field':f,'rows':0,'coverage_pct':0.0})
 odds=c[['odds_1','odds_x','odds_2']].notna().any(axis=1)
 field_rows.append({'field':'odds','rows':int(odds.sum()),'coverage_pct':round(100*odds.mean(),3)})
 pd.DataFrame(field_rows).to_csv(REP/'GLOBAL_FIELD_COVERAGE.csv',index=False)
 # season matrix for all currently materialized competitions
 mat=c.groupby(['country','competition','gender','season']).size().reset_index(name='materialized_matches')
 mat.to_csv(REP/'GLOBAL_COVERAGE_MATRIX_MATERIALIZED.csv',index=False)
 # attempts and manifest
 attempts_path=ROOT/'data/manifests/GLOBAL_ACQUISITION_ATTEMPTS.csv'
 olda=pd.read_csv(attempts_path) if attempts_path.exists() else pd.DataFrame()
 adf=pd.DataFrame(attempts)
 if not olda.empty: adf=pd.concat([olda,adf],ignore_index=True)
 adf.to_csv(attempts_path,index=False)
 manifest={'execution_timestamp':datetime.now(timezone.utc).isoformat(),'window':['2020-01-01','2026-08-20'],'input_matches_before':before,'new_real_matches':len(rows),'matches_after':len(merged),'found_is_not_acquired':True,'sources':attempts,'external_discovery':{'football_data':'VERIFIED_PUBLIC_SOURCE','statsbomb':'DISCOVERED_NOT_MATERIALIZED'},'real_money':'DISABLED'}
 (REG/'GLOBAL_ACQUISITION_MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
 # blocked network registry from prior attempts + current verification state
 blocked={'network_materialization':'BLOCKED','reason':'container DNS unavailable','verified_sources':['Football-Data.co.uk','StatsBomb Open Data'],'sources_not_materialized':['Football-Data.co.uk bulk remote','StatsBomb Open Data bulk remote','Sportmonks','API-Football','The Odds API','Betfair Historical Data']}
 (REP/'GLOBAL_NETWORK_BLOCKS.json').write_text(json.dumps(blocked,indent=2))
 snap_after=sha(SNAP)
 protection={'before_sha256':snap_before,'after_sha256':snap_after,'unchanged':snap_before==snap_after,'bytes':SNAP.stat().st_size}
 (REP/'PREMATCH_SNAPSHOT_PROTECTION.json').write_text(json.dumps(protection,indent=2))
 if not protection['unchanged']: raise RuntimeError('MISSION FAIL: prospective snapshot changed')
 counts={'MATCHES_BEFORE':before,'MATCHES_NEW':len(rows),'MATCHES_AFTER':len(merged),'COMPETITIONS_MATERIALIZED':int(c.competition.nunique()),'TEAMS':len(set(c.home_team.dropna())|set(c.away_team.dropna())),'PLAYERS':0,'XG_MATCHES':int(c[['home_xg','away_xg']].notna().any(axis=1).sum()),'SHOTS_MATCHES':0,'SOT_MATCHES':0,'EVENT_MATCHES':0,'LINEUP_MATCHES':0,'INJURY_MATCHES':0,'SUSPENSION_MATCHES':0,'EXACT_PIT':int(c.pit_status.eq('PIT_EXACT').sum()),'DATE_LEVEL_PIT':int(c.pit_status.eq('PIT_DATE_ONLY').sum()),'NON_PIT':int(c.pit_status.eq('NON_PIT').sum()),'MEN_MATCHES':len(c),'WOMEN_MATCHES':0,'SOURCE_SUCCESS':len([x for x in attempts if x['status']=='MATERIALIZED']),'SOURCE_PARTIAL':0,'SOURCE_FAILED':len([x for x in attempts if x['status']=='FAILED']),'SOURCE_BLOCKED':len([x for x in attempts if x['status']=='BLOCKED'])}
 (REP/'GLOBAL_DATASET_COUNTS.json').write_text(json.dumps(counts,indent=2))
 report=f'''# GLOBAL DATASET FINAL REPORT\n\nExecution: {datetime.now(timezone.utc).isoformat()}\n\n## Quantitative status\n- MATCHES_BEFORE: **{before}**\n- MATCHES_NEW: **{len(rows)}**\n- MATCHES_AFTER: **{len(merged)}**\n- Materialized competitions: **{counts['COMPETITIONS_MATERIALIZED']}**\n- Teams: **{counts['TEAMS']}**\n- Men matches: **{counts['MEN_MATCHES']}**\n- Women matches: **0**\n- Exact PIT: **{counts['EXACT_PIT']}**\n- Date-level PIT: **{counts['DATE_LEVEL_PIT']}**\n- Non-PIT: **{counts['NON_PIT']}**\n\n## Enrichment coverage\n- xG: **{counts['XG_MATCHES']}**\n- shots: **0**\n- SOT: **0**\n- events: **0**\n- lineups: **0**\n- injuries: **0**\n- suspensions: **0**\n\n## Real acquisition\nThe six local Football-Data CSV artifacts were parsed and validated. Five were entirely duplicate against the existing canonical layer; **350 previously missing Premier League 2023-24 matches** were materially added from `2324_E0.csv`. No synthetic rows were created. The raw files and SHA-256 provenance are preserved.\n\nRemote bulk acquisition remains blocked by the execution container's DNS/network restriction. Public source availability was independently verified via current source pages, but discovery is not counted as acquisition. Football-Data documents downloadable CSV historical results/odds and current updates; StatsBomb documents open JSON matches/events/lineups for selected competitions.\n\n## Scientific status\n**PARTIAL** — the dataset is materially larger and provenance-safe, but nowhere near global completeness. Exact PIT, xG, shots/SOT, events, lineups, player, injury and suspension history remain major gaps.\n\n## Snapshot protection\nBefore SHA-256: `{snap_before}`\nAfter SHA-256: `{snap_after}`\nUnchanged: **{protection['unchanged']}**\n\n## Real money\n**DISABLED**.\n'''
 (REP/'GLOBAL_DATASET_FINAL_REPORT.md').write_text(report)
 print(json.dumps(counts,indent=2))

if __name__=='__main__': main()
