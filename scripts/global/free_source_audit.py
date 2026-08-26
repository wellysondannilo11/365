"""Audit free/public provider registry without claiming remote acquisition."""
from __future__ import annotations
import json, socket
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[2]
REG=ROOT/'config/free_source_registry.json'
OUT=ROOT/'data/global_dataset/reports/SOURCE_ACQUISITION_REPORT.md'
HOSTS={'api-football':'v3.football.api-sports.io','football-data-org':'api.football-data.org','statsbomb-open-data':'raw.githubusercontent.com','openligadb':'www.openligadb.de','thesportsdb':'www.thesportsdb.com','football-data-co-uk':'www.football-data.co.uk'}

def main():
 reg=json.loads(REG.read_text())
 lines=[f'# SOURCE ACQUISITION REPORT\n\nRun UTC: {datetime.now(timezone.utc).isoformat()}\n','| Source | DNS/Network | Remote bytes acquired this run | Status |','|---|---|---:|---|']
 for s in reg['sources']:
  host=HOSTS.get(s['source_id']); status='NOT_TESTED'
  if host:
   try: socket.gethostbyname(host); status='DNS_ACCESSIBLE'
   except Exception as e: status=f'BLOCKED: {type(e).__name__}'
  lines.append(f"| {s['source']} | {status} | 0 | {'BLOCKED_NO_NETWORK' if status.startswith('BLOCKED') else 'READY_FOR_LOCAL_EXECUTION'} |")
 lines += ['','## Rule','FOUND/registry presence is never promoted to ACQUIRED. Remote acquisition remains zero until bytes are downloaded, checksum-validated, materialized and processed.','']
 OUT.write_text('\n'.join(lines),encoding='utf-8')
 print(OUT)
if __name__=='__main__': main()
