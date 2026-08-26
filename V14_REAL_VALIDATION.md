# V14 Real Validation Status

## Data status

`HISTORICAL_DATA = NOT AVAILABLE IN RUNTIME`

The only bundled dataset is `data.csv`, containing 7 demo rows. It is retained for smoke tests only.

## Why no real backtest is reported

A valid betting backtest requires real historical outcomes plus real historical prices that were available at the decision timestamp. The bundle does not contain timestamped historical odds. Current-odds adapters cannot be substituted for historical snapshots.

## What is now executable when a real dataset is supplied

1. CSV/JSON/Parquet ingestion.
2. Immutable raw hashing/deduplication.
3. Strict timestamp validation.
4. Feature-level PIT validation.
5. Historical prior-only feature construction.
6. Historical odds snapshot selection.
7. Per-bookmaker de-vig and consensus.
8. Temporal train/validation/test/holdout splitting.
9. Calibration reporting.
10. Backtest and bankroll simulation.
11. Statistical bootstrap utilities.
12. Experiment and reproducibility manifests.
13. Research API status and dataset endpoints.

## Validation gate

The system must not label a dataset as serious training data unless it contains the required point-in-time timestamps. Datasets with a future feature timestamp are rejected.

## Result

`PROFITABILITY = NOT AVAILABLE`

`MODEL VALIDATION = NOT VALIDATED`

`OOS VALIDATION = NOT AVAILABLE`

`HOLDOUT = LOCKED / NOT EVALUATED`
