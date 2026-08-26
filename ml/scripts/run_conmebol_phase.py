from pathlib import Path
import sys,json,hashlib,shutil,zipfile,subprocess,os
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT))
from ml.app.conmebol.pipeline import parse_sudamericana_txt,parse_libertadores_csv,enrich,pattern_tests,oos_model,coverage,walk_forward_model
RAW=ROOT/'data/raw'; OUT=ROOT/'data/conmebol'; REPORT=ROOT/'reports/conmebol'
for p in [OUT/'raw',OUT/'processed',OUT/'manifests',OUT/'provenance',OUT/'schemas',REPORT]: p.mkdir(parents=True,exist_ok=True)
# Preserve raw files in conmebol area.
for f in RAW.glob('conmebol_sudamericana_*.txt'):
    shutil.copy2(f,OUT/'raw'/f.name)
shutil.copy2(RAW/'libertadores_brazilian_soccer_data.csv',OUT/'raw/libertadores_brazilian_soccer_data.csv')
frames=[]
for f in sorted(OUT.glob('raw/conmebol_sudamericana_*.txt')):
    frames.append(parse_sudamericana_txt(f,int(f.stem.rsplit('_',1)[1])))
frames.append(parse_libertadores_csv(OUT/'raw/libertadores_brazilian_soccer_data.csv'))
con=pd.concat(frames,ignore_index=True)
con=enrich(con)
con.to_csv(OUT/'processed/CONMEBOL_MATCHES_REAL.csv',index=False)
# integrate canonical, preserving existing rows exactly and avoiding duplicate canonical IDs
canon_path=ROOT/'data/canonical/football_historical_real_canonical.csv'; canon=pd.read_csv(canon_path)
new=pd.DataFrame({
'match_id':con.canonical_match_id,'country':con.country,'competition':con.competition,'division':'CUP','season':con.season.astype(str),'round':con.stage,
'kickoff_timestamp':con.match_date.astype(str),'home_team':con.home_team,'away_team':con.away_team,'home_goals':con.home_goals,'away_goals':con.away_goals,
'referee':pd.NA,'home_cards':pd.NA,'away_cards':pd.NA,'total_cards':pd.NA,'home_corners':pd.NA,'away_corners':pd.NA,'total_corners':pd.NA,
'home_xg':pd.NA,'away_xg':pd.NA,'odds_1':pd.NA,'odds_x':pd.NA,'odds_2':pd.NA,'over_2_5':pd.NA,'under_2_5':pd.NA,'btts_yes':pd.NA,'btts_no':pd.NA,'asian_handicap':pd.NA,
'bookmaker':pd.NA,'odds_timestamp':pd.NA,'feature_timestamp':pd.NA,'decision_timestamp':pd.NA,'source':con.source,'source_url':con.source_url,'provenance_file':'data/conmebol/provenance/CONMEBOL_PROVENANCE.csv','pit_status':con.pit_status,'data_type':con.data_type})
new=new[~new.match_id.isin(canon.match_id)]
# Preserve pre-existing canonical bytes; append only genuinely new rows.
if canon_path.exists():
    existing_bytes=canon_path.read_bytes()
else:
    existing_bytes=canon.to_csv(index=False,lineterminator='\n').encode()
with canon_path.open('wb') as fh:
    fh.write(existing_bytes)
    if not existing_bytes.endswith(b'\n'): fh.write(b'\n')
    new.to_csv(fh,index=False,header=False,lineterminator='\n')
prov=con[['canonical_match_id','competition','season','match_date','source','source_url','pit_status','data_type']].copy(); prov['source_sha256']=pd.NA; prov.to_csv(OUT/'provenance/CONMEBOL_PROVENANCE.csv',index=False)
# hashes
for f in [OUT/'processed/CONMEBOL_MATCHES_REAL.csv',OUT/'provenance/CONMEBOL_PROVENANCE.csv']:
    h=hashlib.sha256(f.read_bytes()).hexdigest(); (OUT/'provenance'/(f.name+'.sha256')).write_text(f'{h}  {f.as_posix()}\n')
# coverage and statistical research
cov=coverage(con); cov.to_csv(REPORT/'CONMEBOL_DATASET_COVERAGE.csv',index=False)
pat=pattern_tests(con); pat.to_csv(REPORT/'CONMEBOL_PATTERN_RESULTS.csv',index=False)
model=oos_model(con); wf=walk_forward_model(con); model['walk_forward']=wf; (REPORT/'CONMEBOL_MODEL_RESULTS.json').write_text(json.dumps(model,ensure_ascii=False,indent=2,default=str))
# acquisition state
requested=[]
for comp in ['Copa Libertadores','Copa Sudamericana']:
  for y in range(2020,2027): requested.append((comp,y))
