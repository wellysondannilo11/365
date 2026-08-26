from __future__ import annotations
import pandas as pd


def require_strict_pit_odds(df: pd.DataFrame) -> None:
    required={'event_id','bookmaker','market','selection','price','captured_at','available_at','source_timestamp'}
    missing=required-set(df.columns)
    if missing: raise ValueError(f'STRICT_PIT_ODDS_MISSING_COLUMNS:{sorted(missing)}')
    for c in ('captured_at','available_at','source_timestamp'):
        d=pd.to_datetime(df[c],utc=True,errors='coerce')
        if d.isna().any(): raise ValueError(f'STRICT_PIT_ODDS_INVALID_TIMESTAMP:{c}')
    if (pd.to_datetime(df['available_at'],utc=True) > pd.to_datetime(df['captured_at'],utc=True)).any():
        raise ValueError('STRICT_PIT_ODDS_AVAILABLE_AFTER_CAPTURE')
    if (pd.to_numeric(df['price'],errors='coerce') <= 1).any() or pd.to_numeric(df['price'],errors='coerce').isna().any():
        raise ValueError('STRICT_PIT_ODDS_INVALID_PRICE')
    if 'availability_evidence' in df.columns:
        bad=df['availability_evidence'].astype(str).str.upper().str.contains('NO_EXACT_TIMESTAMP|EVENT_LEVEL_SOURCE_ONLY',regex=True)
        if bad.any(): raise ValueError('STRICT_PIT_ODDS_UNDEFENDED_AVAILABILITY')


def assert_no_future(df: pd.DataFrame, available='available_at', decision='decision_time') -> None:
    a=pd.to_datetime(df[available],utc=True,errors='coerce'); d=pd.to_datetime(df[decision],utc=True,errors='coerce')
    if a.isna().any() or d.isna().any(): raise ValueError('INVALID_PIT_TIMESTAMP')
    if (a>d).any(): raise ValueError('POINT_IN_TIME_VIOLATION')
