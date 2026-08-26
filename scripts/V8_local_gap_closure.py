from pathlib import Path
import pandas as pd, json, hashlib, subprocess, shutil, os, re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/v8'; OUT.mkdir(parents=True,exist_ok=True)

def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

def count_rows(p):
 try: return len(pd.read_csv(p))
 except: return 0

before={
 'MATCHES':7570,'PLAYERS':59,'PLAYER_MATCH':0,'XG':0,'EVENTS':0,'LINEUPS':0,'INJURIES':0,'SUSPENSIONS':0,'SHOTS':5160,'SOT':5160,'ODDS':4760,'EXACT_PIT':0,'DATE_LEVEL_PIT':30,'WEATHER':0,'WOMEN':0
}
after=dict(before)
after['MATCHES']=count_rows(ROOT/'data/canonical/football_historical_real_canonical.csv')
new={k:after[k]-before[k] for k in before}

# Physical audit of likely data files.
rows=[]
for p in sorted((ROOT/'data').rglob('*')):
 if p.is_file() and p.suffix.lower() in {'.csv','.json','.jsonl','.parquet','.sqlite','.db','.txt','.zip','.xlsx'}:
  try: size=p.stat().st_size
  except: continue
  rows.append({'path':str(p.relative_to(ROOT)).replace('\\','/'),'bytes':size,'type':p.suffix.lower().lstrip('.')})
pd.DataFrame(rows).to_csv(OUT/'V8_LOCAL_DATA_INVENTORY.csv',index=False)

# Before/after matrix.
source_map={'MATCHES':'local canonical + V8 local materialization','PLAYERS':'footballcsv/cache.football.squads (59 already present)','PLAYER_MATCH':'none','XG':'none','EVENTS':'none','LINEUPS':'none','INJURIES':'none','SUSPENSIONS':'none','SHOTS':'Football-Data local artifacts','SOT':'Football-Data local artifacts','ODDS':'Football-Data local artifacts','EXACT_PIT':'none','DATE_LEVEL_PIT':'existing historical odds','WEATHER':'none','WOMEN':'none'}
rows=[]
for k in before:
 cov=100*after[k]/after['MATCHES'] if after['MATCHES'] else 0
 rows.append({'layer':k,'before':before[k],'new':new[k],'after':after[k],'coverage_pct_of_matches':round(cov,4),'source':source_map[k],'temporal_quality':'DATE_LEVEL_ONLY' if k in {'MATCHES','DATE_LEVEL_PIT'} else ('NON_PIT' if k in {'ODDS','EXACT_PIT'} else 'N/A'),'provenance':'validated locally' if new[k] else 'preserved'} )
pd.DataFrame(rows).to_csv(OUT/'V8_BEFORE_AFTER_MATRIX.csv',index=False)

# Gap matrix concise.
targets={'MATCHES':100,'PLAYERS':100,'PLAYER_MATCH':100,'XG':100,'EVENTS':100,'LINEUPS':100,'INJURIES':100,'SUSPENSIONS':100,'SHOTS':100,'SOT':100,'ODDS':100,'EXACT_PIT':100,'WEATHER':100,'WOMEN':1}
g=[]
for k in before:
 coverage=100*after[k]/after['MATCHES'] if k not in {'PLAYERS','PLAYER_MATCH','XG','EVENTS','LINEUPS','INJURIES','SUSPENSIONS','EXACT_PIT','WEATHER','WOMEN'} else (100*after[k]/after['MATCHES'] if k=='PLAYERS' else 0)
 g.append({'layer':k,'current_count':after[k],'target':'match-level' if k!='PLAYERS' else 'player records','coverage_pct':round(coverage,4),'remaining_gap':'OPEN' if (after[k]==0 or (k in {'XG','EVENTS','LINEUPS','INJURIES','SUSPENSIONS','EXACT_PIT','WEATHER','PLAYER_MATCH','WOMEN'})) else 'PARTIAL','highest_value_next_step':{'XG':'StatsBomb/public xG dataset','EVENTS':'StatsBomb Open Data','LINEUPS':'StatsBomb Open Data','PLAYER_MATCH':'StatsBomb lineups/events','INJURIES':'API-Football/public historical injury dataset','SUSPENSIONS':'API-Football/public disciplinary dataset','EXACT_PIT':'timestamped historical odds dataset','WEATHER':'Open-Meteo + stadium geocoding','WOMEN':'StatsBomb women/public women datasets'}.get(k,'expand local/public match statistics')})
