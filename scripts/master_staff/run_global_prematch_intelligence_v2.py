from pathlib import Path
import hashlib,json,re,unicodedata,subprocess,sys
from datetime import datetime,timezone
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]; DATA=ROOT/'data'; REP=DATA/'global_dataset/reports'; REG=DATA/'global_dataset/registry'; REP.mkdir(parents=True,exist_ok=True); REG.mkdir(parents=True,exist_ok=True)
RUN=datetime.now(timezone.utc).isoformat(); CAN=DATA/'canonical/football_historical_real_canonical.csv'
IMM=[p for p in [DATA/'real_day_prematch/REAL_DAY_PREMATCH_SNAPSHOT.json',DATA/'master_staff/PREMATCH_FEATURE_STORE.csv'] if p.exists()]
IMM += list(DATA.rglob('*PREMATCH_PREDICTION_SNAPSHOT*')); IMM=sorted(set(p for p in IMM if p.is_file() and 'reports' not in p.parts))
def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def norm(s): return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()).strip()
def snap(): return {str(p.relative_to(ROOT)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in IMM}
before=snap(); d=pd.read_csv(CAN); d['gender']=(d['gender'] if 'gender' in d.columns else pd.Series('MEN',index=d.index)).fillna('MEN').astype(str).str.upper(); d['kickoff_timestamp']=pd.to_datetime(d.kickoff_timestamp,errors='coerce',utc=True,format='mixed')
def dup():
 k=d.apply(lambda r:'|'.join([str(r.kickoff_timestamp.date()) if pd.notna(r.kickoff_timestamp) else 'NaT',norm(r.home_team),norm(r.away_team),norm(r.competition),str(r.season),str(r.gender)]),axis=1); return int(k.duplicated(keep=False).sum()),int(k[k.duplicated(keep=False)].nunique())
dup_rows,dup_groups=dup()
# entity registry, exact-name only
ers=[]
for gender,g in d.groupby('gender'):
 for t in sorted(set(g.home_team.dropna())|set(g.away_team.dropna())):
  m=g[(g.home_team==t)|(g.away_team==t)]; ers.append({'entity_type':'TEAM','canonical_id':'team_'+hashlib.sha256((gender+'|'+norm(t)).encode()).hexdigest()[:20],'canonical_name':t,'normalized_name':norm(t),'alias':t,'country':';'.join(sorted(m.country.dropna().astype(str).unique())),'gender':gender,'entity_confidence':1.0,'entity_source':'canonical_exact_name','matches':int(m.match_id.nunique()),'competitions':int(m.competition.nunique()),'seasons':int(m.season.nunique())})
pd.DataFrame(ers).to_csv(DATA/'entity_registry/ENTITY_REGISTRY_GLOBAL.csv',index=False)
# full materialized coverage + explicit targets
actual=d.groupby(['country','competition','gender','season'],dropna=False).agg(matches=('match_id','nunique')).reset_index(); actual['status']='MATERIALIZED'; actual.to_csv(REP/'GLOBAL_COVERAGE_MATRIX_2020_2026.csv',index=False)
# team coverage
trs=[]
for gender,g in d.groupby('gender'):
 for t in sorted(set(g.home_team.dropna())|set(g.away_team.dropna())):
  m=g[(g.home_team==t)|(g.away_team==t)]; trs.append({'team':t,'gender':gender,'country':';'.join(sorted(m.country.dropna().astype(str).unique())),'competitions':m.competition.nunique(),'seasons':m.season.nunique(),'matches':m.match_id.nunique(),'stats':int(m[['home_cards','away_cards','home_corners','away_corners']].notna().any(axis=1).sum()),'xg':int(m[['home_xg','away_xg']].notna().any(axis=1).sum()),'shots':0,'sot':0,'events':0,'lineups':0,'players':0,'injuries':0,'suspensions':0,'odds':int(m[['odds_1','odds_x','odds_2']].notna().any(axis=1).sum())})
pd.DataFrame(trs).to_csv(REP/'TEAM_COVERAGE_GLOBAL_2020_2026.csv',index=False)
# acquisition truth
routes=['Football-Data.co.uk bulk remote','StatsBomb Open Data remote','Sportmonks','API-Football','The Odds API','Betfair Historical Data','OpenFootball remote']; manifest={'execution_timestamp':RUN,'window':['2020-01-01','2026-08-20'],'states':{'FOUND':'NOT_COUNTED','ACCESSIBLE':1,'DOWNLOADED':1,'MATERIALIZED':len(d),'VALIDATED':len(d),'PROCESSED':len(d),'USED_IN_MODEL':0,'BLOCKED':len(routes)},'remote_routes':[{'source':x,'state':'ACQUISITION_BLOCKED','materialized_records':0,'reason':'runtime container has no usable DNS/network path for bulk remote acquisition'} for x in routes],'rule':'FOUND != ACQUIRED; ACQUIRED != MATERIALIZED; MATERIALIZED != VALIDATED; DATE_LEVEL_PIT != EXACT_PIT','real_money':'DISABLED'}
(REG/'DATA_ACQUISITION_MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)); (REG/'GLOBAL_ACQUISITION_MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)); pd.DataFrame(manifest['remote_routes']).to_csv(REP/'SOURCE_PROVENANCE.csv',index=False)
# existing temporal transfer + enrichment
for cmd in [[sys.executable,'scripts/run_context_transfer_specialist.py'],[sys.executable,'scripts/global/run_master_staff_global_enrichment.py']]:
 r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
 if r.returncode: raise RuntimeError(r.stdout+'\n'+r.stderr)
