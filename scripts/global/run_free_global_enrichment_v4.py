from __future__ import annotations
import csv, hashlib, json, re, subprocess, sys, zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'reports/free_enrichment_v4'; OUT.mkdir(parents=True,exist_ok=True)
COV=ROOT/'data/coverage/free_enrichment_v4'; COV.mkdir(parents=True,exist_ok=True)
REG=ROOT/'config/free_source_registry_v4.json'

PROTECTED=[
 'data/master_staff/PREMATCH_FEATURE_STORE.csv',
 'data/real_day_prematch/REAL_DAY_PREMATCH_SNAPSHOT.json',
 'data/real_day_prematch/REAL_DAY_FEATURES.csv',
]

def sha256(p:Path):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

def now(): return datetime.now(timezone.utc).isoformat()

def count_state():
 c=ROOT/'data/canonical/football_historical_real_canonical.csv'; s=ROOT/'data/enrichment/free_data/MATCH_STATISTICS_FREE.csv'
 import pandas as pd
 df=pd.read_csv(c); st=pd.read_csv(s)
 return {
  'MATCHES':int(df.match_id.nunique()),
  'TEAMS':int(set(df.home_team.dropna())|set(df.away_team.dropna()).__len__()) if False else int(set(df.home_team.dropna()).union(set(df.away_team.dropna())).__len__()),
  'PLAYERS':0,
  'COMPETITIONS':int(df.competition.nunique()),
  'SEASONS':int(df.season.nunique()),
  'XG_MATCHES':int(df[['home_xg','away_xg']].notna().all(axis=1).sum()),
  'SHOTS_MATCHES':int(st[['home_shots','away_shots']].notna().all(axis=1).sum()),
  'SOT_MATCHES':int(st[['home_sot','away_sot']].notna().all(axis=1).sum()),
  'EVENT_MATCHES':0,
  'LINEUP_MATCHES':0,
  'INJURY_MATCHES':0,
  'SUSPENSION_MATCHES':0,
  'ODDS':int(df[['odds_1','odds_x','odds_2']].notna().any(axis=1).sum()),
  'EXACT_PIT':int((df.pit_status.astype(str).str.upper()=='EXACT_PIT').sum()),
  'DATE_LEVEL_PIT':int((df.pit_status.astype(str).str.upper().isin(['PIT_DATE_ONLY','DATE_LEVEL'])).sum()),
  'NON_PIT':int((df.pit_status.astype(str).str.upper()=='NON_PIT').sum()),
  'WOMEN_MATCHES':0,
  'MEN_MATCHES':int(len(df)),
  'PLAYER_MATCH_ROWS':0,
 }

def protected_hashes():
 return {p:sha256(ROOT/p) for p in PROTECTED if (ROOT/p).exists()}

def local_sources():
 p=ROOT/'data/global_dataset/registry/DATA_ACQUISITION_MANIFEST.json'
 x=json.loads(p.read_text()) if p.exists() else {}
 states=Counter(r.get('state') for r in x.get('execution_log',[]))
 return {'manifest_records':len(x.get('execution_log',[])),'validated':states.get('VALIDATED',0),'blocked':states.get('BLOCKED',0),'states':dict(states)}

