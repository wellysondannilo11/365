#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/epl_2025_2026_web_verified_pilot.csv'
OUT = ROOT / 'reports/real_data_pilot'
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(RAW)
required = {'date','home_team','away_team','result_code','home_odds','draw_odds','away_odds','result_odds'}
missing = sorted(required - set(df.columns))
if missing:
    raise SystemExit(f'MISSING_COLUMNS:{missing}')

for c in ['home_odds','draw_odds','away_odds','result_odds']:
    df[c] = pd.to_numeric(df[c], errors='coerce')

quality = {
    'raw_rows': int(len(df)),
    'duplicate_rows': int(df.duplicated().sum()),
    'duplicate_match_keys': int(df[['date','home_team','away_team']].duplicated().sum()),
    'missing_values': {k:int(v) for k,v in df.isna().sum().items() if int(v)},
    'invalid_odds': int((df[['home_odds','draw_odds','away_odds','result_odds']] <= 1).sum().sum() + df[['home_odds','draw_odds','away_odds','result_odds']].isna().sum().sum()),
    'invalid_results': int((~df.result_code.isin([0,1,3])).sum()),
    'pit_status': 'PIT_UNCERTAIN',
    'pit_reason': 'Source exposes match date and prices but no decision-time timestamp for the quoted prices.',
}
quality['status'] = 'PASS' if not any([quality['duplicate_rows'], quality['duplicate_match_keys'], quality['invalid_odds'], quality['invalid_results'], quality['missing_values']]) else 'FAIL'

# Market-only 1X2 baseline: normalize implied probabilities to remove overround.
inv = 1.0 / df[['home_odds','draw_odds','away_odds']]
probs = inv.div(inv.sum(axis=1), axis=0)
actual = df.result_code.map({3:0,1:1,0:2}).astype(int).to_numpy()
Y = pd.get_dummies(pd.Series(actual), dtype=float).reindex(columns=[0,1,2], fill_value=0).to_numpy()
P = probs.to_numpy()
logloss = float(-sum(math.log(max(P[i, actual[i]], 1e-15)) for i in range(len(df))) / len(df))
brier = float(((P - Y) ** 2).sum(axis=1).mean())

favorite_cols = probs.idxmax(axis=1).tolist()
map_col = {'home_odds': (3,'home_odds'), 'draw_odds': (1,'draw_odds'), 'away_odds': (0,'away_odds')}
pnl = []
for i, col in enumerate(favorite_cols):
    pick, odd_col = map_col[col]
    odd = float(df.iloc[i][odd_col])
    pnl.append(odd - 1.0 if int(df.iloc[i].result_code) == pick else -1.0)

market = {
    'market': '1X2_MARKET_ONLY',
    'n': int(len(df)),
    'log_loss': logloss,
    'brier_multiclass': brier,
    'favorite_strategy_bets': int(len(pnl)),
    'favorite_strategy_wins': int(sum(x > 0 for x in pnl)),
    'favorite_strategy_pnl_1u': float(sum(pnl)),
    'favorite_strategy_roi': float(sum(pnl) / len(pnl)),
    'clv': 'NOT_DETERMINED',
    'reason_clv': 'No timestamped closing/decision-price sequence is present in the materialized source subset.',
}

manifest = {
    'dataset': RAW.name,
    'source_url': str(df.source_url.iloc[0]),
    'source_type': str(df.source_type.iloc[0]),
    'source_hash_sha256': hashlib.sha256(RAW.read_bytes()).hexdigest(),
    'rows': int(len(df)),
    'time_start': str(df.date.min()),
    'time_end': str(df.date.max()),
    'league': 'English Premier League',
    'season': '2025-26',
    'status': 'HISTORICAL_REAL_PILOT',
    'scientific_use': 'PILOT_ONLY_INSUFFICIENT_SAMPLE',
}

(OUT/'DATASET_MANIFEST.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
(OUT/'DATA_QUALITY.json').write_text(json.dumps(quality, indent=2, ensure_ascii=False), encoding='utf-8')
(OUT/'MARKET_ONLY_1X2.json').write_text(json.dumps(market, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps({'manifest':manifest,'quality':quality,'market':market}, indent=2, ensure_ascii=False))
