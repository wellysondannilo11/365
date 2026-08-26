import csv, json, hashlib, zipfile, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports'/'post_match_pilot'; DATA=ROOT/'data'/'post_match_pilot'; COV=ROOT/'reports'/'coverage'; DATA_COV=ROOT/'data'/'coverage'
for p in [OUT,DATA,COV,DATA_COV]: p.mkdir(parents=True,exist_ok=True)
SNAP=ROOT/'data/real_day_prematch/REAL_DAY_PREMATCH_SNAPSHOT.json'
with SNAP.open(encoding='utf-8') as f: snap=json.load(f)
zip_name=snap.get('input_zip')
# The input to this mission is the real-day pilot ZIP, whose snapshot embeds the prior input identity.
source_matches=snap.get('matches',[])
targets=[('LDU Quito','Mirassol'),('Olimpia','Vasco'),('Macará','Santos'),('Corinthians','Rosario Central'),('Botafogo','Cienciano')]
now=datetime.now(timezone.utc).isoformat()

# Snapshot immutability digest: hash the exact JSON before any output is produced.
snap_bytes=SNAP.read_bytes(); snap_hash=hashlib.sha256(snap_bytes).hexdigest()

# Historical coverage from the materialized feature store.
feature=ROOT/'data/master_staff/PREMATCH_FEATURE_STORE.csv'
df=pd.read_csv(feature,low_memory=False)
team_rows=[]
for home,away in targets:
    for team in [home,away]:
        m=df[(df.home_team==team)|(df.away_team==team)].copy()
        if m.empty:
            seasons={}; comps=0; home_n=away_n=0
        else:
            seasons=m.groupby(m.season.astype(str)).size().to_dict(); comps=m.competition.nunique()
            home_n=(m.home_team==team).sum(); away_n=(m.away_team==team).sum()
        cols={c for c in df.columns}
        def nonnull(col): return int(m[col].notna().sum()) if col in cols else 0
        metrics={k:nonnull(c) for k,c in {'goals_for':'home_goals','shots':'home_shots','sot':'home_sot','xg':'home_xg','corners':'home_corners','cards':'home_cards','lineups':'lineup_status','players':'player_count','injuries':'injury_count','suspensions':'suspension_count','odds':'odds_1','timestamped_odds':'odds_timestamp'}.items()}
        team_rows.append({'team':team,'historical_match_count':len(m),'home_matches':int(home_n),'away_matches':int(away_n),'competition_count':comps,'seasons':json.dumps(seasons,ensure_ascii=False),**metrics})

covdf=pd.DataFrame(team_rows)
covdf['historical_depth_score']=covdf.historical_match_count.clip(0,100)/100
covdf['recency_score']=covdf.apply(lambda r: sum(int(k[:4])>=2024 and v>0 for k,v in json.loads(r.seasons).items())/3,axis=1)
covdf['home_away_score']=((covdf.home_matches>0).astype(int)+(covdf.away_matches>0).astype(int))/2
covdf['competition_score']=(covdf.competition_count>0).astype(int)
stat_cols=['goals_for','shots','sot','xg','corners','cards']; covdf['statistical_coverage_score']=covdf[stat_cols].gt(0).mean(axis=1)
covdf['player_coverage_score']=covdf[['players','injuries','suspensions','lineups']].gt(0).mean(axis=1)
covdf['market_coverage_score']=covdf[['odds','timestamped_odds']].gt(0).mean(axis=1)
covdf['team_coverage_score']=(covdf[['historical_depth_score','recency_score','home_away_score','competition_score','statistical_coverage_score','player_coverage_score','market_coverage_score']].mean(axis=1)*100).round(2)
covdf['coverage_class']=pd.cut(covdf.team_coverage_score,[-1,20,40,60,80,101],labels=['CRITICAL','LOW','MODERATE','GOOD','EXCELLENT']).astype(str)
covdf.to_csv(DATA_COV/'TEAM_COVERAGE_5_PILOT_TEAMS.csv',index=False)

# Competition/season coverage.
base=df.groupby(['competition','season','gender'],dropna=False).size().reset_index(name='matches')
for col in ['events','shots','SOT','xG','corners','cards','lineups','players','injuries','suspensions','referees','odds','timestamped_odds','PIT_validated','LIVE','settlements']:
    base[col]=0
    if col in df.columns:
        g=df.groupby(['competition','season','gender'],dropna=False)[col].apply(lambda s:s.notna().sum()).reset_index(name=col)
        base=base.drop(columns=[col]).merge(g,on=['competition','season','gender'],how='left')
base.to_csv(COV/'DATA_COVERAGE_2020_2026.csv',index=False)

