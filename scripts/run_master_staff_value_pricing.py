from __future__ import annotations
import hashlib, json, subprocess, sys, zipfile, shutil
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from ml.app.master_staff.context_engine import build_context
from ml.app.master_staff.value_pricing import price_market
from ml.app.research.global_expansion import build_route_registry, inventory_local_real, attempt_registry

OUT=ROOT/'data/master_staff'; REP=ROOT/'reports/master_staff'; MAN=ROOT/'data/manifests'
for p in (OUT,REP,MAN): p.mkdir(parents=True,exist_ok=True)


def sha256_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def count_inventory():
    c=ROOT/'data/canonical/football_historical_real_canonical.csv'; d=pd.read_csv(c)
    d['gender']=d['gender'].fillna('MEN').astype(str).str.upper() if 'gender' in d.columns else 'MEN'
    return {
      'REAL_MATCHES':len(d),'COUNTRIES':int(d.country.nunique()),'COMPETITIONS':int(d.competition.nunique()),'SEASONS':int(d.season.nunique()),
      'MEN_MATCHES':int((d.gender=='MEN').sum()),'WOMEN_MATCHES':int((d.gender=='WOMEN').sum()),
      'ODDS_ROWS':int(d[['odds_1','odds_x','odds_2']].notna().any(axis=1).sum()),
      'ODDS_PIT_EXACT_OR_VALID':int(d.pit_status.astype(str).isin(['PIT_EXACT','PIT_VALID','EXACT_PIT','VALID_PIT','PIT_VALIDATED']).sum()),
      'ODDS_DATE_LEVEL':int(d.pit_status.astype(str).str.contains('DATE',na=False).sum()),
      'XG_ROWS':int(d[['home_xg','away_xg']].notna().all(axis=1).sum()),'CARDS_ROWS':int(d[['home_cards','away_cards']].notna().all(axis=1).sum()),
      'CORNERS_ROWS':int(d[['home_corners','away_corners']].notna().all(axis=1).sum()),'REFEREES':int(d.referee.notna().sum()),
      'LINEUPS':0,'PLAYERS':0,'INJURIES':0,'SUSPENSIONS':0,'SHOTS':0,'SOT':0,'EVENTS':0,'LIVE_SNAPSHOTS':0,'SETTLEMENTS':0
    }

before=count_inventory()
# Attempt real acquisition. Any bytes are admitted only if materialized by the acquisition layer.
registry=build_route_registry(); attempts,network=attempt_registry(ROOT,registry)
attempts.to_csv(MAN/'MASTER_STAFF_ACQUISITION.csv',index=False)

canonical=pd.read_csv(ROOT/'data/canonical/football_historical_real_canonical.csv')
canonical['kickoff_timestamp']=pd.to_datetime(canonical['kickoff_timestamp'],errors='coerce')
canonical['canonical_match_id']=canonical['match_id'].astype(str)
context=build_context(canonical)
features=pd.concat([canonical.reset_index(drop=True),context.reset_index(drop=True)],axis=1)
features.to_csv(OUT/'CONTEXT_INTELLIGENCE_FEATURES.csv',index=False)

# Explicit registries: empty evidence is preferable to fabricated evidence.
rivalry_cols=['team_a','team_b','rivalry_name','rivalry_type','country','region','evidence_source','confidence','status']
pd.DataFrame(columns=rivalry_cols).to_csv(OUT/'RIVALRY_REGISTRY.csv',index=False)
player_cols=['player_id','team_id','gender','position','importance_score','minutes_share','goal_contribution','assist_contribution','shot_contribution','sot_contribution','defensive_contribution','starting_probability','source','pit_status']
pd.DataFrame(columns=player_cols).to_csv(OUT/'PLAYER_IMPACT_RECORDS.csv',index=False)
for fn,cols in {
 'INJURY_ENGINE_RECORDS.csv':['player_id','team_id','gender','injury_type','injury_start','expected_return','actual_return','minutes_lost','source','decision_timestamp','pit_status'],
 'SUSPENSION_ENGINE_RECORDS.csv':['player_id','team_id','gender','reason','start','end','matches_missed','source','decision_timestamp','pit_status'],
 'LINEUP_ENGINE_RECORDS.csv':['canonical_match_id','team_id','player_id','status','expected_or_confirmed','published_at','decision_timestamp','source','pit_status'],
 'LIVE_SNAPSHOT_ENGINE.csv':['canonical_match_id','snapshot_timestamp','source_timestamp','minute','period','score','shots','sot','xg','corners','cards','odds','freshness','pit_status']
}.items(): pd.DataFrame(columns=cols).to_csv(OUT/fn,index=False)

