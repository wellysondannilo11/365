from __future__ import annotations
import hashlib,json,socket,subprocess,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
REG=json.loads((ROOT/'config/free_source_registry_v3.json').read_text())
HOSTS={'statsbomb-open-data':'raw.githubusercontent.com','football-data-co-uk':'www.football-data.co.uk','api-football':'v3.football.api-sports.io','football-data-org':'api.football-data.org','openligadb':'www.openligadb.de','thesportsdb':'www.thesportsdb.com','the-odds-api':'api.the-odds-api.com'}

def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b): h.update(b)
 return h.hexdigest()

def main():
 out=ROOT/'data/global_dataset/reports/v3'; out.mkdir(parents=True,exist_ok=True)
 rows=[]
 for s in REG['sources']:
  host=HOSTS.get(s['source_id']); dns='NOT_TESTED'
  try: socket.gethostbyname(host); dns='ACCESSIBLE'
  except Exception as e: dns=f'BLOCKED:{type(e).__name__}:{e}'
  rows.append({**s,'dns_status':dns,'downloaded':0,'materialized':0,'validated':0,'processed':0,'used_in_model':0,'acquisition_status':'BLOCKED_NO_NETWORK' if dns.startswith('BLOCKED') else 'READY_FOR_EXTERNAL_EXECUTION'})
 report={'run_utc':datetime.now(timezone.utc).isoformat(),'network_blocked':all(r['dns_status'].startswith('BLOCKED') for r in rows),'sources':rows,'real_money':'DISABLED'}
 (out/'GLOBAL_FREE_SOURCE_DISCOVERY_V3.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
 (out/'GLOBAL_FREE_SOURCE_DISCOVERY_V3.md').write_text('# FREE GLOBAL SOURCE DISCOVERY V3\n\nRemote acquisition is only counted after actual bytes are downloaded, checksummed, normalized and validated.\n\n|Source|Grade|DNS|Acquisition|Capabilities|\n|---|---|---|---|---|\n'+'\n'.join(f"|{r['name']}|{r['grade']}|{r['dns_status']}|{r['acquisition_status']}|{', '.join(r['capabilities'])}|" for r in rows),encoding='utf-8')
 print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
