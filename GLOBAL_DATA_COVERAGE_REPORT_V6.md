# ROBO DA BET — GLOBAL DATA ACQUISITION V6 FINAL REPORT

**Execution:** 2026-08-20T18:39:10.243456+00:00

## BEFORE → NEW → AFTER

| Camada | Antes | Novo real | Depois | Cobertura |
|---|---:|---:|---:|---:|
| MATCHES | 7,570 | 0 | 7,570 | 100.00% |
| SHOTS | 5,160 | 0 | 5,160 | 68.16% |
| SOT | 5,160 | 0 | 5,160 | 68.16% |
| XG | 0 | 0 | 0 | 0% |
| EVENTS | 0 | 0 | 0 | 0% |
| PLAYERS | 0 | 59 | 59 | source-layer only |
| PLAYER_MATCH | 0 | 0 | 0 | 0% |
| LINEUPS | 0 | 0 | 0 | 0% |
| INJURIES | 0 | 0 | 0 | 0% |
| SUSPENSIONS | 0 | 0 | 0 | 0% |
| ODDS | 4,760 | 0 | 4,760 | 62.88% |
| EXACT_PIT | 0 | 0 | 0 | 0% |
| DATE_LEVEL_PIT | 30 | 0 | 30 | 0.40% |
| WEATHER | 0 | 0 | 0 | 0% |

## What was materially acquired

1. **59 unique player entities** from two real public squad artifacts for Brasileirão Série A 2024: Flamengo and Palmeiras.
2. One real Brazil 2024 Série A match CSV artifact from the public footballcsv cache (64 matches in the downloaded artifact). It was retained as source evidence and was not counted as new canonical matches because the canonical backbone already contains overlapping fixtures.
3. Two squad text artifacts were checksumed and normalized into `PLAYER_MASTER_V6.csv`, `PLAYER_TEAM_HISTORY_V6.csv` and `PLAYER_ENTITY_RESOLUTION_V6.csv`.

## What was deliberately NOT inferred

- Roster membership was **not** converted into lineups.
- Squad membership was **not** converted into player-match participation.
- No injuries/suspensions were inferred from absence.
- No xG was calculated from non-xG sources.
- No Exact PIT was promoted from date-level odds.

## Remote limitations

The runtime's ordinary Python HTTP path remains DNS-blocked. A controlled public-web retrieval path was used to verify current availability of StatsBomb Open Data and other public sources. StatsBomb's public repository exposes competitions, matches, events and lineups for selective competitions/seasons, but JSON downloads could not be materialized through the current file-download path because the environment rejects JSON content types. Therefore no StatsBomb JSON rows are counted as acquired.

## Final status

`GLOBAL_DATASET_STATUS = GLOBAL_PARTIAL`

`ACQUISITION_STATUS = PARTIAL_REAL_DATA_ACQUIRED_REMOTE_RUNTIME_LIMITED`

`ENRICHMENT_STATUS = PLAYER_ROSTER_PARTIAL`

`PIT_STATUS = DATE_LEVEL_PIT_ONLY`

`MODEL_STATUS = RESEARCH_ONLY`

`EDGE_STATUS = EDGE_NOT_DETERMINED`

`VALUE_BET_STATUS = BLOCKED`

`REAL_MONEY_STATUS = DISABLED`
