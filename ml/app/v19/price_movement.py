from __future__ import annotations

import pandas as pd


def build_price_timeline(rows, decision_time=None, strict_pit=False):
    d = rows.copy() if isinstance(rows, pd.DataFrame) else pd.DataFrame(list(rows))
    required = {'event_id','market','selection','odds'}
    if not required.issubset(d.columns):
        raise ValueError(f'MISSING_PRICE_MOVEMENT_COLUMNS:{sorted(required-set(d.columns))}')
    ts = 'available_at' if 'available_at' in d.columns else 'captured_at' if 'captured_at' in d.columns else None
    if ts is None:
        raise ValueError('PRICE_MOVEMENT_REQUIRES_TEMPORAL_TIMESTAMP')
    d[ts] = pd.to_datetime(d[ts], utc=True, errors='coerce')
    if d[ts].isna().any():
        raise ValueError('INVALID_PRICE_MOVEMENT_TIMESTAMP')
    d['odds'] = pd.to_numeric(d['odds'], errors='coerce')
    if d['odds'].isna().any() or (d['odds'] <= 1).any():
        raise ValueError('INVALID_PRICE_MOVEMENT_ODDS')
    if strict_pit and 'available_at' not in d.columns:
        raise ValueError('STRICT_PIT_PRICE_MOVEMENT_REQUIRES_AVAILABLE_AT')
    if decision_time is not None:
        t = pd.Timestamp(decision_time)
        if t.tzinfo is None: t = t.tz_localize('UTC')
        else: t = t.tz_convert('UTC')
        d = d[d[ts] <= t].copy()
    d = d.sort_values(['event_id','market','selection',ts,'bookmaker' if 'bookmaker' in d else ts], kind='stable')
    keys = ['event_id','market','selection'] + (['line'] if 'line' in d.columns else []) + (['bookmaker'] if 'bookmaker' in d.columns else [])
    rows_out=[]
    for key, g in d.groupby(keys, dropna=False):
        g=g.sort_values(ts)
        first=float(g.iloc[0].odds); last=float(g.iloc[-1].odds)
        min_o=float(g.odds.min()); max_o=float(g.odds.max())
        rows_out.append({
            'key': key,
            'opening_price': first,
            'current_price': last,
            'minimum_price': min_o,
            'maximum_price': max_o,
            'movement': last-first,
            'movement_percentage': last/first-1,
            'snapshots': int(len(g)),
            'first_timestamp': g.iloc[0][ts].isoformat(),
            'last_timestamp': g.iloc[-1][ts].isoformat(),
        })
    return rows_out


def clv(entry_odds: float, closing_odds: float) -> float | None:
    if entry_odds <= 1 or closing_odds <= 1:
        return None
    return entry_odds / closing_odds - 1.0
