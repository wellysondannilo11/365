# V24 REAL FEED REPORT

## Status

**BLOCKED — CREDENTIAL REQUIRED**

`THE_ODDS_API_KEY` was not present in the execution environment.

Therefore:
- no real request was made;
- no real odds were claimed;
- no real timestamps were claimed;
- no real events were counted;
- no real P/L/ROI/CLV was generated.

The adapter is implemented and hardened for authentication, timeout, transient retry, rate-limit metadata, malformed/error responses and source timestamps.

When credentials are supplied, use:
`PYTHONPATH=ml python ml/scripts/run_v24_observation.py --mode SHADOW`
or `--mode PAPER`.
