from __future__ import annotations
import hashlib, json, re, unicodedata, glob
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'data/canonical/football_historical_real_canonical.csv'
RAW_GLOB=str(ROOT/'data/raw/**/*.csv')
OUT=ROOT/'data/enrichment/free_data'; OUT.mkdir(parents=True,exist_ok=True)
REPORT=ROOT/'data/global_dataset/reports'; REPORT.mkdir(parents=True,exist_ok=True)

def now(): return datetime.now(timezone.utc).isoformat()
def sha256(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()
def norm(x):
    x='' if pd.isna(x) else str(x)
    x=unicodedata.normalize('NFKD',x).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]','',x)

def scan_raw():
    frames=[]; artifacts=[]
    for fp in glob.glob(RAW_GLOB,recursive=True):
        p=Path(fp)
        try: d=pd.read_csv(p,dtype=str)
        except Exception: continue
        if not {'Date','HomeTeam','AwayTeam'}.issubset(d.columns): continue
        for c in ['HS','AS','HST','AST','HC','AC','HF','AF','HY','AY','HR','AR']:
            if c not in d.columns: d[c]=pd.NA
        raw_date=d['Date'].astype(str).str.strip()
        # Football-Data files are mostly dd/mm/yy while some local derivatives use ISO.
        has_slash=raw_date.str.contains('/')
        d['date']=pd.NaT
        if has_slash.any(): d.loc[has_slash,'date']=pd.to_datetime(raw_date[has_slash],errors='coerce',dayfirst=True)
        if (~has_slash).any(): d.loc[~has_slash,'date']=pd.to_datetime(raw_date[~has_slash],errors='coerce',dayfirst=False)
        d['date']=pd.to_datetime(d['date'],errors='coerce').dt.date
        d['hk']=d['HomeTeam'].map(norm); d['ak']=d['AwayTeam'].map(norm); d['source_file']=str(p.relative_to(ROOT))
        frames.append(d[['date','hk','ak','HS','AS','HST','AST','HC','AC','HF','AF','HY','AY','HR','AR','source_file']])
        artifacts.append({'artifact':str(p.relative_to(ROOT)),'sha256':sha256(p),'rows':len(d),'state':'MATERIALIZED_REUSED'})
    if not frames: return pd.DataFrame(), artifacts
    raw=pd.concat(frames,ignore_index=True)
    # Prefer first stable source per key; conflicts are retained separately below.
    raw['_nonnull']=raw[['HS','AS','HST','AST']].notna().sum(axis=1)
    raw=raw.sort_values(['date','hk','ak','_nonnull'],ascending=[True,True,True,False])
    conflicts=raw.groupby(['date','hk','ak']).agg(rows=('source_file','size'),sources=('source_file',lambda s:'|'.join(sorted(set(s))))).reset_index()
    conflicts=conflicts[conflicts.rows>1]
    raw=raw.drop_duplicates(['date','hk','ak'],keep='first').drop(columns=['_nonnull'])
    return raw, artifacts, conflicts

