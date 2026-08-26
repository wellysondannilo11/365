from __future__ import annotations
import argparse, csv, hashlib, json, os, socket, subprocess, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'reports/free_enrichment_v5'; OUT.mkdir(parents=True,exist_ok=True)
COV=ROOT/'data/coverage/free_enrichment_v5'; COV.mkdir(parents=True,exist_ok=True)
PROTECTED=[ROOT/'data/master_staff/PREMATCH_FEATURE_STORE.csv',ROOT/'data/real_day_prematch/REAL_DAY_PREMATCH_SNAPSHOT.json',ROOT/'data/real_day_prematch/REAL_DAY_FEATURES.csv']
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def snapshot_hashes(): return {str(p.relative_to(ROOT)):sha(p) for p in PROTECTED if p.exists()}
def state_counts():
 reg=json.loads((ROOT/'config/free_source_registry_v5.json').read_text())
 return {k:sum(1 for s in reg['sources'] if s.get('runtime')==k) for k in []}
def audit_counts():
 canonical=pd.read_csv(ROOT/'data/canonical/football_historical_real_canonical.csv')
 st=pd.read_csv(ROOT/'data/enrichment/free_data/MATCH_STATISTICS_FREE.csv')
 n=len(canonical)
 return {
 'MATCHES':int(canonical.match_id.nunique()),'TEAMS':len(set(canonical.home_team.dropna()).union(set(canonical.away_team.dropna()))),
 'PLAYERS':0,'PLAYER_MATCH':0,'LINEUPS':0,'INJURIES':0,'SUSPENSIONS':0,'EVENTS':0,'XG':0,
 'SHOTS':int(st[['home_shots','away_shots']].notna().all(axis=1).sum()),'SOT':int(st[['home_sot','away_sot']].notna().all(axis=1).sum()),
 'ODDS':int(canonical[['odds_1','odds_x','odds_2']].notna().any(axis=1).sum()),
 'EXACT_PIT':int(canonical.pit_status.astype(str).str.upper().eq('EXACT_PIT').sum()),
 'DATE_LEVEL_PIT':int(canonical.pit_status.astype(str).str.upper().isin(['DATE_LEVEL','PIT_DATE_ONLY']).sum()),
 'WOMEN_MATCHES':0}
def main():
 before=audit_counts(); hashes_before=snapshot_hashes();
 # Network is intentionally probed, never bypassed.
 hosts=['raw.githubusercontent.com','www.football-data.co.uk','v3.football.api-sports.io','api.open-meteo.com','api.sportmonks.com','api.the-odds-api.com']
 probe={}
 for h in hosts:
  try: socket.gethostbyname(h); probe[h]='DNS_OK'
  except Exception as e: probe[h]=f'BLOCKED:{type(e).__name__}:{e}'
 (OUT/'NETWORK_PROBE.json').write_text(json.dumps({'generated_at_utc':now(),'probe':probe,'remote_bytes_acquired':0},indent=2),encoding='utf8')
 after=audit_counts(); hashes_after=snapshot_hashes();
 rows=[]
 for k in ['MATCHES','SHOTS','SOT','XG','EVENTS','PLAYERS','PLAYER_MATCH','LINEUPS','INJURIES','SUSPENSIONS','ODDS','EXACT_PIT']:
  b=before[k]; a=after[k]; rows.append([k,b,0,a,round((a/after['MATCHES']*100) if after['MATCHES'] else 0,3)])
 with (COV/'V5_LAYER_COVERAGE.csv').open('w',newline='',encoding='utf8') as f:
  w=csv.writer(f); w.writerow(['layer','before','new','after','coverage_pct']); w.writerows(rows)
 status='PASS' if hashes_before==hashes_after else 'FAIL'
 summary={'mission':'GLOBAL FREE DATA MAXIMUM ENRICHMENT V5','generated_at_utc':now(),'remote_bytes_acquired':0,'before':before,'after':after,'snapshot_integrity':status,'network_probe':probe,'real_money':'DISABLED'}
 (OUT/'GLOBAL_ENRICHMENT_STATUS_V5.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
 return summary
if __name__=='__main__': print(json.dumps(main(),indent=2))
