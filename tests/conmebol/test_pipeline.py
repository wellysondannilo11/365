from pathlib import Path
import pandas as pd
from ml.app.conmebol.pipeline import parse_sudamericana_txt, canonical_id

def test_sudamericana_real_parser_has_no_synthetic_rows():
    p=Path('data/raw/conmebol_sudamericana_2020.txt')
    df=parse_sudamericana_txt(p,2020)
    assert len(df)>100
    assert set(df.data_type)=={'HISTORICAL_REAL'}
    assert not df.home_team.str.contains('N.N.',na=False).any()

def test_canonical_id_stable():
    a=canonical_id('Copa Sudamericana',2020,'2020-02-04','Coquimbo','Aragua')
    b=canonical_id('Copa Sudamericana',2020,'2020-02-04','Coquimbo','Aragua')
    assert a==b
