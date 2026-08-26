import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_v5_registry_has_no_secrets():
 r=json.loads((ROOT/'config/free_source_registry_v5.json').read_text())
 assert r['real_money']=='DISABLED'
 text=(ROOT/'config/free_source_registry_v5.json').read_text().lower()
 assert 'api_key=' not in text
def test_v5_counts_match_materialized_stats():
 import pandas as pd
 d=pd.read_csv(ROOT/'data/enrichment/free_data/MATCH_STATISTICS_FREE.csv')
 assert len(d)==5160
 assert d[['home_shots','away_shots','home_sot','away_sot']].notna().all().all()
def test_v5_runner_preserves_snapshots():
 before={p:__import__('hashlib').sha256((ROOT/p).read_bytes()).hexdigest() for p in ['data/master_staff/PREMATCH_FEATURE_STORE.csv','data/real_day_prematch/REAL_DAY_PREMATCH_SNAPSHOT.json','data/real_day_prematch/REAL_DAY_FEATURES.csv']}
 subprocess.run([sys.executable,str(ROOT/'scripts/v5/run_v5_discovery.py')],check=True,capture_output=True)
 after={p:__import__('hashlib').sha256((ROOT/p).read_bytes()).hexdigest() for p in before}
 assert before==after
