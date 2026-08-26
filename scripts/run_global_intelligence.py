from __future__ import annotations
import csv, hashlib, json, os, socket, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'; MAN=ROOT/'data/manifests'; MODEL=ROOT/'data/model'; OUT=ROOT/'reports/intelligence'
for p in (RAW,MAN,MODEL,OUT): p.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'ml'))
from app.intelligence.coverage import build_global_coverage
from app.intelligence_evidence import EvidenceClass

SOURCES=[
 ('Football-Data.co.uk','https://www.football-data.co.uk/mmz4281/2526/E0.csv','HISTORICAL_REAL_NON_PIT'),
 ('Football-Data.co.uk','https://www.football-data.co.uk/mmz4281/2526/E1.csv','HISTORICAL_REAL_NON_PIT'),
 ('Football-Data.co.uk','https://www.football-data.co.uk/mmz4281/2526/BRA.csv','HISTORICAL_REAL_NON_PIT'),
 ('Football-Data.co.uk','https://www.football-data.co.uk/mmz4281/2526/ARG.csv','HISTORICAL_REAL_NON_PIT'),
 ('Football-Data.co.uk','https://www.football-data.co.uk/mmz4281/2526/USA.csv','HISTORICAL_REAL_NON_PIT'),
 ('Football-Data.co.uk','https://www.football-data.co.uk/mmz4281/2526/JPN.csv','HISTORICAL_REAL_NON_PIT'),
 ('StatsBomb Open Data','https://raw.githubusercontent.com/statsbomb/open-data/master/data/competitions.json','HISTORICAL_REAL_STATS'),
 ('The Odds API','https://the-odds-api.com/historical-odds-data/','PIT_SOURCE'),
 ('Betfair Historical Data','https://historicdata.betfair.com/','PIT_SOURCE'),
 ('API-Football','https://www.api-football.com/','SOURCE_DISCOVERY'),
 ('Sportmonks','https://www.sportmonks.com/football-api/','SOURCE_DISCOVERY'),
]

def sha(b): return hashlib.sha256(b).hexdigest()
def fetch(source,url,classification):
    captured=datetime.now(timezone.utc).isoformat()
    try:
        req=Request(url,headers={'User-Agent':'RoboDaBet/GlobalFootballResearch/1.0'})
        with urlopen(req,timeout=8) as r: b=r.read(); status=getattr(r,'status',200)
        if not b: raise ValueError('EMPTY_RESPONSE')
        return {'source':source,'url':url,'classification':classification,'status':'ACQUIRED','http_status':status,'captured_at':captured,'bytes':len(b),'sha256':sha(b),'reason':'MATERIALIZED'} , b
    except HTTPError as e:
        return {'source':source,'url':url,'classification':classification,'status':'FAILED','http_status':e.code,'captured_at':captured,'bytes':0,'sha256':None,'reason':f'HTTP_{e.code}'},None
    except Exception as e:
        return {'source':source,'url':url,'classification':classification,'status':'FAILED','http_status':None,'captured_at':captured,'bytes':0,'sha256':None,'reason':f'{type(e).__name__}:{e}'},None

rows=[]
for source,url,cls in SOURCES:
    meta,b=fetch(source,url,cls); rows.append(meta)
    if b and url.endswith('.csv'):
        name=url.rsplit('/',1)[-1]; (RAW/name).write_bytes(b)

with (MAN/'GLOBAL_INTELLIGENCE_ACQUISITION.json').open('w',encoding='utf-8') as f: json.dump(rows,f,indent=2,ensure_ascii=False)
with (MAN/'GLOBAL_INTELLIGENCE_ACQUISITION.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

coverage=build_global_coverage(MODEL/'global_football_coverage_matrix.csv')
acquired=[r for r in rows if r['status']=='ACQUIRED']
empirical=[r for r in acquired if r['classification'] in {'HISTORICAL_REAL','HISTORICAL_REAL_NON_PIT','LIVE_REAL'}]
manifest={'run_timestamp':datetime.now(timezone.utc).isoformat(),'found':len(SOURCES),'acquired':len(acquired),'materialized':len(acquired),'processed_new':0,'pit_validated_new':0,'used_in_model_new':0,'empirical_bytes':len(empirical),'real_money':'DISABLED','rule':'Discovery does not equal evidence; only materialized real bytes can become empirical evidence.'}
(OUT/'GLOBAL_INTELLIGENCE_EXECUTION_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')

status='PARTIAL' if acquired else 'DATA_ACQUISITION_BLOCKED'
report=f'''# GLOBAL INTELLIGENCE ENGINE — EXECUTION REPORT\n\nTimestamp: {manifest['run_timestamp']}\n\n## Evidence boundary\nOnly materialized real bytes are eligible for empirical evidence. DEMO/MOCK/SYNTHETIC are never counted.\n\n## Acquisition\n- FOUND: {len(SOURCES)}\n- ACQUIRED: {len(acquired)}\n- MATERIALIZED: {len(acquired)}\n- PROCESSED_NEW: 0\n- PIT_VALIDATED_NEW: 0\n- USED_IN_MODEL_NEW: 0\n- STATUS: {status}\n\n## Existing package evidence\nThe supplied package already contains 40 historical-real rows according to its scientific status. This run does not relabel them or manufacture additional rows.\n\n## Runtime\nExternal acquisition is attempted at execution time and every failure is recorded with its actual exception/HTTP status.\n\n## Real money\nDISABLED.\n'''
(OUT/'GLOBAL_INTELLIGENCE_EXECUTION_REPORT.md').write_text(report,encoding='utf-8')
print(json.dumps(manifest,indent=2))