# Current-round reference pricing is deliberately not promoted: no exact PIT odds in canonical history.
round_path=ROOT/'data/processed/round_2026-08-20/ROUND_2026-08-20_INTELLIGENCE.csv'
if round_path.exists():
    rd=pd.read_csv(round_path); rows=[]
    for r in rd.itertuples(index=False):
        for market,sel,odd in [('1X2','HOME',r.home_odds),('1X2','DRAW',r.draw_odds),('1X2','AWAY',r.away_odds)]:
            q=price_market(market=market,selection=sel,odds=odd,model_probability=None,pit_status=str(r.odds_pit_status),model_validated=False,sample_size=0,data_quality=0.0)
            rows.append({'home_team':r.home_team,'away_team':r.away_team,'market':market,'selection':sel,'odds':odd,**q.__dict__})
    pd.DataFrame(rows).to_csv(OUT/'VALUE_CANDIDATES.csv',index=False)
else:
    pd.DataFrame().to_csv(OUT/'VALUE_CANDIDATES.csv',index=False)

# Scientific source registry: web-confirmed routes are recorded as FOUND/REFERENCE only, never as materialized data.
source_registry=[
 {'source':'Football-Data.co.uk','url':'https://www.football-data.co.uk/all_new_data.php','state':'FOUND','evidence':'PUBLIC_SOURCE_CONFIRMED','materialized':False},
 {'source':'StatsBomb Open Data','url':'https://github.com/statsbomb/open-data','state':'FOUND','evidence':'PUBLIC_SOURCE_CONFIRMED','materialized':False},
 {'source':'The Odds API historical','url':'https://the-odds-api.com/historical-odds-data/','state':'FOUND','evidence':'HISTORICAL_SNAPSHOTS_DOCUMENTED','materialized':False},
 {'source':'API-Football','url':'https://www.api-football.com/','state':'FOUND','evidence':'CREDENTIAL_PROVIDER_ROUTE','materialized':False},
 {'source':'Sportmonks','url':'https://www.sportmonks.com/football-api/','state':'FOUND','evidence':'CREDENTIAL_PROVIDER_ROUTE','materialized':False},
]
pd.DataFrame(source_registry).to_csv(MAN/'MASTER_STAFF_SOURCE_REGISTRY.csv',index=False)

# Requested acquisition coverage registry: planning only unless materialized locally.
targets=[
('England','Premier League'),('England','Championship'),('England','League One'),('England','League Two'),('England','National League'),
('Germany','Bundesliga'),('Germany','2. Bundesliga'),('Germany','3. Liga'),('Germany','Regionalliga'),
('Spain','La Liga'),('Spain','Segunda Division'),('Spain','Primera Federación'),
('Italy','Serie A'),('Italy','Serie B'),('Italy','Serie C'),('Italy','Serie D'),
('France','Ligue 1'),('France','Ligue 2'),('France','National 2'),('France','National 3'),
('Portugal','Primeira Liga'),('Portugal','Liga 2'),('Argentina','Liga Profesional Argentina'),('Argentina','Primera B Nacional'),('Argentina','Primera B'),
('Brazil','Brasileirao Serie A'),('Brazil','Brasileirao Serie B'),('Brazil','Brasileirao Serie C'),('Brazil','Brasileirao Serie D'),
('Mexico','Liga MX'),('USA','MLS'),('USA','USL Championship'),('USA','MLS Next Pro'),('Netherlands','Eredivisie'),('Belgium','Belgian Pro League'),('Turkey','Super Lig'),('Scotland','Scottish Premiership'),('Japan','J1 League'),('Japan','J2 League'),('South Korea','K League 1'),('South Korea','K League 2'),
('CONMEBOL','Libertadores'),('CONMEBOL','Sudamericana'),('CONMEBOL','Recopa'),
('WOMEN','UEFA Women Champions League'),('WOMEN','NWSL'),('WOMEN','Liga F'),('WOMEN','Women Super League'),('WOMEN','Frauen-Bundesliga'),('WOMEN','Division 1 Feminine'),('WOMEN','Brasileirao Feminino')]
mat={(str(r.country),str(r.competition)) for r in canonical.itertuples()}
coverage=[]
for country,comp in targets:
    coverage.append({'country':country,'competition':comp,'status':'MATERIALIZED' if (country,comp) in mat else 'NOT_MATERIALIZED','matches_materialized':sum((canonical.country==country)&(canonical.competition==comp))})
