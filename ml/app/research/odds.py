from __future__ import annotations
import hashlib
import json
import pandas as pd

REQUIRED = ['event_id','bookmaker','market','selection','price','captured_at']

def _line_key(df):
    return 'line' if 'line' in df.columns else None

def normalize_odds(df, strict_pit=False):
    d = df.copy()
    missing = [c for c in REQUIRED if c not in d.columns]
    if missing: raise ValueError(f'MISSING_ODDS_COLUMNS:{missing}')
    d['captured_at'] = pd.to_datetime(d['captured_at'], utc=True, errors='coerce')
    if d['captured_at'].isna().any(): raise ValueError('INVALID_ODDS_TIMESTAMP')
    d['price'] = pd.to_numeric(d['price'], errors='coerce')
    if d['price'].isna().any() or (d['price'] <= 1).any(): raise ValueError('INVALID_ODDS')
    if strict_pit and 'available_at' not in d.columns:
        raise ValueError('STRICT_PIT_ODDS_REQUIRES_AVAILABLE_AT')
    if strict_pit and 'source_timestamp' not in d.columns:
        raise ValueError('STRICT_PIT_ODDS_REQUIRES_SOURCE_TIMESTAMP')
    d['available_at'] = pd.to_datetime(d.get('available_at', d['captured_at']), utc=True, errors='coerce')
    d['source_timestamp'] = pd.to_datetime(d.get('source_timestamp', d['captured_at']), utc=True, errors='coerce')
    if d['available_at'].isna().any() or d['source_timestamp'].isna().any(): raise ValueError('INVALID_ODDS_TIMESTAMP')
    if strict_pit and 'availability_evidence' in d.columns and d['availability_evidence'].astype(str).str.upper().str.contains('NO_EXACT_TIMESTAMP|EVENT_LEVEL_SOURCE_ONLY', regex=True).any():
        raise ValueError('STRICT_PIT_UNDEFENDED_AVAILABILITY')
    if (d['available_at'] > d['captured_at']).any():
        raise ValueError('AVAILABLE_AFTER_CAPTURED')
    if 'source' not in d: d['source'] = 'unknown'
    if 'source_record_id' not in d:
        d['source_record_id'] = [hashlib.sha256(json.dumps(r.to_dict(), sort_keys=True, default=str).encode()).hexdigest()[:24] for _, r in d.iterrows()]
    if 'raw_hash' not in d:
        d['raw_hash'] = d['source_record_id']
    if 'line' not in d: d['line'] = None
    d['line'] = pd.to_numeric(d['line'], errors='coerce')
    return d.sort_values(['event_id','market','line','captured_at','bookmaker','selection'], kind='stable').reset_index(drop=True)

def snapshot_at_or_before(df, event_id, decision_time, market=None, max_staleness_seconds=None):
    d = normalize_odds(df)
    t = pd.Timestamp(decision_time)
    if t.tzinfo is None: t = t.tz_localize('UTC')
    else: t = t.tz_convert('UTC')
    d = d[(d.event_id.astype(str) == str(event_id)) & (d.available_at <= t)]
    if market: d = d[d.market == market]
    if d.empty: return d
    d = d.sort_values('captured_at').groupby(['bookmaker','market','line','selection'], dropna=False).tail(1).copy()
    d['stale_seconds'] = (t - d['captured_at']).dt.total_seconds()
    if max_staleness_seconds is not None:
        d = d[d['stale_seconds'] <= float(max_staleness_seconds)]
    return d.reset_index(drop=True)

def select_opening_snapshot(df, event_id):
    d = normalize_odds(df)
    d = d[d.event_id.astype(str) == str(event_id)].sort_values('captured_at')
    if d.empty: return d
    return d.groupby(['bookmaker','market','line','selection'], dropna=False).head(1).reset_index(drop=True)

def select_closing_snapshot(df, event_id):
    d = normalize_odds(df)
    d = d[d.event_id.astype(str) == str(event_id)].sort_values('captured_at')
    if d.empty: return d
    return d.groupby(['bookmaker','market','line','selection'], dropna=False).tail(1).reset_index(drop=True)
