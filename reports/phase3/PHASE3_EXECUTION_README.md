# PHASE 3 EXECUTION README

This update preserves the existing Robo architecture and operates on the latest consolidated package. It adds empirical research artifacts under `reports/phase3/` and `data/model/phase3_*`.

## Executed
- ZIP integrity/SHA-256 check
- Full existing pytest suite
- Source discovery via web research
- Real-data quality checks
- Temporal feature construction with strict prior-date PIT
- Market-only 1X2 baseline
- Naive/logistic/random-forest/gradient-boosting comparison on the binary home-win research target
- Card totals Poisson vs Negative Binomial comparison
- Feature ablation
- Odds-threshold sensitivity on the real 10-row pilot
- Holdout lock discipline
- Research candidate/data-gap inventory

## Not executed as empirical performance claims
- Global league backtests beyond EPL: no real bytes were materialized for them.
- Full Robo BET/NO_BET/WATCH/WAIT reconstruction: missing decision-time odds linkage.
- CLV: missing decision and closing timestamps.
- Meaningful walk-forward: N=30 stats sample is too small.
- Multiple-testing significance correction: no formal hypothesis-testing campaign was run; exploratory comparisons are not promoted.

## Real money
`DISABLED`.
