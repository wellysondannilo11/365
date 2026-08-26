# GLOBAL DATASET 2020–2026 — MASTER STAFF EXECUTION

## Scope
This package is the direct evolution of the latest Library ZIP `ROBO_DA_BET_MASTER_STAFF_CONTEXT_TRANSFER.zip`.

No new V-number was created. Existing architecture, historical data and prospective snapshots were preserved.

## Input integrity
- Input ZIP: `ROBO_DA_BET_MASTER_STAFF_CONTEXT_TRANSFER.zip`
- Input SHA-256: `acbcfb9c7df41e1deed35c78df9f18490bbd0a733a38e65d89c9f915d4e2d777`
- Input size: `3,126,471 bytes`

## Materialized expansion
- Baseline real matches: 4,864
- Current real matches: 6,616
- New real matches: 1,752
- New materialized sources: Football-Data.co.uk E0 2020/21, 2021/22, 2022/23 and D1 2021/22, 2022/23.

## What was NOT counted
A discovered public global dataset advertises a much larger global footprint, but its binary Parquet payload was not materialized into this package during this execution. Therefore its headline row counts are not treated as Robo empirical data.

## Scientific protections
- `FOUND != DOWNLOADED != MATERIALIZED != PROCESSED != PIT_VALIDATED != USED_IN_MODEL`
- Exact PIT remains 0.
- Date-level odds are not promoted to exact PIT.
- No future information is used in historical features.
- No male data fills women coverage.
- No synthetic/mock/demo records enter empirical tables.
- Existing prospective snapshot is immutable and was verified byte-for-byte unchanged.
- Real money remains disabled.

## Main artifacts
- `data/global_dataset/reports/GLOBAL_DATASET_FINAL_REPORT.md`
- `data/global_dataset/reports/GLOBAL_DATASET_COVERAGE.csv`
- `data/global_dataset/reports/GLOBAL_COMPETITION_SEASON_MATRIX_2020_2026.csv`
- `data/global_dataset/reports/GLOBAL_FIELD_COVERAGE.csv`
- `data/global_dataset/reports/GLOBAL_DATASET_PROVENANCE.csv`
- `data/global_dataset/reports/NEGATIVE_FINDINGS.csv`
- `data/global_dataset/reports/GLOBAL_DATASET_COUNTS.json`
- `data/global_dataset/reports/GLOBAL_DATASET_TEST_REPORT.json`
- `data/global_dataset/reports/PREMATCH_SNAPSHOT_PROTECTION.json`
- `data/global_dataset/registry/GLOBAL_ACQUISITION_MANIFEST.json`
- `data/global_dataset/registry/GLOBAL_COMPETITION_TARGET_REGISTRY.csv`
- `data/global_dataset/registry/GLOBAL_SOURCE_CATALOG.csv`
- `scripts/global/run_global_dataset_mission.py`
- `scripts/global/validate_global_dataset.py`

## Engineering recommendation
The next acquisition should prioritize materializing a broad global match layer with stable IDs first, then attach match statistics, lineups/players and finally temporally precise market data. The model should not be retrained merely because the row count increased; first rerun entity resolution, temporal validation, leakage audit, coverage scoring and OOS/walk-forward baselines.
