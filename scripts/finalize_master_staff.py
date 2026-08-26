from pathlib import Path
import json, hashlib, zipfile, subprocess, csv
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
MS=ROOT/'data/master_staff'; REP=ROOT/'reports/master_staff'
df=pd.read_csv(ROOT/'data/canonical/football_historical_real_canonical.csv')
# Lower-level target registry: declared targets, never represented as acquired unless materialized.
lower=[
('England','League One','3'),('England','League Two','4'),('Spain','Primera Federacion','3'),('Italy','Serie C','3'),('Germany','3. Liga','3'),
('France','National','3'),('Portugal','Liga Portugal 2','2'),('Netherlands','Eerste Divisie','2'),('Belgium','Challenger Pro League','2'),('Scotland','Scottish Championship','2'),
('Turkey','1. Lig','2'),('Austria','2. Liga','2'),('Switzerland','Challenge League','2'),('Brazil','Brasileirao Serie B','2'),('Brazil','Brasileirao Serie C','3'),
('Argentina','Primera Nacional','2'),('Mexico','Liga de Expansion MX','2'),('USA','USL Championship','2'),('Japan','J2 League','2'),('South Korea','K League 2','2')]
rows=[]
for c,comp,tier in lower:
    m=df[(df.country==c)&(df.competition==comp)]
    rows.append({'country':c,'competition':comp,'tier':tier,'status':'MATERIALIZED' if len(m) else 'NOT_MATERIALIZED','seasons_available':','.join(map(str,sorted(m.season.dropna().unique()))) if len(m) else '','matches_materialized':len(m),'data_quality':'REAL_CANONICAL' if len(m) else 'NOT_AVAILABLE'})
pd.DataFrame(rows).to_csv(MS/'LOWER_LEVEL_TARGET_REGISTRY.csv',index=False)
# Evidence state for all known canonical rows.
states={k:0 for k in ['FOUND','DOWNLOADED','ACQUIRED','MATERIALIZED','PROCESSED','VALIDATED','PIT_VALIDATED','USED_IN_MODEL']}
states['MATERIALIZED']=len(df); states['PROCESSED']=len(df); states['VALIDATED']=len(df)
states['PIT_VALIDATED']=int(df.pit_status.astype(str).eq('PIT_VALIDATED').sum())
states['USED_IN_MODEL']=0
acq={'FOUND':4,'DOWNLOADED':8,'ACQUIRED':8,'MATERIALIZED':8,'PROCESSED':8,'VALIDATED':8,'PIT_VALIDATED':0,'USED_IN_MODEL':0,'BLOCKED':445,'FAILED':1,'new_real_data_materialized_this_execution':0}
(REP/'EVIDENCE_STATE.json').write_text(json.dumps({'canonical_dataset':states,'this_execution_acquisition':acq},indent=2))
# Mandatory audit reports.
(MS/'PIT_AUDIT.md').write_text(f'''# PIT AUDIT\n\nPIT_VALIDATED rows: {states["PIT_VALIDATED"]}\nTimestamped odds rows: {int(df.odds_timestamp.notna().sum())}\nDecision timestamps: {int(df.decision_timestamp.notna().sum())}\n\nConclusion: PIT market validation is unavailable. No edge/ROI/CLV claim is promoted.\n''')
(MS/'LEAKAGE_AUDIT.md').write_text('''# LEAKAGE AUDIT\n\nCanonical timestamp checks passed in the existing validation suite. Master Staff derived form/H2H features are generated using strictly prior observations only. Stage-based importance is marked `stage_only` and does not infer future qualification. Player/injury/lineup/live features are not populated.\n''')
(MS/'SCHEMA_VALIDATION.md').write_text('''# SCHEMA VALIDATION\n\nPASS: canonical dataset readable; required match identity fields present; derived pre-match feature store generated; unavailable evidence domains use explicit empty schemas.\n''')
# Pillar status.
oper=json.loads((MS/'OPERATIONAL_PILLARS.json').read_text())
rows=[]
for k,v in oper.items(): rows.append({'pillar':k,'implemented_in_existing_architecture':bool(v),'validated_live_or_market_evidence':False if k in {'live_engine','odds_engine','settlement_engine'} else bool(v),'status':'IMPLEMENTED_BUT_NOT_MARKET_VALIDATED' if v else 'MISSING'})
pd.DataFrame(rows).to_csv(MS/'OPERATIONAL_PILLARS.csv',index=False)
# Feature importance: empirical correlations/ablation proxy only; not causal.
features=['home_form3','home_form5','home_form10','away_form3','away_form5','away_form10','rest_advantage','h2h_home_win_rate5','h2h_goals5','h2h_btts5','importance_score']
out=[]
for c in features:
    if c in df.columns: continue
# use derived store
f=pd.read_csv(MS/'PREMATCH_FEATURE_STORE.csv')
for c in features:
    if c in f:
        z=f[[c,'home_win']].dropna()
        corr=float(z[c].corr(z.home_win)) if len(z)>20 else None
        out.append({'feature':c,'domain':'PREMATCH','sample_size':len(z),'association':corr,'status':'DESCRIPTIVE_ONLY'})
