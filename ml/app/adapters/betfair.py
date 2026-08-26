from __future__ import annotations
import gzip
from pathlib import Path
import pandas as pd

class BetfairHistoricalAdapter:
    """Local loader for purchased Betfair Historical Data extracts.

    No credentials or downloads are performed automatically. The parser preserves
    source timestamps; provider-specific normalization must be mapped to the
    canonical odds schema before strict PIT validation.
    """
    name='betfair-historical'
    def read_tabular(self,path):
        p=Path(path)
        if p.suffix=='.gz':
            with gzip.open(p,'rb') as f: return pd.read_csv(f)
        if p.suffix.lower()=='.csv': return pd.read_csv(p)
        if p.suffix.lower()=='.parquet': return pd.read_parquet(p)
        raise ValueError(f'UNSUPPORTED_BETFAIR_FORMAT:{p.suffix}')
