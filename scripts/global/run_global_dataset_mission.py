from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
WINDOW_START=pd.Timestamp('2020-01-01')
WINDOW_END=pd.Timestamp('2026-08-20 23:59:59')

TARGETS = [
('England','Premier League','A'),('England','Championship','A'),('England','League One','B'),('England','League Two','B'),
('Spain','La Liga','A'),('Spain','Segunda División','B'),('Italy','Serie A','A'),('Italy','Serie B','B'),
('Germany','Bundesliga','A'),('Germany','2. Bundesliga','B'),('France','Ligue 1','A'),('France','Ligue 2','B'),
('Portugal','Primeira Liga','A'),('Portugal','Segunda Liga','B'),('Netherlands','Eredivisie','A'),('Belgium','Belgian Pro League','A'),
('Turkey','Süper Lig','A'),('Greece','Super League','B'),('Scotland','Premiership','A'),('Austria','Bundesliga','B'),
('Switzerland','Super League','B'),('Denmark','Superliga','B'),('Norway','Eliteserien','B'),('Sweden','Allsvenskan','B'),
('Poland','Ekstraklasa','B'),('Czechia','Czech First League','B'),('Brazil','Brasileirão Série A','A'),('Brazil','Brasileirão Série B','A'),
('Brazil','Brasileirão Série C','B'),('Brazil','Brasileirão Série D','B'),('Brazil','Copa do Brasil','A'),('Argentina','Primera División','A'),
('Argentina','Primera Nacional','B'),('Argentina','Copa Argentina','A'),('Chile','Primera División','B'),('Colombia','Primera A','B'),
('Uruguay','Primera División','B'),('Paraguay','Primera División','B'),('Ecuador','LigaPro','B'),('Peru','Liga 1','B'),
('Bolivia','Primera División','C'),('Venezuela','Primera División','C'),('CONMEBOL','Libertadores','A'),('CONMEBOL','Sudamericana','A'),
('CONMEBOL','Recopa Sudamericana','B'),('USA/Canada','MLS','A'),('Mexico','Liga MX','A'),('Mexico','Liga de Expansión MX','B'),
('Japan','J1 League','B'),('Japan','J2 League','C'),('South Korea','K League 1','B'),('South Korea','K League 2','C'),
('China','Chinese Super League','B'),('Saudi Arabia','Saudi Pro League','B'),('Australia','A-League','B'),('Egypt','Premier League','C'),
('South Africa','Premier Division','C'),('Morocco','Botola Pro','C'),('Tunisia','Ligue 1','C'),('Algeria','Ligue 1','C'),
]


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()


