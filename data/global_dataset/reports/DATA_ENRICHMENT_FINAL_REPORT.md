# FREE DATA ENRICHMENT FINAL REPORT

Run: 2026-08-20T17:42:06.978867+00:00

## Real materialization
- Canonical matches before/after: 7570 / 7570
- New canonical matches: 0 (enrichment-only run; no duplicate promotion)
- Materialized local Football-Data artifacts reused: 17
- Unique matched canonical fixtures enriched: 5160
- Shots coverage: 5160 matches (68.16%)
- SOT coverage: 5160 matches (68.16%)
- xG: 0 new
- events: 0 new
- players: 0 new
- lineups: 0 new
- injuries: 0 new
- suspensions: 0 new
- exact PIT: 0 new

## Integrity
The original PREMATCH_FEATURE_STORE and real-day prospective snapshots were not written by this enrichment job.

## Source handling
Remote sources were not promoted in this run because the execution environment has no external DNS/network path. API-Football currently advertises a free tier with 100 requests/day; football-data.org documents a registered free plan with request throttling; StatsBomb Open Data exposes selected competitions/seasons via public JSON. Coverage is still subject to actual local materialization and validation.

## Conflicts
Potential multi-source duplicate keys detected in local Football-Data artifacts: 1782. They were deduplicated deterministically and source hashes retained.
