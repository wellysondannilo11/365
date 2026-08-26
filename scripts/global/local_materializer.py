"""Validate/materialize acquired tabular football artifacts without fabricating fields."""
from __future__ import annotations
import csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MAN=ROOT/'data/global_dataset/registry/DATA_ACQUISITION_MANIFEST.json'
OUT=ROOT/'data/global_dataset/processed_acquisition'; OUT.mkdir(parents=True,exist_ok=True)
REQUIRED_ANY=[{'Date','HomeTeam','AwayTeam','FTHG','FTAG'},{'date','home_team','away_team','home_score','away_score'}]

def sha256(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
 return h.hexdigest()

def validate_csv(path):
 with path.open('r',encoding='utf-8-sig',newline='',errors='replace') as f:
  r=csv.DictReader(f); fields=set(r.fieldnames or []); rows=0; valid=0
  for row in r:
   rows+=1
   if any(req.issubset(fields) for req in REQUIRED_ANY): valid+=1
 return {'rows':rows,'columns':sorted(fields),'schema_valid':valid>0,'valid_rows':valid}

def main():
 man=json.loads(MAN.read_text(encoding='utf-8')) if MAN.exists() else {'execution_log':[]}
 results=[]
 for rec in man.get('execution_log',[]):
  p=rec.get('raw_path')
  if not p or rec.get('state')!='CHECKSUM_VALIDATED': continue
  path=ROOT/p
  if not path.exists() or path.suffix.lower()!='.csv': continue
  check=validate_csv(path)
  rec['materialization_validation']=check
  if check['schema_valid']:
   rec['state_history'].append('MATERIALIZED'); rec['materialized']=True
   rec['state_history'].append('VALIDATED'); rec['validated']=True; rec['state']='VALIDATED'
   rec['processing_timestamp']=datetime.now(timezone.utc).isoformat()
   # Store only a byte-identical copy in the acquisition processed area. No fields are invented.
   dest=OUT/path.name; dest.write_bytes(path.read_bytes()); rec['processed_path']=str(dest)
   rec['state_history'].append('NORMALIZED'); rec['state_history'].append('PROCESSED'); rec['processed']=True
   rec['normalization']='byte-preserving CSV staging; canonical schema promotion remains separate'
  else:
   rec['state_history'].append('FAILED'); rec['state']='FAILED'; rec['error']='unsupported/invalid football CSV schema'
  results.append(rec)
 MAN.write_text(json.dumps(man,indent=2,ensure_ascii=False),encoding='utf-8')
 print(json.dumps(results,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