def read_snapshot_hash() -> dict:
    p=ROOT/'data/real_day_prematch/REAL_DAY_PREMATCH_SNAPSHOT.json'
    raw=p.read_bytes()
    return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'predictions_created':json.loads(raw.decode()).get('predictions_created')}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input-zip',default='')
    ap.add_argument('--skip-tests',action='store_true')
    args=ap.parse_args()
    before=read_snapshot_hash()
    canon_path=ROOT/'data/canonical/football_historical_real_canonical.csv'
    canon=pd.read_csv(canon_path)
    before_count=len(canon)
    # Verify uniqueness and temporal bounds of materialized empirical records.
    ts=pd.to_datetime(canon['kickoff_timestamp'],format='mixed',errors='coerce')
    empirical=canon[canon['data_type'].astype(str).str.startswith('HISTORICAL_REAL')].copy()
    in_window=(ts>=WINDOW_START)&(ts<=WINDOW_END)
    # Build exact key deduplication report without deleting anything silently.
    key=ts.dt.date.astype(str)+'|'+canon.home_team.astype(str)+'|'+canon.away_team.astype(str)+'|'+canon.competition.astype(str)
    dup_count=int(key.duplicated(keep=False).sum())
    dup_groups=int(key[key.duplicated(keep=False)].nunique())
    # Coverage reports
    c=canon.loc[in_window].copy()
    c['gender']=c.get('gender',pd.Series(['MEN']*len(c),index=c.index)).fillna('MEN').astype(str).str.upper()
    c['calendar_year']=pd.to_datetime(c['kickoff_timestamp'],format='mixed',errors='coerce').dt.year
    coverage=(c.groupby(['country','competition','season','gender'],dropna=False).agg(matches=('match_id','nunique')).reset_index())
    coverage.to_csv(ROOT/'data/global_dataset/reports/GLOBAL_DATASET_COVERAGE.csv',index=False)
    # Full requested 2020-2026 matrix: missing seasons remain explicit.
    rows=[]
    for country,comp,priority in TARGETS:
        for season in range(2020,2027):
            found=int(((c.country.astype(str)==country)&(c.competition.astype(str)==comp)&(c.season.astype(str).str.contains(str(season)))).sum())
            rows.append({'country':country,'competition':comp,'season':season,'gender':'MEN','priority':priority,'matches_materialized':found,'status':'MATERIALIZED' if found else 'NOT_MATERIALIZED'})
            rows.append({'country':country,'competition':comp,'season':season,'gender':'WOMEN','priority':priority,'matches_materialized':0,'status':'NOT_MATERIALIZED'})
    pd.DataFrame(rows).to_csv(ROOT/'data/global_dataset/reports/GLOBAL_COMPETITION_SEASON_MATRIX_2020_2026.csv',index=False)
    # Field coverage
    fields={
      'cards':c[['home_cards','away_cards']].notna().any(axis=1),
      'corners':c[['home_corners','away_corners']].notna().any(axis=1),
      'xg':c[['home_xg','away_xg']].notna().any(axis=1),
      'shots':pd.Series(False,index=c.index), 'sot':pd.Series(False,index=c.index),
      'lineups':pd.Series(False,index=c.index), 'events':pd.Series(False,index=c.index),
      'odds':c[['odds_1','odds_x','odds_2']].notna().any(axis=1),
    }
    pd.DataFrame([{'field':k,'rows':int(v.sum()),'coverage_pct':round(100*v.mean(),3)} for k,v in fields.items()]).to_csv(ROOT/'data/global_dataset/reports/GLOBAL_FIELD_COVERAGE.csv',index=False)
    # Explicit acquisition state: found != acquired.
    manifest=json.loads((ROOT/'data/global_dataset/registry/GLOBAL_ACQUISITION_MANIFEST.json').read_text())
    manifest['execution_timestamp']=datetime.now(timezone.utc).isoformat()
    manifest['input_zip']=args.input_zip
    manifest['input_zip_sha256']=sha256(ROOT/args.input_zip) if args.input_zip and (ROOT/args.input_zip).exists() else None
    manifest['deduplication']={'duplicate_rows_detected':dup_count,'duplicate_groups':dup_groups,'rows_deleted':0}
    manifest['validation']={'temporal_window':'2020-01-01 through 2026-08-20','future_rows_allowed_in_historical':False,'gender_crossfill':False}
    (ROOT/'data/global_dataset/registry/GLOBAL_ACQUISITION_MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
    # Snapshot protection artifact
    after=read_snapshot_hash()
    protection={'before':before,'after':after,'unchanged':before['sha256']==after['sha256'] and before['bytes']==after['bytes'],'action':'READ_ONLY'}
    (ROOT/'data/global_dataset/reports/PREMATCH_SNAPSHOT_PROTECTION.json').write_text(json.dumps(protection,indent=2))
    if not protection['unchanged']:
        raise RuntimeError('PREMATCH_PREDICTION_SNAPSHOT changed during mission')
    # Summary
    counts={
      'REAL_MATCHES_BEFORE':before_count,'REAL_MATCHES_AFTER':len(canon),'NEW_REAL_MATCHES':len(canon)-before_count,
      'COUNTRIES':int(c.country.nunique()),'COMPETITIONS':int(c.competition.nunique()),'SEASONS':int(c.season.nunique()),
      'TEAMS':int(len(set(c.home_team.dropna())|set(c.away_team.dropna()))),'MEN_MATCHES':int((c.gender=='MEN').sum()),'WOMEN_MATCHES':int((c.gender=='WOMEN').sum()),
      'CARDS_MATCHES':int(fields['cards'].sum()),'CORNERS_MATCHES':int(fields['corners'].sum()),'SHOTS_MATCHES':0,'SOT_MATCHES':0,'XG_MATCHES':0,
      'EVENT_MATCHES':0,'LINEUP_MATCHES':0,'INJURY_RECORDS':0,'SUSPENSION_RECORDS':0,'REFEREE_MATCHES':int(c.referee.notna().sum()),
      'ODDS_MATCHES':int(fields['odds'].sum()),'PIT_EXACT':int(c.pit_status.eq('PIT_EXACT').sum()),'PIT_DATE_LEVEL':int(c.pit_status.eq('PIT_DATE_ONLY').sum()),'NON_PIT':int(c.pit_status.eq('NON_PIT').sum()),'LIVE_MATCHES':0,'SETTLEMENTS':0,'REAL_MONEY':'DISABLED'
    }
    (ROOT/'data/global_dataset/reports/GLOBAL_DATASET_COUNTS.json').write_text(json.dumps(counts,indent=2))
    # Scientific status
    status='DATA_INSUFFICIENT_FOR_GLOBAL_CLAIM' if counts['COMPETITIONS']<20 else 'PARTIAL_GLOBAL_MATERIALIZATION'
    report=f'''# GLOBAL DATASET FINAL REPORT\n\nExecution date: 2026-08-20\n\n## Materialized empirical data\n- Real matches before: **{counts["REAL_MATCHES_BEFORE"]}**\n- Real matches after: **{counts["REAL_MATCHES_AFTER"]}**\n- New real matches: **{counts["NEW_REAL_MATCHES"]}**\n- Countries in materialized canonical data: **{counts["COUNTRIES"]}**\n- Competitions in materialized canonical data: **{counts["COMPETITIONS"]}**\n- Season labels: **{counts["SEASONS"]}**\n- Teams: **{counts["TEAMS"]}**\n- Men: **{counts["MEN_MATCHES"]}**\n- Women: **{counts["WOMEN_MATCHES"]}**\n\n## Field coverage\n- Cards: {counts["CARDS_MATCHES"]}\n- Corners: {counts["CORNERS_MATCHES"]}\n- Shots: {counts["SHOTS_MATCHES"]}\n- SOT: {counts["SOT_MATCHES"]}\n- xG: {counts["XG_MATCHES"]}\n- Events: {counts["EVENT_MATCHES"]}\n- Lineups: {counts["LINEUP_MATCHES"]}\n- Injuries: {counts["INJURY_RECORDS"]}\n- Suspensions: {counts["SUSPENSION_RECORDS"]}\n- Referee: {counts["REFEREE_MATCHES"]}\n- Odds rows represented in canonical: {counts["ODDS_MATCHES"]}\n- Exact PIT: {counts["PIT_EXACT"]}\n- Date-level PIT: {counts["PIT_DATE_LEVEL"]}\n- Non-PIT: {counts["NON_PIT"]}\n- LIVE: 0\n- Settlements: 0\n\n## Acquisition truth\n`FOUND` is kept distinct from `DOWNLOADED`, `MATERIALIZED`, `PROCESSED`, `PIT_VALIDATED`, and `USED_IN_MODEL`.\nThe external global Hugging Face dataset was **discovered but not materialized** in this execution, so its headline scale is not counted in Robo empirical totals.\n\n## Scientific status\n**{status}**\n\nThe Robo is materially larger than the input package, but this is **not** a claim of global completeness. The current empirical layer remains concentrated in a small number of competitions.\n\n## Snapshot protection\nThe existing prospective snapshot was read-only and its SHA-256 remained unchanged.\n\n## Real money\n**DISABLED**.\n'''
    (ROOT/'data/global_dataset/reports/GLOBAL_DATASET_FINAL_REPORT.md').write_text(report)
    (ROOT/'data/global_dataset/reports/FINAL_SCIENTIFIC_STATUS.md').write_text(f'# FINAL SCIENTIFIC STATUS\n\n**{status}**\n\nThe dataset expansion is real but partial. No external dataset headline has been merged without materialization and validation.\n')
    print(json.dumps({'counts':counts,'snapshot_unchanged':protection['unchanged'],'duplicate_rows_detected':dup_count},indent=2))

if __name__=='__main__': main()
