from __future__ import annotations

from dataclasses import asdict
from typing import Iterable
import pandas as pd

from .pricing import Dislocation, market_dislocation


def normalize_market_rows(rows: Iterable[dict] | pd.DataFrame, strict_pit: bool = False) -> pd.DataFrame:
    d = rows.copy() if isinstance(rows, pd.DataFrame) else pd.DataFrame(list(rows))
    if 'odds' not in d.columns and 'price' in d.columns:
        d['odds'] = d['price']
    required = {'event_id', 'bookmaker', 'market', 'selection', 'odds'}
    missing = required - set(d.columns)
    if missing:
        raise ValueError(f'MISSING_MARKET_COLUMNS:{sorted(missing)}')
    for c in ('available_at', 'source_timestamp', 'snapshot_timestamp', 'ingestion_time'):
        if c in d.columns:
            d[c] = pd.to_datetime(d[c], utc=True, errors='coerce')
    d['odds'] = pd.to_numeric(d['odds'], errors='coerce')
    if d['odds'].isna().any() or (d['odds'] <= 1).any():
        raise ValueError('INVALID_MARKET_ODDS')
    if strict_pit:
        if 'available_at' not in d.columns or 'source_timestamp' not in d.columns:
            raise ValueError('STRICT_PIT_MARKET_REQUIRES_AVAILABILITY_AND_SOURCE_TIMESTAMP')
        if d['available_at'].isna().any() or d['source_timestamp'].isna().any():
            raise ValueError('STRICT_PIT_MARKET_INVALID_TIMESTAMP')
    return d


def de_vig_market(rows: pd.DataFrame) -> pd.DataFrame:
    d = rows.copy()
    d['implied_probability'] = 1.0 / d['odds']
    d['overround'] = d.groupby(['event_id', 'bookmaker', 'market', 'line'] if 'line' in d.columns else ['event_id', 'bookmaker', 'market'])['implied_probability'].transform('sum') - 1.0
    d['fair_market_probability'] = d['implied_probability'] / (1.0 + d['overround'])
    return d


def consensus_probability(rows: pd.DataFrame) -> pd.DataFrame:
    d = de_vig_market(rows)
    keys = ['event_id', 'market', 'selection'] + (['line'] if 'line' in d.columns else [])
    out = d.groupby(keys, dropna=False).agg(
        consensus_probability=('fair_market_probability', 'mean'),
        best_odds=('odds', 'max'),
        bookmaker_count=('bookmaker', 'nunique'),
        source_count=('source', 'nunique') if 'source' in d.columns else ('bookmaker', 'nunique'),
    ).reset_index()
    return out


def discover_dislocations(
    model_rows: Iterable[dict],
    market_rows: Iterable[dict] | pd.DataFrame,
    strict_pit: bool = False,
    decision_time=None,
) -> list[dict]:
    m = pd.DataFrame(list(model_rows))
    if not {'event_id', 'market', 'selection', 'probability'}.issubset(m.columns):
        raise ValueError('MISSING_MODEL_PRICING_COLUMNS')
    o = normalize_market_rows(market_rows, strict_pit=strict_pit)
    if decision_time is not None:
        if 'available_at' not in o.columns:
            raise ValueError('MARKET_AVAILABLE_AT_REQUIRED_FOR_DECISION_TIME')
        t = pd.Timestamp(decision_time)
        if t.tzinfo is None:
            t = t.tz_localize('UTC')
        else:
            t = t.tz_convert('UTC')
        o = o[o['available_at'] <= t].copy()
    if 'line' not in m.columns:
        m['line'] = None
    if 'line' not in o.columns:
        o['line'] = None
    joined = o.merge(m[['event_id', 'market', 'selection', 'line', 'probability']], on=['event_id', 'market', 'selection', 'line'], how='inner')
    results: list[dict] = []
    for _, r in joined.iterrows():
        x = market_dislocation(float(r.probability), float(r.odds), market=r.market, selection=r.selection, line=None if pd.isna(r.line) else float(r.line), source=r.get('source'))
        results.append(asdict(x))
    return sorted(results, key=lambda x: x['ev'] if x['ev'] is not None else float('-inf'), reverse=True)
