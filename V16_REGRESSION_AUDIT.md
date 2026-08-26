# ROBO DA BET V16 — V15 → V16 REGRESSION AUDIT

## Findings and corrections

| Area | Finding | Severity | Status |
|---|---|---:|---|
| Docker Compose | `environment: POSTGRES_DB: robobet` was invalid YAML | P1 | FIXED |
| Frontend | UI still displayed V14.1 | P1 | FIXED to V16 |
| TheStatsAPI adapter | Existing paths were generic/older and did not align with documented match endpoints | P1 | FIXED |
| Raw ingestion | `available_at` could fall back to current time in `research/raw.py` | P0 quantitative | FIXED: provider timestamps required |
| The Odds API normalizer | Inner market/bookmaker update clocks were conflated with snapshot availability | P0 quantitative | FIXED: snapshot + inner clocks preserved separately |
| API security | No configurable API-key gate | P1 security | FIXED with optional `ROBO_API_KEY` in ML and backend |
| V15 event atomicity | Must remain atomic | P0 | VERIFIED by regression suite |
| V15 PIT | `available_at <= decision_time` | P0 | VERIFIED |
| V15 holdout isolation | Holdout remains locked | P0 | VERIFIED |
| V15 cluster bootstrap | Event-level clustering remains | P1 | VERIFIED |
| V15 ROI semantics | Stake-based ROI remains | P1 | VERIFIED |

## Independent conclusion

The V16 audit found real regressions/risks that were corrected before release. The final Python suite passes after the corrections.
