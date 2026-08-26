# CONMEBOL DATASET FINAL REPORT

## Scientific status
`EDGE_NOT_DETERMINED`

## Real data materialized
**1170 matches** across Libertadores (2020–2022 available from the materialized CSV source) and Sudamericana (2020–2025 completed rows available from openfootball files). 2026 acquisition was not materialized in this execution.

## Coverage
- FOUND/DOWNLOADED/MATERIALIZED/PROCESSED are tracked per season in `data/conmebol/manifests/CONMEBOL_ACQUISITION_MATRIX.csv`.
- PIT validated: 0.
- Timestamped odds: 0.
- LIVE snapshots: 0.
- Settlements: 0.
- Female CONMEBOL: `WOMEN_DATA_INSUFFICIENT`.

## Research
The available CONMEBOL layer supports result, goal, stage, group, home/away, rest and pre-match rolling-form research. It does **not** support player-impact, injuries, lineups, cards, corners, shots, SOT, xG or PIT market edge claims for this materialized layer because those fields were not present in the acquired sources.

## Edge
No EDGE is confirmed. No ROI/CLV/PIT market conclusion is asserted.

## Limitations
2026 CONMEBOL data was not materialized; 2023–2026 Libertadores was not available in the acquired materialized source used here. Missing event/player/statistical layers remain explicit gaps.
