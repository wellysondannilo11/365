import json, subprocess, sys
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def test_free_enrichment_artifact_has_real_stats():
    p=ROOT/'data/enrichment/free_data/MATCH_STATISTICS_FREE.csv'
    assert p.exists()
    d=pd.read_csv(p)
    assert len(d)==5160
    assert d.home_shots.notna().all()
    assert d.away_sot.notna().all()
    assert d.temporal_status.eq('DATE_LEVEL_ONLY').all()
    assert d.raw_source_sha256.str.len().eq(64).all()

def test_free_source_registry_is_explicit_and_no_keys():
    r=json.loads((ROOT/'config/free_source_registry.json').read_text())
    assert r['real_money']=='DISABLED'
    assert all('key' not in s for s in r['sources'])

def test_snapshot_integrity_passes():
    out=subprocess.run([sys.executable,str(ROOT/'scripts/global/verify_snapshot_integrity.py')],capture_output=True,text=True)
    assert out.returncode==0
    assert '"status": "PASS"' in out.stdout