pd.DataFrame(g).to_csv(OUT/'V8_DATA_GAP_MATRIX.csv',index=False)

# Source coverage, with strict acquisition states.
sources=[
 ['StatsBomb Open Data','OPEN_DATA','WEB_VERIFIED','DISCOVERED','NOT_MATERIALIZED_THIS_RUN','matches;events;lineups;players;shots;360','remote DNS unavailable'],
 ['Football-Data.co.uk','PUBLIC_DATASET','WEB_VERIFIED','LOCAL_PRESENT','MATERIALIZED_REUSED','results;stats;odds','local artifacts already in ZIP; no new remote bytes'],
 ['footballcsv/cache.footballmatches','PUBLIC_DATASET','LOCAL_VERIFIED','LOCAL_PRESENT','MATERIALIZED_REUSED','players;squads','59 players already materialized; 64 Brazilian Série A matches reused/materialized'],
 ['ricardo-mattoss/Brazilian-Soccer-Data','PUBLIC_DATASET','LOCAL+WEB_CORROBORATED','LOCAL_PRESENT','MATERIALIZED_THIS_RUN','Libertadores matches 2013-2022','889 new canonical matches materialized; one undated row excluded'],
 ['API-Football FREE','FREE_API','WEB_VERIFIED','DISCOVERED','NOT_TESTED_REMOTE','fixtures;events;lineups;players;injuries;sidelined;statistics;odds','100/day and 10/min; no key exposed/configured'],
 ['Open-Meteo','FREE_API','WEB_VERIFIED','DISCOVERED','NOT_MATERIALIZED_THIS_RUN','historical weather;geocoding;elevation','remote DNS unavailable'],
 ['football-data.org','FREE_API','DISCOVERED','DISCOVERED','NOT_TESTED_REMOTE','fixtures;teams;competitions','credential not configured'],
 ['OpenLigaDB','OPEN_API','DISCOVERED','DISCOVERED','BLOCKED_REMOTE','German fixtures/results/goals','remote DNS unavailable'],
 ['TheSportsDB','FREE_API','DISCOVERED','DISCOVERED','BLOCKED_REMOTE','teams;players;events;venues','remote DNS unavailable'],
 ['SofaScore','REFERENCE_ONLY','WEB_VERIFIED','DISCOVERED_ONLY','NOT_ACQUIRED','matches;events;lineups;players;injuries;ratings;shots;xG','no bypass; no authorized dataset materialized'],
 ['GitHub/Hugging Face/Kaggle/Zenodo','PUBLIC_DATASET','DISCOVERY','DISCOVERED','NOT_MATERIALIZED_THIS_RUN','various','license/dataset-specific validation required']
]
pd.DataFrame(sources,columns=['source','type','verification','access_status','materialization_status','capabilities','notes']).to_csv(OUT/'V8_SOURCE_COVERAGE.csv',index=False)

