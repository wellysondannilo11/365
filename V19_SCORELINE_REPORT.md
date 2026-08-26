# V19 — SCORELINE DISTRIBUTION REPORT

## Result

**IMPLEMENTED AND UNIT-VALIDATED.**

The engine generates a finite scoreline grid, applies optional Dixon-Coles correction, and renormalizes the grid to total probability 1.

## Empirical status

No real football dataset with defensible PIT odds was available. Therefore no claim is made about scoreline calibration, Brier, Log Loss, ROI or edge.

## Validation evidence

- Distribution normalization tests: PASS.
- Dixon-Coles normalization tests: PASS.
- 1X2 consistency tests: PASS.
- Totals complement tests: PASS.
- BTTS complement tests: PASS.

## Future evidence required

Real OOS calibration by league/season, reliability curves, Brier/Log Loss, parameter stability and comparison against market-only baselines.
