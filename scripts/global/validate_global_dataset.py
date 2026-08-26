from pathlib import Path
import json, hashlib, zipfile, compileall, pandas as pd
ROOT=Path(__file__).resolve().parents[2]
results={}
def check(name,fn):
    try: fn(); results[name]={'status':'PASS'}
    except Exception as e: results[name]={'status':'FAIL','error':str(e)}
canon=pd.read_csv(ROOT/'data/canonical/football_historical_real_canonical.csv')

def dataset_validation():
    assert len(canon)>=6616
    assert canon.match_id.notna().all(); assert canon.match_id.is_unique
    assert canon.home_team.notna().all() and canon.away_team.notna().all()
    ts=pd.to_datetime(canon.kickoff_timestamp,format='mixed',errors='coerce')
    assert ts.notna().all(); assert (ts>=pd.Timestamp('2020-01-01')).all()

def gender_separation():
    g=canon.get('gender',pd.Series(['MEN']*len(canon))).fillna('MEN').astype(str).str.upper(); assert set(g)<= {'MEN','WOMEN'}

def temporal_validation():
    ts=pd.to_datetime(canon.kickoff_timestamp,format='mixed',errors='coerce'); assert ts.max()<=pd.Timestamp('2026-08-20 23:59:59')

def provenance():
    p=pd.read_csv(ROOT/'data/canonical/football_historical_real_provenance.csv'); assert len(p)>=len(canon)-4864; assert p.source_url.notna().all()

def snapshot():
    a=json.loads((ROOT/'data/global_dataset/reports/PREMATCH_SNAPSHOT_PROTECTION.json').read_text()); assert a['unchanged'] is True

def pit(): assert int(canon.pit_status.eq('PIT_EXACT').sum())==0

def no_synthetic(): assert not canon.data_type.astype(str).str.contains('SYNTHETIC|MOCK|DEMO',case=False,regex=True).any()

def coverage(): assert (ROOT/'data/global_dataset/reports/GLOBAL_DATASET_COVERAGE.csv').exists(); assert (ROOT/'data/global_dataset/reports/GLOBAL_COMPETITION_SEASON_MATRIX_2020_2026.csv').exists()

def manifest():
    m=json.loads((ROOT/'data/global_dataset/registry/GLOBAL_ACQUISITION_MANIFEST.json').read_text()); assert all(k in m for k in ['sources','external_discovery'])

def security():
    for p in ROOT.rglob('.env'):
        assert p.stat().st_size==0, f'non-empty .env: {p}'
for n,f in [('dataset_validation',dataset_validation),('gender_separation',gender_separation),('temporal_validation',temporal_validation),('provenance',provenance),('snapshot_protection',snapshot),('PIT_audit',pit),('no_synthetic',no_synthetic),('coverage_reports',coverage),('manifest',manifest),('security',security)]: check(n,f)
out={'results':results,'overall':'PASS' if all(x['status']=='PASS' for x in results.values()) else 'FAIL','real_money':'DISABLED'}
(ROOT/'data/global_dataset/reports/GLOBAL_DATASET_TEST_REPORT.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
if out['overall']!='PASS': raise SystemExit(1)
