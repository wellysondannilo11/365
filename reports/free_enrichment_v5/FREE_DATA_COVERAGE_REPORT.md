# GLOBAL DATA COVERAGE REPORT V5

Generated: 2026-08-20T18:24:59.451724+00:00

## Mission boundary
The latest Library artifact used as input was `GLOBAL_FREE_DATA_DISCOVERY_ENRICHMENT_V4_COMPLETE.zip` (5,103,310 bytes). The inherited project was audited in-place; no protected snapshot was rewritten.

## Hard execution result
`REMOTE_BYTES_ACQUIRED = 0` in this runtime. DNS resolution is blocked for the public acquisition hosts tested. Therefore V5 does **not** claim new remote football data.

## Real inherited materialized data
- Canonical matches: **7,570**.
- SHOTS: **5,160** real match-stat rows.
- SOT: **5,160** real match-stat rows.
- Match statistics artifact: 5,160 rows.
- Odds-bearing canonical matches: **4,760**.
- Exact PIT: **0**.
- Players/lineups/injuries/suspensions/events/xG: **0** in the canonical enrichment layer.

## Engineering gain vs data gain
`DATA_GAIN_THIS_RUN = 0` remote records.
`ENGINEERING_GAIN_THIS_RUN = HIGH`: provider contract, V5 source registry, field-level gap matrix, network probe, API key ENV contracts, provider URL templates, free-tier prioritization, paid cost matrix, and expanded audit/reporting.

## Discovery findings
StatsBomb Open Data is a legitimate open-data source with competition/season metadata plus matches, events and lineups, and selected 360 data. It is the highest-value free source for closing events/lineups/player-event gaps, but coverage is selective.

Football-Data.co.uk is free and provides historical results, match statistics and odds; its current public site states 32 seasons of results, 27 seasons of betting odds and 27 seasons of match statistics, with downloadable CSV/Excel files.

API-Football currently advertises a free plan with 100 requests/day and 10/minute, including events, lineups, players, injuries, statistics and odds.

Open-Meteo is useful for contextual weather/elevation enrichment, not football truth.

Sofascore remains `DISCOVERED_ONLY` for automated acquisition under this mission; no bypass or aggressive scraping was attempted.

## Coverage score
For the 12 core layers (matches, shots, SOT, xG, events, players, player-match, lineups, injuries, suspensions, odds, Exact PIT), the simple unweighted diagnostic coverage remains approximately **17.6%** when each layer is binary at the requested target. This is a diagnostic, not model accuracy.

## Next highest-value free execution
1. Run StatsBomb Open Data acquisition on a DNS-enabled machine and materialize competitions/seasons/matches/events/lineups.
2. Run Football-Data.co.uk incremental historical acquisition for uncovered leagues/seasons and preserve existing checksums.
3. If credentials are available, use API-Football free quota first on P0 fields (injuries, lineups, players, events).
4. Add Open-Meteo only after venue coordinates are resolved.
5. Do not spend on odds until exact timestamped PIT coverage is quantified.
