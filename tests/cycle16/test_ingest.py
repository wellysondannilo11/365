from pathlib import Path
import pandas as pd
from ml.app.cycle16.ingest import normalize_csv, sha256_file, inspect_zip

def test_normalize_csv_uses_immutable_file_hash(tmp_path):
    p=tmp_path/'sharp.csv'
    pd.DataFrame([{'id':'1','sportsbook':'bet365','event_id':'e1','market_type':'moneyline','selection':'A','odds_decimal':2.1,'event_start_time':'2026-08-25T20:00:00Z','timestamp':'2026-08-25T18:00:00Z'}]).to_csv(p,index=False)
    out=normalize_csv(p,chunksize=1)
    assert out.loc[0,'raw_hash']==sha256_file(p)
    assert out.loc[0,'provenance'].startswith('file:sharp.csv:')
