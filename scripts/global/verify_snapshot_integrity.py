from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
TARGETS=[ROOT/'data/master_staff/PREMATCH_FEATURE_STORE.csv',ROOT/'data/real_day_prematch/REAL_DAY_PREMATCH_SNAPSHOT.json',ROOT/'data/real_day_prematch/REAL_DAY_FEATURES.csv']
OUT=ROOT/'data/global_dataset/reports/FREE_ENRICHMENT_SNAPSHOT_INTEGRITY.json'
def h(p):
 x=hashlib.sha256(); x.update(p.read_bytes()); return x.hexdigest()
def main():
 before={str(p.relative_to(ROOT)):h(p) for p in TARGETS}; out=json.loads(OUT.read_text()) if OUT.exists() else {}
 expected=out.get('before_hashes',before)
 after={str(p.relative_to(ROOT)):h(p) for p in TARGETS}; changed=[k for k in after if after[k]!=expected.get(k)]
 result={'before_hashes':expected,'after_hashes':after,'changed_files':changed,'unchanged':not changed,'status':'PASS' if not changed else 'MISSION_FAILED_INTEGRITY'}
 OUT.write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2)); return 0 if not changed else 2
if __name__=='__main__': raise SystemExit(main())
