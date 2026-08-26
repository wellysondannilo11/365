# WEB_VERIFIED_DATA_SOURCES — FOOTBALL EMPIRICAL ACQUISITION

This document records public football-data routes verified through the web retrieval layer during the empirical run. Verification of a public source is **not** counted as historical-real rows processed by the local pipeline.

## Primary source
- Football-Data.co.uk publishes historical football results, match statistics and betting odds in CSV/Excel formats, with season-by-season files and historical coverage back to the 1990s. The site also states that since 2019/20 it has collected an opening/pre-closing odds set and a closing odds set, while warning about Pinnacle public-API reliability since 23/07/2025.
- Verified source: https://www.football-data.co.uk/downloadm.php

## Historical EPL derivative with odds
- `AnishKhetani/premier-league-data` is a public derivative sourced from football-data.co.uk. Its repository documents 12,700+ Premier League matches from 1993-94 onward and a `results_with_odds` table containing opening/closing bookmaker odds, 1X2, Over/Under 2.5 and Asian Handicap fields.
- Verified source: https://github.com/AnishKhetani/premier-league-data

## Historical EPL results/statistics/cards
- DataHub's English Premier League dataset is sourced from football-data.co.uk and publishes season CSV files from 1993/94 onward. Its schema includes referee, shots, fouls, corners, yellow cards and red cards where available.
- Verified source: https://datahub.io/football/english-premier-league

## Runtime limitation
The local execution container has no functioning external DNS/network route. Direct acquisition attempts therefore failed with name-resolution/network errors. The web layer could verify public sources and schemas, but the available tooling did not provide a byte-materialization path from those web results into the project filesystem.

Therefore:

`HISTORICAL_REAL_PROCESSED = 0`

No source verified only through the web layer is treated as processed historical evidence.
