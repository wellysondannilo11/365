# V19 — MARKET DISLOCATION REPORT

## Implemented

For a valid market observation the engine calculates:

- model probability
- market implied probability
- probability edge
- fair odds
- market odds
- odds ratio
- EV

Market rows can be normalized and de-vigged. Consensus is aggregated separately from raw bookmaker prices.

## PIT control

When a decision time is supplied, only market observations with `available_at <= decision_time` are eligible. Strict mode requires explicit availability and source timestamps.

## Scientific status

No real dislocation study was executed because no real timestamped odds dataset was acquired. Positive EV remains a mathematical signal, not evidence of sustainable edge.