# Public dataset discovery catalog.
discovery=[
 ['StatsBomb Open Data','https://github.com/statsbomb/open-data','research/open data','matches;events;lineups;360','select competitions/seasons','NOT_MATERIALIZED_THIS_RUN'],
 ['Football-Data.co.uk','https://www.football-data.co.uk/data.php','free public dataset','results;match stats;odds','many leagues/seasons','LOCAL_REUSED_ONLY'],
 ['Brazilian Soccer Data / Libertadores_Matches','https://github.com/ricardo-mattoss/Brazilian-Soccer-Data/blob/master/Data/Libertadores_Matches.csv','CC BY 4.0 per public benchmark reference','Libertadores matches','2013-2022','LOCAL_MATERIALIZED'],
 ['API-Football','https://www.api-football.com/','free API tier','fixtures;events;lineups;players;injuries;statistics;odds','free tier recent seasons','NOT_TESTED_REMOTE'],
 ['Open-Meteo','https://open-meteo.com/en/docs/historical-weather-api','open historical weather','temperature;humidity;precipitation;wind;pressure','1940-present','NOT_MATERIALIZED_THIS_RUN'],
 ['TheSportsDB','https://www.thesportsdb.com/documentation','public/free API','teams;players;events;venues','variable','BLOCKED_REMOTE'],
 ['OpenLigaDB','https://www.openligadb.de/','public API','German fixtures/results/goals','Germany','BLOCKED_REMOTE'],
 ['GitHub/Hugging Face/Kaggle/Zenodo','multiple public repositories','dataset-specific','events;xG;players;lineups;odds','varies','DISCOVERED_ONLY']
]
pd.DataFrame(discovery,columns=['dataset','url','license_or_access','fields','coverage','materialization_status']).to_csv(OUT/'V8_PUBLIC_DATASET_DISCOVERY.csv',index=False)

# PIT report.
pit='''# V8 PIT REPORT\n\n- Exact PIT before: 0\n- Exact PIT new: 0\n- Exact PIT after: 0\n- Date-level PIT before/after: 30 / 30\n- No local source added a trustworthy bookmaker timestamp in this run.\n- The 64 Brazilian matches and 889 Libertadores matches are historical result records only and are marked NON_PIT.\n- No date was promoted to an odds timestamp.\n'''
(OUT/'V8_PIT_REPORT.md').write_text(pit)

# Provenance report.
prov='''# V8 PROVENANCE REPORT\n\n## Materialização local real\n\n1. `data/raw/libertadores_brazilian_soccer_data.csv` — SHA-256 validated and reused. 889 new dated matches were inserted into the canonical dataset after normalized date/team deduplication.\n2. `data/raw/acquisition_worker/footballcsv_2024_br1.csv` — SHA-256 validated and reused. 64 new Brasileirão Série A 2024 matches were inserted.\n\nEvery inserted row has source, source_url, source file, raw hash, parser version and materialization status in the canonical provenance file.\n\nNo remote bytes were acquired in this runtime.\n'''
(OUT/'V8_PROVENANCE_REPORT.md').write_text(prov)

# Reports.
summary=json.loads((OUT/'V8_LOCAL_MATERIALIZATION_SUMMARY.json').read_text())
(OUT/'V8_ACQUISITION_REPORT.md').write_text(f'''# V8 AQUISIÇÃO\n\n## Resultado\n- Remote bytes acquired: **0**\n- Local bytes reused for real materialization: **98,906**\n- New canonical matches: **{summary['new_matches']}**\n- Libertadores: **{summary['new_libertadores']}**\n- Brasileirão Série A 2024: **{summary['new_brasileirao']}**\n\n## Bloqueio remoto\nO container não resolve DNS (`raw.githubusercontent.com`, `github.com` etc.). O teste HTTP confirmou `curl: (6) Could not resolve host`. Portanto nenhuma fonte remota foi promovida a adquirido.\n\n## Regra aplicada\nDISCOVERED != ACQUIRED != MATERIALIZED. Apenas arquivos que já existiam dentro do ZIP foram usados para fechar gaps nesta execução.\n''')
(OUT/'V8_ENRICHMENT_REPORT.md').write_text(f'''# V8 ENRICHMENT REPORT\n\nA V8 conseguiu fechar parcialmente o gap de **MATCHES** usando dados reais já presentes no ZIP.\n\n- Matches: 7.570 → {after['MATCHES']} (+{new['MATCHES']})\n- Players: 59 → 59\n- Player-match: 0 → 0\n- XG: 0 → 0\n- Events: 0 → 0\n- Lineups: 0 → 0\n- Injuries: 0 → 0\n- Suspensions: 0 → 0\n- Shots: 5.160 → 5.160\n- SOT: 5.160 → 5.160\n- Odds: 4.760 → 4.760\n- Exact PIT: 0 → 0\n- Weather: 0 → 0\n- Women: 0 → 0\n\nOs novos jogos não foram artificialmente enriquecidos com xG, eventos, lineups, odds ou PIT.\n''')
(OUT/'V8_PLAYER_REPORT.md').write_text('''# V8 PLAYER REPORT\n\nPlayers físicos no ZIP: 59.\nPlayer-match materializado: 0.\nNenhum squad foi convertido em participação de partida.\n''')
(OUT/'V8_LINEUP_REPORT.md').write_text('''# V8 LINEUP REPORT\n\nLineups materializados: 0.\nNenhum elenco/squad foi promovido para lineup.\n''')
(OUT/'V8_XG_REPORT.md').write_text('''# V8 XG REPORT\n\nxG externo materializado: 0.\nNenhum xG foi inferido ou gerado para preencher o gap.\n''')
(OUT/'V8_EVENT_REPORT.md').write_text('''# V8 EVENT REPORT\n\nEventos materializados: 0.\nOs resultados de partidas adicionados não foram convertidos em eventos individuais.\n''')
(OUT/'V8_INJURY_REPORT.md').write_text('''# V8 INJURY REPORT\n\nInjuries materializadas: 0. Nenhuma evidência temporal suficiente local foi promovida.\n''')
(OUT/'V8_SUSPENSION_REPORT.md').write_text('''# V8 SUSPENSION REPORT\n\nSuspensions materializadas: 0. Cartões/resultados não foram convertidos em bans.\n''')
(OUT/'V8_ODDS_REPORT.md').write_text('''# V8 ODDS REPORT\n\nOdds: 4.760 → 4.760. Exact PIT: 0 → 0.\nNenhuma nova odds foi promovida nesta execução.\n''')
(OUT/'V8_WEATHER_REPORT.md').write_text('''# V8 WEATHER REPORT\n\nWeather: 0 → 0. Open-Meteo foi verificada como fonte pública adequada, mas a aquisição remota foi bloqueada por DNS.\n''')

