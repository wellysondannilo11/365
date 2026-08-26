# Release V25

V25 consolidates the existing Robo da Bet architecture without replacing V20–V24.

## Start PAPER/SHADOW observation

```bash
PYTHONPATH=ml python ml/scripts/run_v25_observation.py --mode SHADOW
```

Requires `THE_ODDS_API_KEY` for real feed access.

## API highlights

- `/v25/status`
- `/v25/infra/health`
- `/v25/feed/poll`
- `/v25/session/scan`
- `/v25/market/analyze`
- `/v25/live/reprice`
- `/v25/live/snapshot`
- `/v25/position/reassess`
- `/v25/position/settle`
- `/v25/position/reversal`
- `/v25/watchlist`
- `/v25/export/xlsx`
- `/v25/hash-chain`

## Real-money policy

Disabled by design.
