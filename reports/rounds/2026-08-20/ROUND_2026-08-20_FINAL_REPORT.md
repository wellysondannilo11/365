# CONMEBOL ROUND SCAN — 2026-08-20

Execution UTC: 2026-08-20T16:26:11.260842+00:00

## Scientific verdict

**INSUFFICIENT_DATA — TOP_TIP = NONE — REAL_MONEY = DISABLED**

Five CONMEBOL matches were independently confirmed for 20/08/2026 in the local Brazilian date: two Libertadores and three Sudamericana. No candidate can pass the Robo VALUE_BET gate because the available market references are not decision-time PIT snapshots and the internal canonical dataset does not contain sufficient historical coverage for all target teams.

## Canonical slate

| Competition | Match | Kickoff BRT | First leg | Aggregate state |
|---|---|---:|---|---|
| Libertadores | LDU Quito vs Mirassol | 19:00 | 1-1 | level; win advances, draw -> penalties |
| Libertadores | Corinthians vs Rosario Central | 21:30 | 0-0 | level; win advances, draw -> penalties |
| Sudamericana | Olimpia vs Vasco | 19:00 | 0-0 | level; win advances, draw -> penalties |
| Sudamericana | Macará vs Santos | 19:00 | 1-2 | Santos advances with draw/win |
| Sudamericana | Botafogo vs Cienciano | 21:30 | 1-6 | Botafogo needs 6-goal win for direct qualification; 5-goal win sends to penalties |

Sources: AFA schedule, UOL, CONMEBOL, GE and match-center sources; see registry CSV for provenance.

## Value-bet gate

The gate requires: independent Robo probability + calibrated/OOS model + valid price timestamp at or before decision timestamp + fair price + EV + data-quality checks.

**No market in this execution satisfies all gates.**

### Why this matters

Current web odds are useful as market references, but they are not automatically PIT. A page updated today without an exact odds timestamp cannot prove `odd_timestamp <= decision_timestamp`. Therefore they are not used to declare value.

## Game notes

### LDU Quito vs Mirassol
First leg ended 1-1. LDU has home advantage and altitude context in Quito, but the current internal canonical dataset has no Mirassol history, so a fully independent calibrated Robo probability cannot be produced.

### Corinthians vs Rosario Central
First leg ended 0-0. Both teams need a regulation win to avoid the penalty route. Corinthians has internal historical rows, but the target pairing still lacks sufficient complete current-season/team coverage for a calibrated independent market comparison.

### Olimpia vs Vasco
First leg ended 0-0. GE reported Vasco had 20 shots in the first leg while Olimpia defended deeply; this is useful context but is post-first-leg evidence and not a substitute for a validated pre-match feature store.

### Macará vs Santos
Santos won the first leg 2-1 and advances with a draw. The current internal dataset has no Macará history. Available O2.5 reference odds are stale relative to the decision timestamp and therefore rejected for PIT value analysis.

### Botafogo vs Cienciano
Cienciano won 6-1 in Cusco. Botafogo needs six goals to advance directly and five to force penalties. The extreme aggregate creates a special state that should not be priced like a normal league match. Current odds references show a huge Botafogo favorite, but the price timestamp is not decision-time verifiable and therefore cannot establish value.

## Ranking

| Rank | Match | Best supported market conclusion | Decision |
|---:|---|---|---|
| 1 | LDU Quito vs Mirassol | No independently validated Robo price | INSUFFICIENT_DATA |
| 2 | Corinthians vs Rosario Central | No independently validated Robo price | INSUFFICIENT_DATA |
| 3 | Olimpia vs Vasco | No independently validated Robo price | INSUFFICIENT_DATA |
| 4 | Macará vs Santos | No PIT price + incomplete internal history | INSUFFICIENT_DATA |
| 5 | Botafogo vs Cienciano | No PIT price + special aggregate state | INSUFFICIENT_DATA |

## Data audit

- REAL_MATCHES_BEFORE: 4,864
- REAL_MATCHES_NEW: 5 sourced round-context records
- REAL_MATCHES_TOTAL: 4,869 records across project + round registry (not merged into historical canonical because these are future fixtures, not completed historical matches)
- NEW_PIT_ODDS: 0
- TIMESTAMPED_ODDS: 0 new
- LIVE_SNAPSHOTS: 0 new
- XG_ROWS: 0 new
- LINEUPS: 0 new confirmed-at-decision snapshots
- PLAYERS: 0 new canonical records
- INJURIES: 0 new decision-time canonical records
- SUSPENSIONS: 0 new decision-time canonical records
- SETTLEMENTS: 0

## Important distinction

`FOUND` ≠ `DOWNLOADED` ≠ `MATERIALIZED` ≠ `PIT_VALIDATED`.

The five fixture/context records were materialized with provenance. Market references remain `NON_PIT` or `UNKNOWN`; none were promoted to PIT.

## Final status

```text
SCIENTIFIC_LEVEL = LEVEL 1/2 — DESCRIPTIVE/EXPLORATORY FOR THIS ROUND
DATA_QUALITY = MIXED
PIT_QUALITY = INSUFFICIENT
ODDS_QUALITY = NON_PIT / UNKNOWN TIMESTAMPS
MODEL_CONFIDENCE = NOT ELIGIBLE FOR FULL-SLATE VALUE PRICING
EDGE_STATUS = EDGE_NOT_DETERMINED
CLV_STATUS = NOT_AVAILABLE
LIVE_STATUS = NOT_AVAILABLE
REAL_MONEY = DISABLED
TOP_TIP = NONE
```