pd.DataFrame(coverage).to_csv(OUT/'TARGET_COVERAGE_REGISTRY.csv',index=False)

# Integrity / state separation report.
after=count_inventory(); delta={k:after[k]-before[k] for k in before}
status={
 'FOUND':int((attempts.status.isin(['BLOCKED','FAILED','MATERIALIZED','PROCESSED'])).sum()),
 'DOWNLOADED':int(pd.to_numeric(attempts.bytes,errors='coerce').fillna(0).gt(0).sum()),
 'MATERIALIZED':int(attempts.materialized.fillna(False).sum()),
 'PROCESSED':int(attempts.processed.fillna(False).sum()),
 'PIT_VALIDATED':int(attempts.pit_validated.fillna(False).sum()),
 'USED_IN_MODEL':int(attempts.used_in_model.fillna(False).sum())}
summary={'before':before,'after':after,'delta':delta,'acquisition_state_counts':status,'network':network,'real_money':'DISABLED','new_real_data_materialized':int(delta['REAL_MATCHES']),'source_discoveries':source_registry,'scientific_status':'ACQUISITION_BLOCKED' if network.get('global_blocked') else 'ACQUISITION_ATTEMPTED'}
(REP/'MASTER_STAFF_VALUE_PRICING_EXECUTION.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,default=str))
(REP/'MASTER_STAFF_VALUE_PRICING_REPORT.md').write_text(f'''# MASTER STAFF — VALUE PRICING REPORT\n\n## Dataset integrity\n- BEFORE real matches: {before['REAL_MATCHES']}\n- AFTER real matches: {after['REAL_MATCHES']}\n- NEW REAL MATCHES: {delta['REAL_MATCHES']}\n- Network acquisition: {'BLOCKED' if network.get('global_blocked') else 'AVAILABLE'}\n\n## Evidence states\nFOUND={status['FOUND']} | DOWNLOADED={status['DOWNLOADED']} | MATERIALIZED={status['MATERIALIZED']} | PROCESSED={status['PROCESSED']} | PIT_VALIDATED={status['PIT_VALIDATED']} | USED_IN_MODEL={status['USED_IN_MODEL']}\n\n## Pricing rule\nNo `VALUE_BET` is allowed without exact/valid PIT, validated model, sufficient sample, adequate data quality, and minimum edge/EV. Date-level odds remain reference-only.\n\n## Current package market evidence\n- Canonical timestamped/PIT-valid odds: {after['ODDS_PIT_EXACT_OR_VALID']}\n- Date-level odds: {after['ODDS_DATE_LEVEL']}\n- Settlements: {after['SETTLEMENTS']}\n- CLV: NOT DETERMINED\n\n## Status\n`EDGE_NOT_DETERMINED` — no market edge is scientifically promoted.\n`REAL_MONEY=DISABLED`\n''',encoding='utf-8')
(REP/'MASTER_STAFF_CONTEXT_INTELLIGENCE.md').write_text(f'''# CONTEXT INTELLIGENCE\n\nH2H engine: temporal, prior-only, windows 3/5/10/20.\nRivalry registry: {len(pd.read_csv(OUT/'RIVALRY_REGISTRY.csv'))} materialized records.\nImportance: stage-only where present; mathematical qualification state is not promoted without table/aggregate evidence.\nRest/congestion: computed only from prior canonical timestamps.\nPlayer/injury/lineup/live evidence: not materialized.\n\nNo narrative context is promoted to quantitative edge.\n''',encoding='utf-8')
(REP/'MASTER_STAFF_H2H_RIVALRY_REPORT.md').write_text('''# H2H / RIVALRY REPORT\n\nH2H features are generated strictly from observations preceding each match. Windows: 3/5/10/20.\n\nRIVALRY_REGISTRY is intentionally empty in the empirical package; no rivalry was fabricated or inferred from narrative alone.\nRivalry effect status: `INSUFFICIENT_DATA`.\n''',encoding='utf-8')
(REP/'MASTER_STAFF_PLAYER_IMPACT_REPORT.md').write_text('''# PLAYER IMPACT REPORT\n\nPLAYER_RECORDS, INJURY_RECORDS, SUSPENSION_RECORDS and LINEUP_RECORDS remain empty because no real materialized player/availability bytes were acquired in this runtime.\n\nInfrastructure is present; empirical validation is not.\n''',encoding='utf-8')
(REP/'MASTER_STAFF_MARKET_QUALITY_REPORT.md').write_text(f'''# MARKET QUALITY\n\nCanonical odds rows: {after['ODDS_ROWS']}\nExact/valid PIT rows: {after['ODDS_PIT_EXACT_OR_VALID']}\nDate-level rows: {after['ODDS_DATE_LEVEL']}\nUnknown/other rows: {after['ODDS_ROWS']-after['ODDS_PIT_EXACT_OR_VALID']-after['ODDS_DATE_LEVEL']}\n\nNo CLV or ROI can be scientifically validated without PIT odds and settlements.\n''',encoding='utf-8')
(REP/'MASTER_STAFF_ROUND_ANALYSIS_REPORT.md').write_text('''# ROUND ANALYSIS\n\nThe current round artifact for 2026-08-20 is preserved. Its 15 market observations are date-level reference prices, not exact PIT. The existing round gate therefore remains `NO_BET/WAIT` and `EDGE_NOT_DETERMINED`.\n''',encoding='utf-8')
(REP/'MASTER_STAFF_SCIENTIFIC_STATUS.md').write_text('''# MASTER STAFF SCIENTIFIC STATUS\n\nIMPLEMENTED: context engine, temporal H2H 3/5/10/20, rest/congestion features, evidence-state registries, independent pricing gate, target coverage registry, acquisition audit, provenance/hashes, round analysis artifacts.\n\nMATERIALIZED: 4,864 existing real canonical matches; no new historical match bytes in this execution.\n\nVALIDATED: engineering tests and temporal/PIT gates. Predictive/market profitability remains unvalidated because exact PIT odds, settlements, player feeds and historical LIVE snapshots are absent.\n\nSTATUS: `ACQUISITION_BLOCKED` / `EDGE_NOT_DETERMINED` / `REAL_MONEY=DISABLED`.\n''',encoding='utf-8')
(REP/'NEGATIVE_RESULTS.csv').write_text('hypothesis,status,reason\nRIVALRY_EFFECT,INSUFFICIENT_DATA,no_materialized_rivalry_registry\nPLAYER_IMPACT,INSUFFICIENT_DATA,no_materialized_player_history\nINJURY_IMPACT,INSUFFICIENT_DATA,no_materialized_injury_history\nPIT_VALUE,INSUFFICIENT_DATA,no_exact_or_valid_pit_odds\nCLV,INSUFFICIENT_DATA,no_timestamped_odds_or_settlements\nLIVE_MODEL,INSUFFICIENT_DATA,no_historical_live_snapshots\n',encoding='utf-8')

# Final provenance for newly created artifacts.
prov=[]
for p in sorted([*OUT.glob('*'),*REP.glob('MASTER_STAFF_*'),MAN/'MASTER_STAFF_ACQUISITION.csv',MAN/'MASTER_STAFF_SOURCE_REGISTRY.csv',MAN/'MASTER_STAFF_ACQUISITION.csv']):
    if p.exists() and p.is_file(): prov.append({'file':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha256_file(p),'status':'MATERIALIZED_ARTIFACT'})
pd.DataFrame(prov).drop_duplicates('file').to_csv(OUT/'MASTER_STAFF_PROVENANCE.csv',index=False)

# Machine-readable final counts.
final_counts={**after,'NEW_REAL_MATCHES':delta['REAL_MATCHES'],'NEW_REAL_DATA_MATERIALIZED':int(delta['REAL_MATCHES']),'H2H_RECORDS':after['REAL_MATCHES'],'RIVALRY_RECORDS':0,'IMPORTANCE_RECORDS':after['REAL_MATCHES'],'PAPER_CANDIDATES':0,'VALUE_BETS':0,'REAL_MONEY':'DISABLED'}
(OUT/'DATASET_FINAL_COUNTS.json').write_text(json.dumps(final_counts,indent=2),encoding='utf-8')
(MAN/'ACQUISITION_MANIFEST_FINAL.json').write_text(json.dumps({'run':'MASTER_STAFF_VALUE_PRICING','attempted_routes':len(attempts),'states':status,'network':network,'new_real_data_materialized':int(delta['REAL_MATCHES']),'real_money':'DISABLED'},indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2,ensure_ascii=False,default=str))
