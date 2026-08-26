# GLOBAL FREE DATA DISCOVERY REPORT V4

Generated: 2026-08-20T18:13:44.368011+00:00
Input ZIP: FREE_GLOBAL_ENRICHMENT_MASTER_COMPLETE.zip (latest Library artifact at mission start).

## Execution boundary

The working container has DNS/network resolution blocked. A direct HTTPS test to public sources fails with `Temporary failure in name resolution`. Therefore **REMOTE_BYTES_ACQUIRED_THIS_RUN = 0**. No source was promoted from DISCOVERED/FOUND to ACQUIRED merely because its documentation was found.

The mission nevertheless completed the local audit, source discovery, gap mapping, source-state enforcement, coverage matrix generation, snapshot hashing, and validation. The existing local materialized artifacts were preserved.

## Before / after

| Layer | Before | New | After |
|---|---:|---:|---:|
| Matches | 7,570 | 0 | 7,570 |\n| Players | 0 | 0 | 0 |\n| Player-match | 0 | 0 | 0 |\n| Lineups | 0 | 0 | 0 |\n| Injuries | 0 | 0 | 0 |\n| Suspensions | 0 | 0 | 0 |\n| Events | 0 | 0 | 0 |\n| xG | 0 | 0 | 0 |\n| Shots | 5,160 | 0 | 5,160 |\n| SOT | 5,160 | 0 | 5,160 |\n| Odds | 4,760 | 0 | 4,760 |\n| Exact PIT | 0 | 0 | 0 |\n| Women | 0 | 0 | 0 |\n
## Source state counts

- Sources discovered/documented in V4 registry: **15**.
- Remote sources accessible from this runtime: **0**.
- Remote source artifacts downloaded this run: **0**.
- New remote materialized artifacts this run: **0**.
- Inherited local validated acquisition records: **7**.
- Blocked acquisition records in inherited manifest: **9**.

The inherited local dataset already contains real materialized Football-Data/openfootball artifacts. These are not counted as new V4 acquisition.

## Verified discovery highlights

- StatsBomb Open Data exposes competitions/seasons plus match, event and lineup JSON and selected 360 data; its public repository was updated in May 2026.
- Football-Data.co.uk provides free CSV/Excel historical results, match statistics and odds across many leagues/seasons.
- API-Football currently advertises a free tier with 100 requests/day and 10/minute, including events, lineups, players, injuries, statistics and odds.
- football-data.org documents a registered free plan with 10 requests/minute.
- TheSportsDB provides a public/free V1 API with endpoint-specific free limits.
- OpenLigaDB exposes public football results/goals/fixtures for German competitions.
- Open-Meteo exposes historical weather from 1940 onward and geocoding/elevation APIs; this is a contextual source, not football event truth.
- Sofascore was assessed as DISCOVERED_ONLY. No automated endpoint use or bypass was performed; its own FAQ says it cannot share underlying data sources as API endpoints.

## Scientific status

- `GLOBAL_DATASET_STATUS = GLOBAL_PARTIAL`
- `FREE_DATA_STATUS = DISCOVERY_COMPLETE_MATERIALIZATION_BLOCKED`
- `ACQUISITION_STATUS = REMOTE_BLOCKED_DNS`
- `ENRICHMENT_STATUS = NO_NEW_REMOTE_BYTES_LOCAL_DATA_PRESERVED`
- `PIT_STATUS = DATE_LEVEL_PIT_ONLY`
- `MODEL_STATUS = RESEARCH_ONLY`
- `EDGE_STATUS = EDGE_NOT_DETERMINED`
- `VALUE_BET_STATUS = BLOCKED`
- `REAL_MONEY_STATUS = DISABLED`

## Core-layer coverage

For transparency, a simple unweighted layer-coverage indicator over the 11 requested core layers (matches, shots, SOT, xG, events, players, player-match, lineups, injuries, suspensions, Exact PIT) is **21.49%**. This is a diagnostic coverage index, not a probability of model accuracy and not a claim that 78.51% can necessarily be purchased. `PAID_GAP_PERCENT = NOT_DETERMINED` until provider-level paid coverage is empirically verified.

## Snapshot integrity

`SNAPSHOT_INTEGRITY = PASS`. No protected snapshot was changed by V4.

Before hashes:
```text
{
  "data/master_staff/PREMATCH_FEATURE_STORE.csv": "a8707eb991764492289e7f5806278962ae3ff3377891e979609bf747c4672a6b",
  "data/real_day_prematch/REAL_DAY_PREMATCH_SNAPSHOT.json": "97f83c1d992a8ea36bca44a8e14bb4d21e4c1d8024463e715f1bf24cba7c5c5c",
  "data/real_day_prematch/REAL_DAY_FEATURES.csv": "8616c6cb7e8ddc6a1bf2c67aa3b48745267efb78ab460ed4c4075bd6983ffec7"
}
```
After hashes:
```text
{
  "data/master_staff/PREMATCH_FEATURE_STORE.csv": "a8707eb991764492289e7f5806278962ae3ff3377891e979609bf747c4672a6b",
  "data/real_day_prematch/REAL_DAY_PREMATCH_SNAPSHOT.json": "97f83c1d992a8ea36bca44a8e14bb4d21e4c1d8024463e715f1bf24cba7c5c5c",
  "data/real_day_prematch/REAL_DAY_FEATURES.csv": "8616c6cb7e8ddc6a1bf2c67aa3b48745267efb78ab460ed4c4075bd6983ffec7"
}
```

## Main remaining bottlenecks

1. xG and event-level data remain unmaterialized.
2. Players/player-match and lineups remain unmaterialized.
3. Historical injuries/suspensions with point-in-time publication evidence remain unmaterialized.
4. Exact PIT remains zero; existing odds are not timestamp-complete.
5. Women's football remains zero in the canonical materialized dataset.
6. Remote acquisition must be run on a normal Internet/DNS-enabled machine.

## External execution

Use the existing resumable worker and the new V4 registry. API keys remain ENV-only. No paid API is enabled and REAL_MONEY remains disabled.