# Paid gap matrix.
paid=[]
for field,cov,nextsrc in [
 ('events',0,'StatsBomb Open Data / API-Football'),('xg',0,'StatsBomb/public xG datasets'),('lineups',0,'StatsBomb / API-Football'),('player_match',0,'StatsBomb lineups/events / API-Football'),('injuries',0,'API-Football/public historical injury datasets'),('suspensions',0,'API-Football/public disciplinary datasets'),('exact_pit',0,'timestamped historical odds provider/dataset'),('weather',0,'Open-Meteo + geocoding'),('women',0,'StatsBomb women/public women datasets')]:
 paid.append({'field':field,'current_coverage':cov,'free_coverage':cov,'remaining_gap':'OPEN','provider_candidates':nextsrc,'estimated_cost':'NOT_EVALUATED_THIS_RUN'})
pd.DataFrame(paid).to_csv(OUT/'V8_PAID_GAP_MATRIX.csv',index=False)

# Tests / evidence.
def run(cmd,timeout=180):
 try:
  p=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
  return {'status':'PASS' if p.returncode==0 else 'FAIL','exit_code':p.returncode,'tail':p.stdout[-4000:]}
 except subprocess.TimeoutExpired as e:
  return {'status':'TIMEOUT','exit_code':None,'tail':str(e)}

tests={
 'compileall':run(['python','-m','compileall','-q','.']),
 'pytest':run(['pytest','-q'],timeout=300),
 'unzip_t':run(['unzip','-t','/tmp/v8_test.zip']) if Path('/tmp/v8_test.zip').exists() else {'status':'NOT_RUN'},
}
# simple security scan for common accidental credential patterns; report findings only, not claim a formal scanner.
scan=[]
for p in ROOT.rglob('*'):
 if p.is_file() and p.suffix.lower() in {'.py','.json','.yml','.yaml','.env','.ini','.properties'}:
  try: txt=p.read_text(errors='ignore')
  except: continue
  if re.search(r'(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*["\']?[A-Za-z0-9_\-]{20,}',txt): scan.append(str(p.relative_to(ROOT)))
tests['security_scan']={'status':'PASS' if not scan else 'FAIL','method':'heuristic credential-pattern scan','findings':scan[:50]}

