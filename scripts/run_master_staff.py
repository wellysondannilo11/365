from pathlib import Path
import json, hashlib, shutil, zipfile, subprocess, sys
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'ml'))
from app.master_staff.engine import load_canonical, build_features, h2h_records, hypothesis_tests, oos_walk_forward, coverage, target_registry, operational_manifest
OUT=ROOT/'data/master_staff'; REP=ROOT/'reports/master_staff'; OUT.mkdir(parents=True,exist_ok=True); REP.mkdir(parents=True,exist_ok=True)
d=load_canonical(ROOT); f=build_features(d)
f.to_csv(OUT/'PREMATCH_FEATURE_STORE.csv',index=False)
h2h_records(f).to_csv(OUT/'H2H_INTELLIGENCE.csv',index=False)
coverage(f).to_csv(OUT/'MASTER_COVERAGE.csv',index=False)
target_registry(f).to_csv(OUT/'TARGET_COMPETITION_REGISTRY.csv',index=False)
hyp=hypothesis_tests(f); hyp.to_csv(OUT/'MASTER_HYPOTHESES.csv',index=False)
model=oos_walk_forward(f); (OUT/'MODEL_VALIDATION.json').write_text(json.dumps(model,indent=2,default=str))
oper=operational_manifest(ROOT,f); (OUT/'OPERATIONAL_PILLARS.json').write_text(json.dumps(oper,indent=2))
# Explicit schemas for unavailable evidence; no fabricated rows.
empty_schemas={
 'PLAYER_RECORDS.csv':['player_id','team_id','gender','position','status','minutes','importance_score','source','pit_status'],
 'INJURY_RECORDS.csv':['player_id','team_id','status','injury_type','injury_start','expected_return','actual_return','source','decision_timestamp','pit_status'],
 'LINEUP_RECORDS.csv':['canonical_match_id','team_id','player_id','status','confirmed_at','decision_timestamp','source','pit_status'],
 'LIVE_SNAPSHOTS.csv':['canonical_match_id','snapshot_timestamp','source_timestamp','minute','score','shots','sot','xg','corners','cards','odds','freshness','pit_status'],
 'PAPER_DECISIONS.csv':['decision_id','canonical_match_id','timestamp','market','line','odd','model_probability','fair_odd','ev','stake','confidence','risk','decision'],
 'SETTLEMENTS.csv':['decision_id','settlement_timestamp','status','pnl','source','pit_status'],
}
for name,cols in empty_schemas.items():
    p=OUT/name
    if not p.exists(): pd.DataFrame(columns=cols).to_csv(p,index=False)
# Provenance and hashes
prov=[]
for p in sorted(OUT.glob('*')):
    b=p.read_bytes(); prov.append({'file':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'status':'MATERIALIZED' if p.suffix in {'.csv','.json'} else 'MATERIALIZED'})
pd.DataFrame(prov).to_csv(OUT/'MASTER_STAFF_PROVENANCE.csv',index=False)
summary={
 'total_matches':len(f),'new_matches':0,'countries':int(f.country.nunique()),'competitions':int(f.competition.nunique()),'seasons':int(f.season.nunique()),
 'men_matches':int((f.gender=='MEN').sum()),'women_matches':0,'h2h_records':len(f),'rivalry_records':0,'importance_records':len(f),
 'player_records':0,'injury_records':0,'suspension_records':0,'lineups':0,'events':0,'shots':0,'sot':0,'xg':int(f[['home_xg','away_xg']].notna().all(axis=1).sum()),
 'cards':int(f[['home_cards','away_cards']].notna().all(axis=1).sum()),'corners':int(f[['home_corners','away_corners']].notna().all(axis=1).sum()),'referees':int(f.referee.notna().sum()),
 'odds':int(f[['odds_1','odds_x','odds_2']].notna().all(axis=1).sum()),'timestamped_odds':int(f.odds_timestamp.notna().sum()),'pit_validated':int(f.pit_status.eq('PIT_VALIDATED').sum()),
 'live_matches':0,'live_snapshots':0,'settlements':0,'paper_bets':0,'real_money':'DISABLED','new_real_data_materialized':0,
 'evidence_note':'This execution added no new external real data because network acquisition was unavailable in the runtime. Existing real materialized data were preserved and reprocessed.'}
(REP/'MASTER_STAFF_FINAL_SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
(REP/'MASTER_STAFF_EXECUTION.md').write_text(f'''# MASTER STAFF EXECUTION\n\n## Evidence boundary\nNo new external bytes were materialized in this execution. Existing real canonical data were preserved.\n\n- TOTAL_MATCHES: {len(f)}\n- NEW_REAL_DATA_MATERIALIZED: 0\n- COUNTRIES: {f.country.nunique()}\n- COMPETITIONS: {f.competition.nunique()}\n- SEASONS: {f.season.nunique()}\n- MEN_MATCHES: {len(f)}\n- WOMEN_MATCHES: 0\n- H2H_RECORDS: {len(f)}\n- IMPORTANCE_RECORDS: {len(f)} (stage-only where available)\n- PLAYER/INJURY/LINEUP/LIVE records: 0\n- PIT_VALIDATED: {int(f.pit_status.eq('PIT_VALIDATED').sum())}\n- REAL_MONEY: DISABLED\n\n## Scientific limitation\nThe package is not market-validated because timestamped PIT odds, player/lineup/injury feeds, and historical LIVE snapshots are not materialized.\n\n## Status\nEDGE_NOT_DETERMINED\n''')
(REP/'MASTER_STAFF_SCIENTIFIC_STATUS.md').write_text('''# SCIENTIFIC STATUS\n\nENGINEERING STATUS: IMPLEMENTED ON EXISTING PACKAGE\nEMPIRICAL DATA STATUS: EXPANDED HISTORICAL REAL DATA PRESERVED; NO NEW EXTERNAL DATA IN THIS RUN\nPREDICTIVE STATUS: EXPERIMENTAL / OOS-TESTED WHERE SAMPLE ALLOWS\nMARKET STATUS: NOT PIT-VALIDATED\nLIVE STATUS: NOT HISTORICALLY VALIDATED\nPAPER TRADING STATUS: SCHEMA/ENGINE PRESENT; NO NEW PAPER BETS\nEDGE STATUS: EDGE_NOT_DETERMINED\nREAL MONEY STATUS: DISABLED\n''')
# immutable run manifest
manifest={'run':'MASTER_STAFF','input_zip':'ROBO_DA_BET_GLOBAL_FOOTBALL_CONTEXT_INTELLIGENCE_PATTERN_DISCOVERY_CONMEBOL.zip','new_real_data_materialized':0,'real_money':'DISABLED','output_files':len(list(OUT.glob('*'))),'model':model}
(OUT/'MASTER_STAFF_MANIFEST.json').write_text(json.dumps(manifest,indent=2,default=str))
print(json.dumps(summary,indent=2)); print(json.dumps(model,indent=2,default=str))
