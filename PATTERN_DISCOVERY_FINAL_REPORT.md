# PATTERN DISCOVERY FINAL REPORT

## Scientific status
- REAL_MONEY = DISABLED
- No new external real data were acquired in this execution because outbound network/DNS was unavailable in the execution environment.
- The phase therefore operated on the complete latest real ZIP and its already-materialized real datasets.

## Audited sample
- 3,694 real historical matches
- England, Germany, Italy
- 6 competitions
- 9 competition-season pairs
- seasons 2023-24, 2024-25, 2025-26
- 2020-01-01 was the requested primary window, but the materialized dataset starts 2023-08-11; no earlier records were fabricated.

## Main empirical signals
1. Pre-match rolling attack strength advantage for the home team was associated with a higher home-win rate and replicated with the same sign in holdout.
2. Lower recent goals-against for the home team relative to the away team showed a similar association and replicated in holdout.
3. High recent home shot volume showed a positive home-win association and replicated in holdout.
4. High recent away shot volume had a positive away-win association in discovery and the same sign in holdout, but the holdout effect was materially smaller.
5. Second-division matches showed lower mean total goals than the rest of the sample and this sign replicated in holdout.
6. A fourth-division total-goals pattern did not replicate in holdout and is therefore rejected as a robust pattern.

These are research patterns, not betting edges. They were not tested with exact PIT odds and must not be interpreted as profitable strategies.

## What was not validated
- Player impact: INSUFFICIENT_DATA
- Injury-return effect: INSUFFICIENT_DATA
- Objective motivation/must-win: INSUFFICIENT_DATA
- Derby/rivalry: INSUFFICIENT_DATA
- Historical LIVE: INSUFFICIENT_DATA
- xG: INSUFFICIENT_DATA
- Exact PIT odds / CLV: NOT_DETERMINED

## OOS / walk-forward
A chronological validation and four expanding-window walk-forward folds were executed. Holdout model performance is reported in `data/research/PATTERN_DISCOVERY_OOS.csv` and `PATTERN_DISCOVERY_WALK_FORWARD.csv`.

## Multiple testing
A pre-registered segment grid across competitions, seasons and divisions was evaluated and Benjamini-Hochberg FDR correction was applied. Significant descriptive results remain hypotheses until further independent replication.

## Verdict
`EDGE NOT DETERMINED`.
