# ACQUISITION FAILURE REPORT

## Current execution environment

Remote acquisition was not counted because outbound DNS/network resolution is unavailable in this execution environment. This is a real block, not a simulated failure.

Observed blocked routes in the existing acquisition manifest include API-Football, The Odds API, Betfair historic data, raw GitHub, Sportmonks and football-data.org.

## What was actually materialized

The run reused 17 already-materialized Football-Data CSV artifacts inside the ZIP. These were checksum-tracked and parsed locally. They enriched 5,160 existing canonical fixtures with real shots/SOT and related match-stat fields. No new fixture rows were promoted, so the canonical count remains 7,570.

## Not acquired in this run

- StatsBomb Open Data: 0 new remote bytes; open-data registry recorded, but not promoted without local download/materialization.
- API-Football: 0 new remote bytes; free tier requires a user API key and remote access.
- football-data.org API: 0 new remote bytes; authenticated access and remote network required.
- OpenLigaDB: 0 new remote bytes.
- TheSportsDB: 0 new remote bytes.
- Historical Exact-PIT odds: 0 new rows.
- Players, lineups, injuries, suspensions, xG and event streams: 0 new rows.

## Prohibition compliance

No Cloudflare bypass, authentication bypass, paywall bypass, synthetic data, fabricated timestamps, or deliberate rate-limit violation was used.