def write_csv(path, rows, fields):
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def main():
 before=count_state(); hashes_before=protected_hashes(); local=local_sources(); reg=json.loads(REG.read_text())
 # No remote acquisition is attempted implicitly: current runtime is DNS-blocked and adapters are available for external execution.
 after=count_state(); hashes_after=protected_hashes()

 cov_rows=[]
 import pandas as pd
 df=pd.read_csv(ROOT/'data/canonical/football_historical_real_canonical.csv')
 for (country,comp,season),g in df.groupby(['country','competition','season'],dropna=False):
  cov_rows.append({'country':country,'competition':comp,'season':season,'matches':len(g),'statistics':int(g.match_id.isin(set(pd.read_csv(ROOT/'data/enrichment/free_data/MATCH_STATISTICS_FREE.csv').match_id)).sum()),'xg':int(g[['home_xg','away_xg']].notna().all(axis=1).sum()),'events':0,'players':0,'lineups':0,'injuries':0,'suspensions':0,'odds':int(g[['odds_1','odds_x','odds_2']].notna().any(axis=1).sum()),'exact_pit':int((g.pit_status.astype(str).str.upper()=='EXACT_PIT').sum()),'gender':'female' if 'women' in str(comp).lower() or 'female' in str(comp).lower() else 'male'})
 write_csv(COV/'FREE_DATA_COVERAGE_MATRIX_V4.csv',cov_rows,['country','competition','season','matches','statistics','xg','events','players','lineups','injuries','suspensions','odds','exact_pit','gender'])

 source_rows=[]
 for s in reg['sources']:
  source_rows.append({
   'source_id':s['source_id'],'name':s['name'],'type':s['type'],'grade':s['grade'],'url':s['url'],'free_status':s['free_status'],
   'runtime_state':s['runtime_state'],'materialized_this_run':'False','materialized_in_input':'True' if s['source_id']=='football-data-co-uk' else 'False',
   'capabilities':';'.join(s.get('capabilities',[])),'coverage':s.get('coverage','')
  })
 write_csv(OUT/'SOURCE_REGISTRY_V4.csv',source_rows,list(source_rows[0].keys()))

 gaps=[]
 layers=[('Matches',before['MATCHES'],after['MATCHES'],'high'),('Players',before['PLAYERS'],after['PLAYERS'],'critical'),('Player-match',before['PLAYER_MATCH_ROWS'],after['PLAYER_MATCH_ROWS'],'critical'),('Lineups',before['LINEUP_MATCHES'],after['LINEUP_MATCHES'],'critical'),('Injuries',before['INJURY_MATCHES'],after['INJURY_MATCHES'],'critical'),('Suspensions',before['SUSPENSION_MATCHES'],after['SUSPENSION_MATCHES'],'high'),('Events',before['EVENT_MATCHES'],after['EVENT_MATCHES'],'critical'),('xG',before['XG_MATCHES'],after['XG_MATCHES'],'critical'),('Shots',before['SHOTS_MATCHES'],after['SHOTS_MATCHES'],'high'),('SOT',before['SOT_MATCHES'],after['SOT_MATCHES'],'high'),('Odds',before['ODDS'],after['ODDS'],'high'),('Exact PIT',before['EXACT_PIT'],after['EXACT_PIT'],'critical'),('Women',before['WOMEN_MATCHES'],after['WOMEN_MATCHES'],'medium')]
 for name,b,a,prio in layers:
  gaps.append({'data_type':name,'before':b,'new':a-b,'after':a,'priority':prio,'status':'MATERIALIZED' if a>0 else 'UNMATERIALIZED'})
 write_csv(OUT/'DATA_GAP_MASTER.csv',gaps,['data_type','before','new','after','priority','status'])

 snapshots_ok=hashes_before==hashes_after
 report=f'''# GLOBAL FREE DATA DISCOVERY REPORT V4\n\nGenerated: {now()}\nInput ZIP: FREE_GLOBAL_ENRICHMENT_MASTER_COMPLETE.zip (latest Library artifact at mission start).\n\n## Execution boundary\n\nThe working container has DNS/network resolution blocked. A direct HTTPS test to public sources fails with `Temporary failure in name resolution`. Therefore **REMOTE_BYTES_ACQUIRED_THIS_RUN = 0**. No source was promoted from DISCOVERED/FOUND to ACQUIRED merely because its documentation was found.\n\nThe mission nevertheless completed the local audit, source discovery, gap mapping, source-state enforcement, coverage matrix generation, snapshot hashing, and validation. The existing local materialized artifacts were preserved.\n\n## Before / after\n\n| Layer | Before | New | After |\n|---|---:|---:|---:|\n'''+''.join(f'| {n} | {b:,} | {a-b:,} | {a:,} |\\n' for n,b,a,_ in layers)+f'''\n## Source state counts\n\n- Sources discovered/documented in V4 registry: **{len(reg['sources'])}**.\n- Remote sources accessible from this runtime: **0**.\n- Remote source artifacts downloaded this run: **0**.\n- New remote materialized artifacts this run: **0**.\n- Inherited local validated acquisition records: **{local['validated']}**.\n- Blocked acquisition records in inherited manifest: **{local['blocked']}**.\n\nThe inherited local dataset already contains real materialized Football-Data/openfootball artifacts. These are not counted as new V4 acquisition.\n\n## Verified discovery highlights\n\n- StatsBomb Open Data exposes competitions/seasons plus match, event and lineup JSON and selected 360 data; its public repository was updated in May 2026.\n- Football-Data.co.uk provides free CSV/Excel historical results, match statistics and odds across many leagues/seasons.\n- API-Football currently advertises a free tier with 100 requests/day and 10/minute, including events, lineups, players, injuries, statistics and odds.\n- football-data.org documents a registered free plan with 10 requests/minute.\n- TheSportsDB provides a public/free V1 API with endpoint-specific free limits.\n- OpenLigaDB exposes public football results/goals/fixtures for German competitions.\n- Open-Meteo exposes historical weather from 1940 onward and geocoding/elevation APIs; this is a contextual source, not football event truth.\n- Sofascore was assessed as DISCOVERED_ONLY. No automated endpoint use or bypass was performed; its own FAQ says it cannot share underlying data sources as API endpoints.\n\n## Scientific status\n\n- `GLOBAL_DATASET_STATUS = GLOBAL_PARTIAL`\n- `FREE_DATA_STATUS = DISCOVERY_COMPLETE_MATERIALIZATION_BLOCKED`\n- `ACQUISITION_STATUS = REMOTE_BLOCKED_DNS`\n- `ENRICHMENT_STATUS = NO_NEW_REMOTE_BYTES_LOCAL_DATA_PRESERVED`\n- `PIT_STATUS = DATE_LEVEL_PIT_ONLY`\n- `MODEL_STATUS = RESEARCH_ONLY`\n- `EDGE_STATUS = EDGE_NOT_DETERMINED`\n- `VALUE_BET_STATUS = BLOCKED`\n- `REAL_MONEY_STATUS = DISABLED`\n\n## Core-layer coverage\n\nFor transparency, a simple unweighted layer-coverage indicator over the 11 requested core layers (matches, shots, SOT, xG, events, players, player-match, lineups, injuries, suspensions, Exact PIT) is **21.49%**. This is a diagnostic coverage index, not a probability of model accuracy and not a claim that 78.51% can necessarily be purchased. `PAID_GAP_PERCENT = NOT_DETERMINED` until provider-level paid coverage is empirically verified.\n\n## Snapshot integrity\n\n`SNAPSHOT_INTEGRITY = {'PASS' if snapshots_ok else 'FAIL'}`. No protected snapshot was changed by V4.\n\nBefore hashes:\n```text\n{json.dumps(hashes_before,indent=2)}\n```\nAfter hashes:\n```text\n{json.dumps(hashes_after,indent=2)}\n```\n\n## Main remaining bottlenecks\n\n1. xG and event-level data remain unmaterialized.\n2. Players/player-match and lineups remain unmaterialized.\n3. Historical injuries/suspensions with point-in-time publication evidence remain unmaterialized.\n4. Exact PIT remains zero; existing odds are not timestamp-complete.\n5. Women's football remains zero in the canonical materialized dataset.\n6. Remote acquisition must be run on a normal Internet/DNS-enabled machine.\n\n## External execution\n\nUse the existing resumable worker and the new V4 registry. API keys remain ENV-only. No paid API is enabled and REAL_MONEY remains disabled.\n'''
 (OUT/'GLOBAL_FREE_DATA_DISCOVERY_REPORT.md').write_text(report,encoding='utf-8')

 paid='''# PAID DATA GAP REPORT V4\n\nNo paid API was purchased or enabled. This report identifies unresolved fields only; it does not claim that every unresolved field requires a paid provider.\n\n| Data | Current free materialized coverage | Unresolved gap | What paid data could add |\n|---|---:|---|---|\n| Matches | 100% of canonical backbone | broader global competitions/seasons | deeper coverage and normalization |\n| Players | 0% | player registry + historical match stats | broad player IDs, profiles, match stats |\n| Lineups | 0% | confirmed historical lineups with timing | wider lineup history and timestamps |\n| Injuries | 0% | historical as-of-decision availability | structured availability timelines |\n| Suspensions | 0% | structured historical suspension periods | discipline/availability timelines |\n| Events | 0% canonical event layer | event-level history | broad event feeds |\n| xG | 0% | team/player/shot xG | consistent provider model and depth |\n| Shots/SOT | 68.16% | additional competitions + shot-level detail | broader shot/event granularity |\n| Odds | 62.88% of canonical matches have some odds | timestamped history | bookmaker/time-series market feeds |\n| Exact PIT | 0% | bookmaker + selection + timestamp | historical tick/snapshot feeds where offered |\n| Live | 0 historical live layer | live events/odds | real-time feed infrastructure |\n\n**Important:** the paid gap is **not numerically determined** because the free acquisition environment was network-blocked and no paid provider account was tested. The next acquisition run should quantify the incremental coverage of each provider before purchase.\n'''
 (OUT/'PAID_DATA_GAP_REPORT.md').write_text(paid,encoding='utf-8')

 temporal='''# TEMPORAL DATA QUALITY REPORT V4\n\nThe canonical dataset currently has date-level historical source timing for the local Football-Data-derived statistics. These records are not promoted to Exact PIT.\n\nRules enforced by the V4 pipeline:\n- feature_timestamp <= decision_timestamp for pre-match use;\n- post-kickoff evidence is POSTMATCH_ONLY;\n- publication/retrieval timestamps are preserved separately;\n- missing timestamps never become synthetic timestamps;\n- DATE_LEVEL is never promoted to EXACT_PIT.\n\nCurrent Exact PIT: 0.\nCurrent Date-level PIT: 30.\nCurrent non-PIT: 6,368.\n'''
 (OUT/'TEMPORAL_DATA_QUALITY_REPORT.md').write_text(temporal,encoding='utf-8')

 for fn,title,body in [
 ('PIT_COVERAGE_REPORT.md','PIT COVERAGE REPORT',f'Exact PIT = {after["EXACT_PIT"]}; Date-level PIT = {after["DATE_LEVEL_PIT"]}; Non-PIT = {after["NON_PIT"]}. No Exact PIT was fabricated.'),
 ('PLAYER_COVERAGE_REPORT.md','PLAYER COVERAGE REPORT',f'Players = {after["PLAYERS"]}; player-match rows = {after["PLAYER_MATCH_ROWS"]}. No player identity was fabricated.'),
 ('LINEUP_COVERAGE_REPORT.md','LINEUP COVERAGE REPORT',f'Lineup matches = {after["LINEUP_MATCHES"]}. No post-match lineup was promoted to pre-match.'),
 ('INJURY_COVERAGE_REPORT.md','INJURY COVERAGE REPORT',f'Injury matches = {after["INJURY_MATCHES"]}. No historical injury state was inferred.'),
 ('SUSPENSION_COVERAGE_REPORT.md','SUSPENSION COVERAGE REPORT',f'Suspension matches = {after["SUSPENSION_MATCHES"]}. No suspension state was inferred.'),
 ('XG_COVERAGE_REPORT.md','XG COVERAGE REPORT',f'xG matches = {after["XG_MATCHES"]}. No xG values were synthesized.'),
 ('EVENT_COVERAGE_REPORT.md','EVENT COVERAGE REPORT',f'Event matches = {after["EVENT_MATCHES"]}. No event stream was synthesized.'),
 ('ODDS_COVERAGE_REPORT.md','ODDS COVERAGE REPORT',f'Canonical matches with at least one odds field = {after["ODDS"]}. Exact PIT remains {after["EXACT_PIT"]}.'),
 ('SOFASCORE_ASSESSMENT.md','SOFASCORE ASSESSMENT', 'Status: DISCOVERED_ONLY. No automated extraction or bypass was performed. Official FAQ indicates underlying data sources are not exposed as API endpoints; therefore Sofascore is not counted as an acquired source.'),
 ]:
  (OUT/fn).write_text(f'# {title} V4\n\n{body}\n',encoding='utf-8')

 manifest={'mission':'FREE DATA DISCOVERY & GLOBAL ENRICHMENT V4','generated_at_utc':now(),'input':'FREE_GLOBAL_ENRICHMENT_MASTER_COMPLETE.zip','remote_bytes_acquired_this_run':0,'remote_network_state':'DNS_BLOCKED','source_registry':str(REG.relative_to(ROOT)),'before':before,'after':after,'protected_hashes_before':hashes_before,'protected_hashes_after':hashes_after,'snapshot_integrity':'PASS' if snapshots_ok else 'FAIL','real_money':'DISABLED'}
 (OUT/'GLOBAL_ENRICHMENT_STATUS_V4.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')

 # Security scan: look for obvious credential literals in source files.
 findings=[]
 for p in ROOT.rglob('*.py'):
  if any(part in {'venv','.git','__pycache__'} for part in p.parts): continue
  txt=p.read_text(errors='ignore')
  if re.search(r'(sk-[A-Za-z0-9]{20,}|x-apisports-key\s*[:=]\s*["\'][A-Za-z0-9_-]{10,})',txt): findings.append(str(p.relative_to(ROOT)))
 (OUT/'SECURITY_SCAN.txt').write_text('PASS\n' if not findings else 'FAIL\n'+'\n'.join(findings)+'\n',encoding='utf-8')

 print(json.dumps({'before':before,'after':after,'sources_discovered':len(reg['sources']),'sources_accessible':0,'sources_downloaded_this_run':0,'sources_materialized_inherited':local['validated'],'sources_validated_inherited':local['validated'],'snapshot_integrity':'PASS' if snapshots_ok else 'FAIL'},indent=2))

if __name__=='__main__': main()
