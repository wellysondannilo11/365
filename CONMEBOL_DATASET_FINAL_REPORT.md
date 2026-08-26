# CONMEBOL DATASET FINAL REPORT

## Scientific Status
`EDGE_NOT_DETERMINED`

## Real data
- Existing canonical historical matches preserved: **3694** prior rows + **1170** new materialized CONMEBOL rows = **4864** canonical rows.
- New real data materialized: **1170** matches.
- Competitions: Copa Libertadores and Copa Sudamericana.
- Seasons materialized: 2020–2025 (2025 Sudamericana is partial).
- Male: **1170**. Female: **0** (`WOMEN_DATA_INSUFFICIENT`).

## Acquisition truth
Per-season truth is in `data/conmebol/manifests/CONMEBOL_ACQUISITION_MATRIX.csv`. Only downloaded/parsed source files are marked materialized. 2026 is `ACQUISITION_BLOCKED`. Libertadores 2023–2026 are also `ACQUISITION_BLOCKED` in this execution.

## Available fields
Real date/team/stage/group/result data. No materialized CONMEBOL PIT odds, LIVE snapshots, settlements, player records, lineups, injuries, suspensions, cards, corners, shots, SOT or xG were available in the acquired sources.

## Research
Temporal-safe rolling form, rest, home/away, stage and knockout context were implemented. Benjamini-Hochberg FDR is applied to exploratory hypotheses. A simple pre-match logistic model has OOS/holdout/walk-forward diagnostics; it is not a betting edge model.

## Edge
No `EDGE_CONFIRMED`. PIT odds and settlements are absent, so ROI/CLV/value claims are not valid.

## Limitations
The 2025 Sudamericana file materializes **64 completed matches** from a partially updated source; its header advertises a larger season total, but future/unplayed rows are not materialized. 2026 data was not materialized. Female/player/context layers remain insufficient.
