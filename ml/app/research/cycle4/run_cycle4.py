from __future__ import annotations
import csv, json, hashlib, subprocess, sys
from pathlib import Path
import pandas as pd
from .audit import source_audit, network_probe
from .pit import classify_pit

ROOT=Path(__file__).resolve().parents[4]
REPORT=ROOT/'reports/cycle4'; DATA=ROOT/'data/cycle4'
REPORT.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)

def sha256(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

def main():
 sources=source_audit(ROOT)
 probe=network_probe()
 odds_path=ROOT/'data/processed/odds_observations_real_nonpit.csv'
 d=pd.read_csv(odds_path) if odds_path.exists() else pd.DataFrame()
 exact=0; eligible=0; reasons={}
 if not d.empty:
  for _,r in d.iterrows():
   # Existing dataset explicitly lacks an exact odds timestamp; never infer one from date-level rows.
   x=classify_pit({'event_id':r.get('match_id'),'decision_time':r.get('odds_timestamp'),'entry_timestamp':r.get('odds_timestamp'),'entry_price':r.get('selection_home'),'source':r.get('source'),'source_record_id':r.get('match_id'),'availability_evidence':'DATE_ONLY'})
   reasons[x.reason]=reasons.get(x.reason,0)+1
   exact += x.pit_status=='EXACT_PIT'; eligible += x.scientific_status=='SCIENTIFICALLY_ELIGIBLE'
 status={'EXACT_PIT_COUNT':int(exact),'DECISION_ELIGIBLE_COUNT':int(eligible),'PAPER_BETS_COUNT':0,'SETTLEMENT_COUNT':0,'CLV_COUNT':0,'OOS_COUNT':0,'WALK_FORWARD_COUNT':0,'REAL_MONEY':'DISABLED','EDGE':'NOT_PROVEN'}
 (REPORT/'SOURCE_AUDIT.json').write_text(json.dumps({'sources':sources,'network_probe':probe},indent=2,ensure_ascii=False))
 (REPORT/'PIT_STATUS.json').write_text(json.dumps({'status':status,'local_nonpit_rows':int(len(d)),'classification_reasons':reasons},indent=2,ensure_ascii=False))
 (REPORT/'CYCLE4_EXECUTIVE_REPORT.md').write_text(f'''# ROBO DA BET V16+ — CICLO 4\n\n## Estado\n\n- EXACT_PIT: **{status["EXACT_PIT_COUNT"]}**\n- Scientifically eligible decisions: **{status["DECISION_ELIGIBLE_COUNT"]}**\n- Settlements: **0**\n- CLV: **0**\n- OOS PIT: **0**\n- Walk-forward PIT: **0**\n- REAL_MONEY: **DISABLED**\n- EDGE: **NOT_PROVEN**\n\n## Acquisition\n\nThe Odds API adapter exists locally, but no physical historical snapshot response is materialized. The runtime network probe is `{probe["status"]}`. Therefore the historical provider track is `BLOCKED_EXTERNAL` and no exact PIT rows are promoted.\n\nOfficial provider documentation states that historical odds are returned as snapshots at a requested timestamp, with the closest snapshot equal to or earlier than the requested time; the historical endpoint is paid. citeturn0search0turn0search1\n\n## Local data\n\nThe available `odds_observations_real_nonpit.csv` contains historical opening/closing/date-level odds, explicitly classified as NON_PIT. It is not promoted to exact PIT.\n\n## Scientific conclusion\n\nBecause there are zero exact-PIT prices, there are zero scientifically eligible paper bets, settlements and CLVs. Consequently this cycle cannot establish or reject betting edge. The correct verdict is **C — INCONCLUSIVE**, with `EDGE = NOT_PROVEN`.\n\n## What was validated locally\n\n- PIT gate: price must be present, valid, provenance-backed and timestamped at/before decision.\n- Future price rejection.\n- Date-level evidence rejection.\n- Decision snapshot required fields.\n- Deterministic settlement mechanics.\n- CLV temporal semantics.\n- The Odds API parser keeps provider snapshot timestamp distinct from nested bookmaker/market update timestamps.\n''')
 manifest={'cycle':'4','status':status,'source_audit_sha256':sha256(REPORT/'SOURCE_AUDIT.json'),'pit_status_sha256':sha256(REPORT/'PIT_STATUS.json'),'adapter':'ml/app/adapters/odds.py','network_probe':probe}
 (REPORT/'CYCLE4_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
 print(json.dumps({'status':status,'network':probe},indent=2))

if __name__=='__main__': main()