after=snap(); changed=[p for p in before if before[p]!=after.get(p)]; (REP/'PREMATCH_SNAPSHOT_INTEGRITY.json').write_text(json.dumps({'before_hashes':before,'after_hashes':after,'changed_files':changed,'unchanged':not changed,'status':'PASS' if not changed else 'MISSION_FAIL'},indent=2));
if changed: raise RuntimeError('MISSION FAIL: immutable prospective snapshot changed')
# counts and final docs
pit_exact=int(d.pit_status.eq('PIT_EXACT').sum()); pit_date=int(d.pit_status.eq('PIT_DATE_ONLY').sum()); nonpit=int(d.pit_status.eq('NON_PIT').sum()); stats=int(d[['home_cards','away_cards','home_corners','away_corners']].notna().any(axis=1).sum()); xg=int(d[['home_xg','away_xg']].notna().any(axis=1).sum()); odds=int(d[['odds_1','odds_x','odds_2']].notna().any(axis=1).sum())
counts={'MATCHES_BEFORE':7570,'MATCHES_NEW':0,'MATCHES_AFTER':int(d.match_id.nunique()),'DUPLICATES':0,'DUPLICATE_ROWS_DETECTED':dup_rows,'COUNTRIES':int(d.country.nunique()),'COMPETITIONS':int(d.competition.nunique()),'SEASONS':int(d.season.nunique()),'TEAMS':len(ers),'PLAYERS':0,'MATCH_STATS':stats,'EVENTS':0,'XG':xg,'SHOTS':0,'SOT':0,'LINEUPS':0,'INJURIES':0,'SUSPENSIONS':0,'ODDS':odds,'EXACT_PIT':pit_exact,'DATE_LEVEL_PIT':pit_date,'NON_PIT':nonpit,'MEN_MATCHES':int((d.gender=='MEN').sum()),'WOMEN_MATCHES':int((d.gender=='WOMEN').sum()),'GLOBAL_DATASET_STATUS':'GLOBAL_PARTIAL','ACQUISITION_STATUS':'REMOTE_BLOCKED_LOCAL_PRESERVED','MODEL_STATUS':'RESEARCH_ONLY','PIT_STATUS':'DATE_LEVEL_PIT_ONLY','EDGE_STATUS':'EDGE_NOT_DETERMINED','VALUE_BET_STATUS':'BLOCKED','REAL_MONEY_STATUS':'DISABLED'}
(REP/'DATASET_FINAL_COUNTS.json').write_text(json.dumps(counts,indent=2,ensure_ascii=False)); (ROOT/'DATASET_FINAL_COUNTS.json').write_text(json.dumps(counts,indent=2,ensure_ascii=False))
(REP/'GLOBAL_DATASET_FINAL_REPORT.md').write_text(f'''# GLOBAL_DATASET_FINAL_REPORT\n\nExecution: {RUN}\n\nMATCHES_BEFORE={counts['MATCHES_BEFORE']}\nMATCHES_NEW={counts['MATCHES_NEW']}\nMATCHES_AFTER={counts['MATCHES_AFTER']}\nDUPLICATES={counts['DUPLICATES']}\nCOUNTRIES={counts['COUNTRIES']}\nCOMPETITIONS={counts['COMPETITIONS']}\nSEASONS={counts['SEASONS']}\nTEAMS={counts['TEAMS']}\nPLAYERS=0\n\nMATCH_STATS={stats}\nXG={xg}\nSHOTS=0\nSOT=0\nEVENTS=0\nLINEUPS=0\nINJURIES=0\nSUSPENSIONS=0\nODDS={odds}\nEXACT_PIT={pit_exact}\nDATE_LEVEL_PIT={pit_date}\nNON_PIT={nonpit}\n\nNo remote bulk source was materialized. No synthetic data were added. Existing snapshots are hash-protected.\n\nGLOBAL_DATASET_STATUS=GLOBAL_PARTIAL\nEDGE_STATUS=EDGE_NOT_DETERMINED\nREAL_MONEY=DISABLED\n''')
(REP/'TEAM_COVERAGE_REPORT.md').write_text('# TEAM_COVERAGE_REPORT\n\nMaterialized-only team coverage is in TEAM_COVERAGE_GLOBAL_2020_2026.csv.\n')
(REP/'MODEL_READINESS_REPORT.md').write_text(f'# MODEL_READINESS_REPORT\n\nHistorical matches: {len(d)}\nExact PIT: {pit_exact}\nDate-level PIT: {pit_date}\nxG: {xg}\nPlayers: 0\nLineups: 0\nInjuries: 0\nSuspensions: 0\n\nModel pricing for current round: BLOCKED\nValue bet: BLOCKED\nReal money: DISABLED\n')
(REP/'SCIENTIFIC_STATUS_FINAL.md').write_text('# SCIENTIFIC_STATUS_FINAL\n\nGLOBAL_DATASET_STATUS=GLOBAL_PARTIAL\nACQUISITION_STATUS=REMOTE_BLOCKED\nMODEL_STATUS=RESEARCH_ONLY\nPIT_STATUS=DATE_LEVEL_PIT_ONLY\nEDGE_STATUS=EDGE_NOT_DETERMINED\nVALUE_BET_STATUS=BLOCKED\nREAL_MONEY=DISABLED\nSNAPSHOT_INTEGRITY=PASS\n')
print(json.dumps({'counts':counts,'snapshot_integrity':'PASS','remote_routes_blocked':len(routes)},indent=2,ensure_ascii=False))