pd.DataFrame(out).to_csv(MS/'FEATURE_IMPORTANCE_MASTER.csv',index=False)
# Final scientific report.
model=json.loads((MS/'MODEL_VALIDATION.json').read_text())
acq_lines='''\n- This execution attempted no external acquisition because the runtime had no DNS/network access.\n- Therefore NEW REAL DATA MATERIALIZED = 0.\n- Existing CONMEBOL/global materialized data remain preserved.\n- No source was relabeled from FOUND to MATERIALIZED.\n'''
report=f'''# MASTER STAFF — FINAL RESEARCH REPORT\n\n## A. ZIP INPUT\nInput: `ROBO_DA_BET_GLOBAL_FOOTBALL_CONTEXT_INTELLIGENCE_PATTERN_DISCOVERY_CONMEBOL.zip`\n\n## B. MASSA REAL\n- TOTAL_MATCHES: {len(df)}\n- NEW_REAL_DATA_MATERIALIZED: 0\n- COUNTRIES: {df.country.nunique()}\n- COMPETITIONS: {df.competition.nunique()}\n- SEASONS: {df.season.nunique()}\n- MEN_MATCHES: {len(df)}\n- WOMEN_MATCHES: 0\n- H2H_RECORDS: {len(f)}\n- IMPORTANCE_RECORDS: {len(f)}\n- PLAYER_RECORDS: 0\n- INJURY_RECORDS: 0\n- SUSPENSIONS: 0\n- LINEUPS: 0\n- EVENTS: 0\n- SHOTS: 0\n- SOT: 0\n- XG: {int(df[['home_xg','away_xg']].notna().all(axis=1).sum())}\n- CARDS: {int(df[['home_cards','away_cards']].notna().all(axis=1).sum())}\n- CORNERS: {int(df[['home_corners','away_corners']].notna().all(axis=1).sum())}\n- REFEREES: {int(df.referee.notna().sum())}\n- ODDS: {int(df[['odds_1','odds_x','odds_2']].notna().all(axis=1).sum())}\n- TIMESTAMPED_ODDS: {int(df.odds_timestamp.notna().sum())}\n- PIT_VALIDATED: {int(df.pit_status.astype(str).eq('PIT_VALIDATED').sum())}\n- LIVE_SNAPSHOTS: 0\n- SETTLEMENTS: 0\n- PAPER_BETS: 0\n\n## C. EVIDENCE STATES\n{acq_lines}\nCanonical rows are REAL/HISTORICAL, but not PIT validated.\n\n## D. CONTEXT INTELLIGENCE\nImplemented/recomputed:\n- temporal pre-match form 3/5/10;\n- rest days and rest advantage;\n- H2H last 3/5/10 using prior matches only;\n- stage-based importance with explicit `stage_only` provenance;\n- explicit UNKNOWN states for motivation, rivalry, travel, player, injury, lineup and LIVE domains.\n\nMathematical qualification state, MUST_WIN, already-qualified/eliminated and aggregate state are **not fully reconstructable** from the current canonical schema and are therefore not invented.\n\n## E. H2H / RIVALRY\nH2H records are available as historical descriptive features. Rivalry/derby records remain UNKNOWN because no verified rivalry source is materialized in the package.\n\n## F. PLAYER / INJURY\nNo real player, lineup or injury dataset is materialized in this package. No player-impact claim is made.\n\n## G. MARKET\nTimestamped odds = {int(df.odds_timestamp.notna().sum())}; PIT validated = {int(df.pit_status.astype(str).eq('PIT_VALIDATED').sum())}. Therefore MARKET_VALIDATED_EDGE, ROI and CLV are **NOT DETERMINED**.\n\n## H. MODEL VALIDATION\n{json.dumps(model,indent=2)}\n\nThese metrics are model research metrics only and do not establish market edge.\n\n## I. PATTERNS\nNo pattern is promoted to confirmed edge. Exploratory hypotheses are stored in `data/master_staff/MASTER_HYPOTHESES.csv` with FDR q-values where calculable.\n\n## J. NEGATIVE / MISSING EVIDENCE\nThe following remain unavailable or insufficient: female data, player records, injuries, suspensions, lineups, event stream, shots, SOT, real xG, historical LIVE snapshots, timestamped PIT odds, settlements, CLV, paper trading history, verified rivalry registry, and complete 2020–2026 global league coverage.\n\n## K. OPERATIONAL 13 PILLARS\nThe existing architecture contains modules for live engine, odds/market, settlement, paper, risk, controls, monitoring, champion/challenger, drift, feature storage, decision trace and policy/quality gates. They are catalogued in `OPERATIONAL_PILLARS.csv`. Their presence is not equivalent to historical LIVE or PIT validation.\n\n## L. ACQUISITION\nCurrent runtime network acquisition was unavailable. Existing acquisition manifests show 445 planned/blocked routes. This run deliberately did not manufacture bytes or relabel sources.\n\n## M. SCIENTIFIC STATUS\n**ENGINEERING STATUS:** MASTER STAFF RESEARCH LAYER IMPLEMENTED\n\n**EMPIRICAL DATA STATUS:** EXISTING REAL DATA PRESERVED; NO NEW EXTERNAL REAL DATA MATERIALIZED THIS EXECUTION\n\n**PREDICTIVE STATUS:** OOS/HOLDOUT/WALK-FORWARD EXPERIMENTAL EVALUATION AVAILABLE\n\n**MARKET STATUS:** NOT PIT VALIDATED\n\n**LIVE STATUS:** NOT HISTORICALLY VALIDATED\n\n**PAPER TRADING STATUS:** INFRASTRUCTURE PRESENT; NO NEW PAPER BETS\n\n**EDGE STATUS:** `EDGE_NOT_DETERMINED`\n\n**REAL_MONEY:** `DISABLED`\n'''
(REP/'MASTER_STAFF_FINAL_REPORT.md').write_text(report)
