# ROBO DA BET — PHASE 2 EXECUTION

This package update is the empirical football run over every historical-real dataset currently materialized in the supplied artifact.

## Real data processed
- 30 EPL matches (2023/24) with scores, referee, shots, fouls, corners and cards.
- 10 EPL matches (2025/26) with 1X2 prices/results.
- Total: 40 historical-real matches.

## What was executed
- source hashes and provenance;
- data quality checks;
- strict prior-calendar-date feature construction;
- temporal OOS split;
- locked holdout;
- 1X2 market-only baseline;
- temporal logistic model;
- feature ablation;
- card totals Poisson vs Negative Binomial;
- threshold sensitivity;
- scientific status report.

## What was not claimed
Decision-time odds, CLV, historical Robo BET/NO_BET/WATCH/WAIT signals, Asian Handicap, BTTS/Totals betting ROI, repeated walk-forward, or persistent edge were not fabricated because the materialized real bytes do not contain the required synchronized PIT odds/market snapshots.

## Expansion blocker
The runtime container still cannot resolve external hosts. Public sources were independently verified through web retrieval, but their bytes could not be transferred into the container during this run. Existing real data was therefore preserved and fully processed rather than replaced with synthetic data.

## Money
`REAL_MONEY = DISABLED`