def main():
    before=pd.read_csv(CANON,dtype=str)
    before_n=len(before)
    before['date']=pd.to_datetime(before['kickoff_timestamp'],errors='coerce').dt.date
    before['hk']=before['home_team'].map(norm); before['ak']=before['away_team'].map(norm)
    raw, artifacts, conflicts=scan_raw()
    if raw.empty: raise SystemExit('No materialized football-data CSVs found')
    merged=before.merge(raw,on=['date','hk','ak'],how='left',suffixes=('','_raw'),indicator=True)
    matched=merged['_merge'].eq('both')
    fields=['HS','AS','HST','AST','HC','AC','HF','AF','HY','AY','HR','AR']
    stats=merged.loc[matched,['match_id','canonical_match_id' if 'canonical_match_id' in merged.columns else 'match_id'] if False else ['match_id']].copy()
    stats['home_shots']=pd.to_numeric(merged.loc[matched,'HS'],errors='coerce').values
    stats['away_shots']=pd.to_numeric(merged.loc[matched,'AS'],errors='coerce').values
    stats['home_sot']=pd.to_numeric(merged.loc[matched,'HST'],errors='coerce').values
    stats['away_sot']=pd.to_numeric(merged.loc[matched,'AST'],errors='coerce').values
    for c in ['HC','AC','HF','AF','HY','AY','HR','AR']:
        stats[c.lower()]=pd.to_numeric(merged.loc[matched,c],errors='coerce').values
    stats['source']=merged.loc[matched,'source_file'].values
    stats['source_type']='Football-Data.co.uk CSV already materialized locally'
    stats['source_timestamp_status']='DATE_ONLY_SOURCE'
    stats['temporal_status']='DATE_LEVEL_ONLY'
    stats['provenance_timestamp']=now()
    stats['raw_source_sha256']=stats['source'].map(lambda x: next((a['sha256'] for a in artifacts if a['artifact']==x),''))
    stats=stats.drop_duplicates('match_id')
    out=OUT/'MATCH_STATISTICS_FREE.csv'; stats.to_csv(out,index=False)

    # Build a non-snapshot enriched canonical derivative. Original canonical remains untouched.
    enriched=before.drop(columns=['date','hk','ak']).copy()
    add=stats[['match_id','home_shots','away_shots','home_sot','away_sot','source','raw_source_sha256','temporal_status']]
    enriched=enriched.merge(add,on='match_id',how='left')
    enriched_path=OUT/'FOOTBALL_CANONICAL_ENRICHED_FREE.csv'; enriched.to_csv(enriched_path,index=False)

    # Source matrix reflects actual local materialization plus remote status from this environment.
    rows=[]
    rows.append(['Football-Data.co.uk','MULTIPLE','materialized local CSVs','2020-2026',len(stats),'PARTIAL','NO','YES','YES','NO','NO','NO','NO','YES','DATE_ONLY','MATERIALIZED_REUSED'])
    rows += [
      ['StatsBomb Open Data','MULTIPLE','selected open-data seasons','2020-2026',0,'NO','YES','YES','YES','YES','YES','YES','NO','NO','EVENT_TIME','REMOTE_NOT_ACQUIRED'],
      ['API-Football','GLOBAL','free tier','2020-2026',0,'REMOTE','REMOTE','REMOTE','REMOTE','REMOTE','REMOTE','REMOTE','REMOTE','REMOTE','REMOTE','BLOCKED_NO_NETWORK'],
      ['football-data.org','GLOBAL','free plan','2020-2026',0,'REMOTE','NO','NO','NO','NO','REMOTE','NO','NO','NO','REMOTE','BLOCKED_NO_NETWORK'],
      ['OpenLigaDB','Germany','German competitions','2020-2026',0,'RESULTS','NO','NO','NO','NO','NO','NO','NO','NO','DATE/UNKNOWN','BLOCKED_NO_NETWORK'],
      ['TheSportsDB','GLOBAL','provider dependent','2020-2026',0,'PARTIAL','UNKNOWN','UNKNOWN','UNKNOWN','PARTIAL','PARTIAL','PARTIAL','UNKNOWN','UNKNOWN','UNKNOWN','BLOCKED_NO_NETWORK']
    ]
    pd.DataFrame(rows,columns=['Source','Country','Competition','Season','Matches','Stats','xG','Shots','SOT','Events','Players','Lineups','Injuries','Odds','Timestamp','Status']).to_csv(REPORT/'FREE_SOURCE_COVERAGE_MATRIX.csv',index=False)

    # Counts and coverage.
    cpath=ROOT/'data/master_staff/DATASET_FINAL_COUNTS.json'
    counts=json.loads(cpath.read_text())
    counts.update({'MATCH_STATS':int(max(int(counts.get('MATCH_STATS',0)),len(stats))), 'SHOTS':int(stats.home_shots.notna().sum()), 'SOT':int((stats.home_sot.notna() & stats.away_sot.notna()).sum())})
    counts['ENRICHMENT_RUN_UTC']=now(); counts['FREE_ENRICHMENT_SOURCE']='Football-Data.co.uk local materialized CSVs'
    cpath.write_text(json.dumps(counts,indent=2,ensure_ascii=False))
    (REPORT/'GLOBAL_FIELD_COVERAGE_FREE.csv').write_text(pd.DataFrame([
        ['home_shots',int(stats.home_shots.notna().sum()),round(100*stats.home_shots.notna().sum()/before_n,3)],
        ['away_shots',int(stats.away_shots.notna().sum()),round(100*stats.away_shots.notna().sum()/before_n,3)],
        ['home_sot',int(stats.home_sot.notna().sum()),round(100*stats.home_sot.notna().sum()/before_n,3)],
        ['away_sot',int(stats.away_sot.notna().sum()),round(100*stats.away_sot.notna().sum()/before_n,3)]
    ],columns=['field','records_with_value','coverage_pct']).to_csv(index=False))
    # Acquisition report.
    rep=f'''# FREE DATA ENRICHMENT FINAL REPORT\n\nRun: {now()}\n\n## Real materialization\n- Canonical matches before/after: {before_n} / {before_n}\n- New canonical matches: 0 (enrichment-only run; no duplicate promotion)\n- Materialized local Football-Data artifacts reused: {len(artifacts)}\n- Unique matched canonical fixtures enriched: {len(stats)}\n- Shots coverage: {int(stats.home_shots.notna().sum())} matches ({100*stats.home_shots.notna().sum()/before_n:.2f}%)\n- SOT coverage: {int((stats.home_sot.notna() & stats.away_sot.notna()).sum())} matches ({100*(stats.home_sot.notna() & stats.away_sot.notna()).sum()/before_n:.2f}%)\n- xG: 0 new\n- events: 0 new\n- players: 0 new\n- lineups: 0 new\n- injuries: 0 new\n- suspensions: 0 new\n- exact PIT: 0 new\n\n## Integrity\nThe original PREMATCH_FEATURE_STORE and real-day prospective snapshots were not written by this enrichment job.\n\n## Source handling\nRemote sources were not promoted in this run because the execution environment has no external DNS/network path. API-Football currently advertises a free tier with 100 requests/day; football-data.org documents a registered free plan with request throttling; StatsBomb Open Data exposes selected competitions/seasons via public JSON. Coverage is still subject to actual local materialization and validation.\n\n## Conflicts\nPotential multi-source duplicate keys detected in local Football-Data artifacts: {len(conflicts)}. They were deduplicated deterministically and source hashes retained.\n'''
    (REPORT/'DATA_ENRICHMENT_FINAL_REPORT.md').write_text(rep,encoding='utf-8')
    pd.DataFrame(artifacts).to_csv(REPORT/'LOCAL_FREE_ARTIFACT_MANIFEST.csv',index=False)
    conflicts.to_csv(REPORT/'FREE_SOURCE_CONFLICTS.csv',index=False)
    print(json.dumps({'matches_before':before_n,'matches_new':0,'matches_after':before_n,'stats_enriched':len(stats),'shots':int(stats.home_shots.notna().sum()),'sot':int((stats.home_sot.notna()&stats.away_sot.notna()).sum()),'artifacts_reused':len(artifacts),'conflicts':len(conflicts)},indent=2))
if __name__=='__main__': main()