mat={(r.competition,int(r.season)) for r in con.itertuples()}
rows=[]
for comp,y in requested:
    n=int(((con.competition==comp)&(con.season==y)).sum())
    rows.append({'competition':comp,'season':y,'requested':'YES','found':'YES' if n else 'NO','downloaded':'YES' if n else 'NO','materialized':'YES' if n else 'NO','processed':'YES' if n else 'NO','PIT_validated':'NO','used_in_model':'YES' if n else 'NO','matches':n,'status':'MATERIALIZED' if n else 'ACQUISITION_BLOCKED'})
acq=pd.DataFrame(rows); acq.to_csv(OUT/'manifests/CONMEBOL_ACQUISITION_MATRIX.csv',index=False)
manifest={'generated_at_utc':pd.Timestamp.utcnow().isoformat(),'real_money':'DISABLED','window_requested':'2020-01-01 to 2026-12-31','materialized_matches':int(len(con)),'new_canonical_rows':int(len(new)),'competitions':sorted(con.competition.unique().tolist()),'seasons':sorted(con.season.unique().tolist()),'male_matches':int((con.gender=='MEN').sum()),'female_matches':0,'women_status':'WOMEN_DATA_INSUFFICIENT','pit_validated_matches':0,'timestamped_odds':0,'live_snapshots':0,'settlements':0,'acquisition_blocked':acq.query("status=='ACQUISITION_BLOCKED'").to_dict('records')}
(OUT/'manifests/CONMEBOL_EXECUTION_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
# specialist research tables
pat=pattern_tests(con)
pat.to_csv(REPORT/'CONMEBOL_PATTERN_RESULTS.csv',index=False)
negative=pd.DataFrame([
 {'hypothesis':'PIT market edge from CONMEBOL results','status':'INSUFFICIENT_DATA','reason':'No timestamped odds or settlements materialized'},
 {'hypothesis':'Player-key absence impact','status':'INSUFFICIENT_DATA','reason':'No real player/lineup/injury layer materialized'},
 {'hypothesis':'Referee cards effect','status':'INSUFFICIENT_DATA','reason':'No referee/card event layer materialized'},
 {'hypothesis':'Shots/SOT/xG predictive effect','status':'INSUFFICIENT_DATA','reason':'No shots/SOT/xG layer materialized'},
 {'hypothesis':'LIVE posterior update','status':'INSUFFICIENT_DATA','reason':'No real LIVE snapshots materialized'},
])
negative.to_csv(REPORT/'CONMEBOL_NEGATIVE_RESULTS.csv',index=False)
hyp=pd.DataFrame([
 {'hypothesis':'Knockout stage home-win behavior differs from group stage','status':'EXPLORATORY','next_test':'larger multi-season Libertadores + PIT/context controls'},
 {'hypothesis':'Prior-only rolling form adds predictive information','status':'PROMISING','next_test':'compare against Elo/strength baseline on full CONMEBOL 2020-2026'},
 {'hypothesis':'Rest advantage adds predictive information','status':'INCONCLUSIVE','next_test':'add domestic+continental schedule and travel data'},
 {'hypothesis':'Must-win/qualification state changes market-relevant behavior','status':'INSUFFICIENT_DATA','next_test':'materialize standings/aggregate state before kickoff'},
])
hyp.to_csv(REPORT/'CONMEBOL_HYPOTHESES.csv',index=False)
fi=pd.DataFrame([
 {'feature':'home_form5','model_role':'PREMATCH_CONTEXT','importance':'COEFFICIENT_AVAILABLE','status':'CANDIDATE'},
 {'feature':'away_form5','model_role':'PREMATCH_CONTEXT','importance':'COEFFICIENT_AVAILABLE','status':'CANDIDATE'},
 {'feature':'rest_advantage','model_role':'PREMATCH_CONTEXT','importance':'COEFFICIENT_AVAILABLE','status':'CANDIDATE'},
 {'feature':'PIT_odds','model_role':'MARKET','importance':'NOT_AVAILABLE','status':'INSUFFICIENT_DATA'},
 {'feature':'player_importance','model_role':'PLAYER','importance':'NOT_AVAILABLE','status':'INSUFFICIENT_DATA'},
])
fi.to_csv(REPORT/'CONMEBOL_FEATURE_IMPORTANCE.csv',index=False)
# reports
final=f'''# CONMEBOL DATASET FINAL REPORT\n\n## Scientific status\n`EDGE_NOT_DETERMINED`\n\n## Real data materialized\n**{len(con)} matches** across Libertadores (2020–2022 available from the materialized CSV source) and Sudamericana (2020–2025 completed rows available from openfootball files). 2026 acquisition was not materialized in this execution.\n\n## Coverage\n- FOUND/DOWNLOADED/MATERIALIZED/PROCESSED are tracked per season in `data/conmebol/manifests/CONMEBOL_ACQUISITION_MATRIX.csv`.\n- PIT validated: 0.\n- Timestamped odds: 0.\n- LIVE snapshots: 0.\n- Settlements: 0.\n- Female CONMEBOL: `WOMEN_DATA_INSUFFICIENT`.\n\n## Research\nThe available CONMEBOL layer supports result, goal, stage, group, home/away, rest and pre-match rolling-form research. It does **not** support player-impact, injuries, lineups, cards, corners, shots, SOT, xG or PIT market edge claims for this materialized layer because those fields were not present in the acquired sources.\n\n## Edge\nNo EDGE is confirmed. No ROI/CLV/PIT market conclusion is asserted.\n\n## Limitations\n2026 CONMEBOL data was not materialized; 2023–2026 Libertadores was not available in the acquired materialized source used here. Missing event/player/statistical layers remain explicit gaps.\n'''
(REPORT/'CONMEBOL_DATASET_FINAL_REPORT.md').write_text(final,encoding='utf-8')
(REPORT/'CONTEXT_INTELLIGENCE_REPORT.md').write_text('# Context Intelligence Report\n\nImplemented: stage, group, knockout/final context, rest days, prior-only rolling form, home/away result context. Motivation is not inferred psychologically; competition-state features require standings/aggregate inputs not present in the materialized sources.\n',encoding='utf-8')
(REPORT/'PLAYER_IMPACT_REPORT.md').write_text('# Player Impact Report\n\nSTATUS: INSUFFICIENT_DATA. No real player/lineup/injury dataset was materialized in this phase. No player importance or absence impact is fabricated.\n',encoding='utf-8')
(REPORT/'INJURY_RETURN_REPORT.md').write_text('# Injury Return Report\n\nSTATUS: INSUFFICIENT_DATA.\n',encoding='utf-8')
(REPORT/'COMPETITIVE_MOTIVATION_REPORT.md').write_text('# Competitive Motivation Report\n\nSTATUS: PARTIAL. Stage is known; standings/aggregate state before each match is not sufficiently materialized to infer must-win/qualification states without future-information risk.\n',encoding='utf-8')
(REPORT/'PATTERN_DISCOVERY_GLOBAL_REPORT.md').write_text('# Global Pattern Discovery\n\nResults are exploratory only. FDR-adjusted results are in `CONMEBOL_PATTERN_RESULTS.csv`. OOS model results are in `CONMEBOL_MODEL_RESULTS.json`.\n',encoding='utf-8')
(REPORT/'PATTERN_DISCOVERY_NEGATIVE_RESULTS.md').write_text('# Negative Results\n\nNo market edge claims were tested because PIT odds and settlements are absent. Complex player/context hypotheses are marked insufficient data rather than failed.\n',encoding='utf-8')
(REPORT/'PATTERN_DISCOVERY_OOS.md').write_text('# OOS\n\nTemporal split is enforced by date order. See `CONMEBOL_MODEL_RESULTS.json`.\n',encoding='utf-8')
(REPORT/'PATTERN_DISCOVERY_WALK_FORWARD.md').write_text('# Walk Forward\n\nA full walk-forward edge test is NOT RUN because PIT odds/settlements are absent. The prior-only feature construction is temporal-safe.\n',encoding='utf-8')
(REPORT/'PATTERN_DISCOVERY_MULTIPLE_TESTING.md').write_text('# Multiple Testing\n\nBenjamini-Hochberg FDR is applied to the exploratory hypothesis family.\n',encoding='utf-8')
(REPORT/'FINAL_SCIENTIFIC_STATUS.md').write_text('# FINAL SCIENTIFIC STATUS\n\n`EDGE_NOT_DETERMINED`\n\nREAL_MONEY = DISABLED\n\nThe CONMEBOL empirical dataset has been expanded with materialized real results, but PIT odds, settlements, LIVE snapshots, player/lineup/injury layers and full 2020–2026 Libertadores/Sudamericana coverage are not established.\n',encoding='utf-8')
(OUT/'schemas/CONMEBOL_SCHEMA.md').write_text('''# CONMEBOL schema\n\nRequired: canonical_match_id, competition, season, gender, country, stage, group, match_date, home_team, away_team, home_goals, away_goals, pit_status, data_type, source, source_url.\n\nOptional future-only fields: events, shots, SOT, xG, corners, cards, referee, lineups, players, injuries, suspensions, timestamped_odds, LIVE snapshots, settlements.\n''',encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False,indent=2))
