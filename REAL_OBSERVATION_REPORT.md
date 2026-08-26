# REAL_OBSERVATION_REPORT

## Materialized observations
- Odds pilot: 10 EPL 2025/26 matches.
- Match-statistics/card pilot: 30 EPL 2023/24 matches.

## What was actually observed
The runtime successfully loaded real football observations that are distinct from the package's DEMO fixture. Data quality checks passed on both pilots. A 1X2 market-only descriptive calculation was executed on the 10-match odds pilot.

## What was not observed
The current Robo's full historical decision distribution could not be scientifically characterized because the available materialized odds pilot lacks the historical feature inputs and timestamped PIT price stream required by the strict research path.

## Status
`REAL_DATA_OBSERVATION = PASS`
`FULL_EMPIRICAL_ROBO_OBSERVATION = NOT_DETERMINED`
