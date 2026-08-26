# V15 Regression Audit

## Scope

Independent review of V14.2 → V15 across API, backend, database contracts, adapters, PIT, leakage, temporal validation, backtest, tests, configuration and build packaging.

## Findings

| Area | Finding | Severity | Action |
|---|---|---:|---|
| Temporal split | Multi-row events could be split by row-index boundaries | P0 quantitative | Fixed: event groups are atomic |
| Holdout | Holdout sizing was row-based | P0 quantitative | Fixed: unique-event sizing |
| Backtest metrics | `roi` was bankroll return while `yield` was stake ROI | P1 quantitative | Fixed: ROI = profit / stake; bankroll_return separate |
| Backend Docker | Dockerfile copied stale/missing 10.0.0 JAR | P1 engineering | Fixed with multi-stage Maven build |
| Versioning | API/backend exposed older version | P1 engineering | Fixed to 15.0.0 |
| Historical odds | Provider snapshot normalization was incomplete | P1 data | Fixed with strict timestamp-preserving normalizer |
| PIT | Row-level price/odds values were incorrectly exposed to feature-level availability checks | P1 data | Fixed: row-level PIT columns use record availability clock |
| Authentication | Research/control endpoints have no auth layer | P1 security | Not silently changed; remains production gate |
| Frontend build | Dependencies could not be installed in current environment | P2 validation | Documented; no functional code replacement made |

## Regression conclusion

No failing Python regression was left unresolved. The major quantitative regressions found during the audit were corrected and the full Python test suite passed.
