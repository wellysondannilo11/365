# ROUND 2026-08-20 — MASTER STAFF INTELLIGENCE

## Decision boundary
Decision timestamp: 2026-08-20T16:40:00Z (analysis execution).

Five CONMEBOL matches were independently verified from public sources. No completed-match rows were added to the historical canonical dataset. The new materialization is structured fixture/context/market-reference data with provenance.

## Market gate
All 1X2 odds below are recorded on 2026-08-18 by the source pages; the timezone and exact capture timestamp are not independently proven. They are therefore `DATE_LEVEL_PIT`, not `EXACT_PIT` or `VALID_PIT`. No EV/edge is promoted to a value bet.

## Match status
- LDU Quito vs Mirassol: model_status=INSUFFICIENT_DATA; PIT=DATE_LEVEL_PIT; decision=NO_BET/WAIT
- Corinthians vs Rosario Central: model_status=INSUFFICIENT_DATA; PIT=DATE_LEVEL_PIT; decision=NO_BET/WAIT
- Olimpia vs Vasco da Gama: model_status=INSUFFICIENT_DATA; PIT=DATE_LEVEL_PIT; decision=NO_BET/WAIT
- Macará vs Santos: model_status=INSUFFICIENT_DATA; PIT=DATE_LEVEL_PIT; decision=NO_BET/WAIT
- Botafogo vs Cienciano: model_status=INSUFFICIENT_DATA; PIT=DATE_LEVEL_PIT; decision=NO_BET/WAIT

## Scientific verdict
`INSUFFICIENT_DATA` / `EDGE_NOT_DETERMINED`

## Important current context
- LDU–Mirassol: 1-1 aggregate; altitude/context is relevant but no independently materialized historical altitude model was promoted.
- Corinthians–Rosario Central: 0-0 aggregate; UOL reports André likely out and Allan suspended.
- Macará–Santos: 1-2 aggregate; UOL reports Santos preserving key players and playing at ~2,580m; these are context inputs, not causal claims.
- Botafogo–Cienciano: 1-6 aggregate; reversal requirement makes match result and qualification state distinct targets.
- Olimpia–Vasco: 0-0 aggregate; qualification remains open.
## Quantitative market observations

All 15 structured 1X2 observations are DATE_LEVEL_PIT only. Because exact timestamp and timezone are not proven, they are not eligible for PIT value calculation. Therefore TOP_VALUE_BET = NONE and PAPER_CANDIDATES = 0.