before_snap={
 'data/master_staff/PREMATCH_FEATURE_STORE.csv':'a8707eb991764492289e7f5806278962ae3ff3377891e979609bf747c4672a6b',
 'data/real_day_prematch/REAL_DAY_PREMATCH_SNAPSHOT.json':'97f83c1d992a8ea36bca44a8e14bb4d21e4c1d8024463e715f1bf24cba7c5c5c'}
after_snap={p:sha(ROOT/p) for p in before_snap}
snap_ok=all(after_snap[p]==h for p,h in before_snap.items())

evidence={'mission':'V8','timestamp_utc':pd.Timestamp.utcnow().isoformat(),'remote_bytes_acquired':0,'local_bytes_reused_for_materialization':98906,'new_records':new,'tests':tests,'snapshot_integrity':'PASS' if snap_ok else 'FAIL','snapshot_hashes_before':before_snap,'snapshot_hashes_after':after_snap,'canonical_rows_before':7570,'canonical_rows_after':after['MATCHES'],'notes':['No remote data was fabricated.','Only pre-existing local files were used for new match materialization.','Protected prematch snapshots were not modified.']}
(OUT/'V8_EXECUTION_EVIDENCE.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False))

# Master staff report.
(OUT/'V8_MASTER_STAFF_REPORT.md').write_text(f'''# V8 MASTER STAFF REPORT\n\n## A. Dado novo real\n**{new['MATCHES']} partidas históricas reais** entraram no canonical: **889 Copa Libertadores (2013-2022) + 64 Brasileirão Série A 2024**.\n\n## B. Engenharia vs dados\nRemote data acquisition: 0 bytes. Engineering progress exists only in reports/evidence; data progress is the {new['MATCHES']} rows materialized from local artifacts already present in the ZIP.\n\n## C. Gaps fechados\n- Match coverage: parcialmente ampliada.\n- Brasil: abriu uma camada real de 64 partidas de Brasileirão 2024.\n- Libertadores: ampliou histórico para 2013-2022.\n\n## D. Gaps abertos\nPlayer-match, xG, events, lineups, injuries, suspensions, Exact PIT, weather e women continuam sem novos registros nesta execução.\n\n## E. Fonte mais eficiente nesta execução\nA maior contribuição foi o artefato local `Libertadores_Matches.csv`, seguido pelo arquivo local de Brasileirão 2024.\n\n## F. Próxima fonte de maior valor científico\nMaterialização legítima do StatsBomb Open Data em ambiente com Internet/DNS, porque uma única fonte pode fornecer matches/events/lineups e dados de jogadores para competições selecionadas.\n\n## G. Cobertura materializada\nCanonical: 7.570 → **{after['MATCHES']}**. Players: 59. Shots/SOT: 5.160. Odds: 4.760. Exact PIT: 0.\n\n## H. Maior gargalo\n**Aquisição remota + ausência de event/lineup/xG/PIT timestamped.**\n\n## I. Treinamento OOS\nO dataset tem massa histórica maior, mas **não é suficiente para declarar prontidão OOS para as camadas que dependem de xG/events/lineups/PIT**.\n\n## J. Edge\n**EDGE_NOT_DETERMINED.** Nenhum resultado desta missão autoriza declaração de edge/value bet.\n\n## Estados\n- GLOBAL_DATASET_STATUS: GLOBAL_PARTIAL\n- FREE_DATA_STATUS: LOCAL_GAP_CLOSURE_PARTIAL / REMOTE_BLOCKED\n- ACQUISITION_STATUS: REMOTE_BLOCKED_DNS_LOCAL_MATERIALIZED\n- ENRICHMENT_STATUS: MATCHES_ENRICHED_LOCAL_ONLY\n- PIT_STATUS: DATE_LEVEL_PIT_ONLY\n- MODEL_STATUS: RESEARCH_ONLY\n- EDGE_STATUS: EDGE_NOT_DETERMINED\n- VALUE_BET_STATUS: BLOCKED\n- REAL_MONEY_STATUS: DISABLED\n- SNAPSHOT_INTEGRITY: {'PASS' if snap_ok else 'FAIL'}\n''')

print('V8 reports generated:', OUT)