# Acquisition priority from current registry, emphasizing missing data with scientific value.
reg=ROOT/'data/manifests/MASTER_STAFF_SOURCE_REGISTRY.csv'
if reg.exists():
    r=pd.read_csv(reg)
    if len(r):
        r['SCIENTIFIC_VALUE']=r.get('priority',pd.Series(['UNKNOWN']*len(r))).astype(str)
        r['DATA_VOLUME']=r.get('coverage',pd.Series(['UNKNOWN']*len(r))).astype(str)
        r['DATA_QUALITY']=r.get('quality',pd.Series(['UNKNOWN']*len(r))).astype(str)
        r['TEMPORAL_QUALITY']=r.get('pit_status',pd.Series(['UNKNOWN']*len(r))).astype(str)
        r['COMPETITION_RELEVANCE']=r.get('competition',pd.Series(['UNKNOWN']*len(r))).astype(str)
        r['COST_ACCESS']=r.get('access',pd.Series(['UNKNOWN']*len(r))).astype(str)
        r.to_csv(COV/'ACQUISITION_PRIORITY.csv',index=False)

# Post-match status: the five fixtures have not finished at this audit timestamp; do not fabricate outcomes.
rows=[]
for home,away in targets:
    match=next((x for x in source_matches if x.get('home')==home and x.get('away')==away),None)
    rows.append({'home_team':home,'away_team':away,'audit_timestamp_utc':now,'status':'NOT_COMPLETED_AT_AUDIT','final_score':'UNKNOWN','winner':'UNKNOWN','qualification_result':'UNKNOWN','correct':'NOT_SETTLEABLE','brier':'NOT_AVAILABLE','log_loss':'NOT_AVAILABLE','postmatch_stats':'UNKNOWN','note':'Post-match evaluation is blocked until the fixture has actually ended; no future information was used.'})
pd.DataFrame(rows).to_csv(DATA/'POST_MATCH_PILOT_RESULTS.csv',index=False)

report=f'''# POST-MATCH PILOT — FORENSICS + COVERAGE AUDIT\n\nAudit timestamp (UTC): `{now}`\n\n## Snapshot integrity\n- Snapshot file: `{SNAP.relative_to(ROOT)}`\n- Snapshot SHA-256: `{snap_hash}`\n- Prospectively recorded matches: **{len(source_matches)}**\n- Original snapshots were not modified.\n\n## Post-match status\nThe five 20/08/2026 fixtures are scheduled for later on the audit date. At this execution time, authoritative post-match results are not yet available. Therefore the forensic section remains **PENDING** and no score, winner, Brier, Log Loss, ROI or CLV has been invented.\n\n| Jogo | Status | Resultado | Avaliação |\n|---|---|---|---|\n'''
for r in rows: report+=f"| {r['home_team']} x {r['away_team']} | {r['status']} | UNKNOWN | NOT_SETTLEABLE |\n"
report+='''\n### Scientific interpretation\n`SAMPLE_SIZE = 0 SETTLED` for this post-match execution. The prospective sample remains preserved for later settlement. A result cannot be used to claim edge or no-edge before the games end.\n\n## Coverage diagnosis\nThe current materialized feature store contains strong historical match counts in a limited set of competitions, but several of the five pilot clubs have zero local historical rows in the feature store. This blocks independent team-specific pricing and is the principal coverage bottleneck.\n\nSee `TEAM_COVERAGE_5_PILOT_TEAMS.csv` and `DATA_COVERAGE_2020_2026.csv`.\n'''
(OUT/'POST_MATCH_PILOT_REPORT.md').write_text(report,encoding='utf-8')

summary={'audit_timestamp_utc':now,'historical_matches':int(snap.get('historical_matches_before',0)),'prospective_snapshots':len(source_matches),'settled_matches':0,'postmatch_status':'PENDING_FIXTURES_NOT_FINISHED_AT_AUDIT','snapshot_sha256':snap_hash,'value_bets_from_pilot':0,'edge_status':'EDGE_NOT_DETERMINED','real_money':'DISABLED'}
(DATA/'POST_MATCH_AUDIT_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')

# Explicit acquisition gaps.
gaps='''# DATA COVERAGE GAPS — 2020–2026\n\n## Highest priority gaps\n1. Historical match rows for LDU Quito, Mirassol, Olimpia, Vasco, Macará, Rosario Central, Botafogo and Cienciano in the materialized feature store.\n2. Exact PIT odds with timestamp and bookmaker.\n3. xG, shots and SOT.\n4. Lineups, player identity and player-level availability.\n5. Injuries and suspensions with temporal provenance.\n6. Event-level data and live snapshots.\n7. Settlement and closing-price data for CLV.\n\n`FOUND != ACQUIRED != MATERIALIZED != PROCESSED != PIT_VALIDATED != USED_IN_MODEL`.\n'''
(COV/'DATA_COVERAGE_GAPS.md').write_text(gaps,encoding='utf-8')
print('audit generated', now)
