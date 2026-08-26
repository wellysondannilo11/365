from __future__ import annotations

import pandas as pd


def summarize_market_efficiency(df: pd.DataFrame) -> pd.DataFrame:
    required={'market','result','odds','probability'}
    missing=required-set(df.columns)
    if missing: raise ValueError(f'MISSING_MARKET_EFFICIENCY_COLUMNS:{sorted(missing)}')
    d=df.copy()
    d['profit']=d['result'].astype(float)*d['odds'].astype(float)-1.0
    d['brier']=(d['probability'].astype(float)-d['result'].astype(float))**2
    d['log_loss']=-(
        d['result'].astype(float)*d['probability'].astype(float).clip(1e-12,1-1e-12).apply(__import__('math').log)
        +(1-d['result'].astype(float))*(1-d['probability'].astype(float)).clip(1e-12,1-1e-12).apply(__import__('math').log)
    )
    return d.groupby('market').agg(sample_size=('result','size'), roi=('profit','mean'), brier=('brier','mean'), log_loss=('log_loss','mean')).reset_index()
