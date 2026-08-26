# FREE GLOBAL COVERAGE STATUS V3

## Runtime result

The execution environment has no working external DNS path. Direct DNS resolution failed for every tested remote provider host. Therefore **remote acquisition in this execution = 0 bytes**.

## Existing real data preserved

The input ZIP already contains a real Football-Data.co.uk-derived enrichment layer matching 5,160 canonical fixtures for SHOTS/SOT. This mission did not count those existing rows as new acquisition.

## Discovery that was verified from current public documentation

- StatsBomb Open Data: public repository with selected competitions/seasons and JSON matches/events/lineups; current repository activity shows a May 2026 data update.
- Football-Data.co.uk: public historical results, match statistics and betting-odds files across many leagues/seasons.
- API-Football: free tier currently advertises 100 requests/day, 10 requests/minute and endpoints including events, lineups, players, injuries, statistics and odds.
- football-data.org: free plan currently advertises 12 competitions and 10 calls/minute, with fixtures/schedules/tables.
- TheSportsDB: public/free V1 API with provider-dependent method limits; free users are rate limited.

## Classification rule

`FOUND` / documentation presence is never promoted to `ACQUIRED`.

Remote records remain:

`FOUND -> BLOCKED_NO_NETWORK`

No bytes were promoted to MATERIALIZED, VALIDATED, PROCESSED or USED_IN_MODEL during this execution.
