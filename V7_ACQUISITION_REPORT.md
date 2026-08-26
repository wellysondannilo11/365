# ROBO DA BET — V7 ACQUISITION REPORT

## Executive status

`REMOTE_ACQUISITION = BLOCKED_DNS`

The V6 ZIP was opened and audited in the current runtime. A real HTTPS request to the StatsBomb public GitHub raw endpoint failed at DNS resolution (`Could not resolve host: raw.githubusercontent.com`). Therefore this run did **not** claim any new remote data.

## Real materialized gain

| Layer | Before | New | After |
|---|---:|---:|---:|
| MATCHES | 7,570 | 0 | 7,570 |
| PLAYERS | 0 | 59 | 59 |
| PLAYER_MATCH | 0 | 0 | 0 |
| XG | 0 | 0 | 0 |
| EVENTS | 0 | 0 | 0 |
| LINEUPS | 0 | 0 | 0 |
| INJURIES | 0 | 0 | 0 |
| SUSPENSIONS | 0 | 0 | 0 |
| SHOTS | 5,160 | 0 | 5,160 |
| SOT | 5,160 | 0 | 5,160 |
| ODDS | 4,760 | 0 | 4,760 |
| EXACT_PIT | 0 | 0 | 0 |
| DATE_LEVEL_PIT | 30 | 0 | 30 |
| WEATHER | 0 | 0 | 0 |
| WOMEN | 0 | 0 | 0 |

The 59 players are **existing V6 materialization**, not a V7 acquisition gain.

## Remote evidence

Remote bytes acquired during V7: **0**.

No simulated downloads, fabricated records, inferred lineups, inferred injuries, or promoted PIT records were used.

## Local rediscovery

The V6 package contains real local materializations including 5,160 match-stat rows, 5,160 shot/SOT records, 4,760 odds rows, 59 canonical player records, player entity resolution, and multiple provenance/coverage reports. Empty engine tables for player-match, lineups, injuries and suspensions remain empty and were not falsely populated.
