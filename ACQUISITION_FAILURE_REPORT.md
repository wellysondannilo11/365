# ACQUISITION FAILURE REPORT — V2

## Status
`ACQUISITION_BLOCKED` for remote acquisition in the current execution environment.

## Technical evidence
Remote HTTP(S) resolution failed with `Temporary failure in name resolution` for previously tested public hosts including Football-Data, StatsBomb raw GitHub, API-Football, Sportmonks, The Odds API and Betfair historical endpoints.

## Consequence
- New remote matches: 0
- New remote xG: 0
- New remote events: 0
- New remote players: 0
- New remote lineups: 0
- New remote injuries: 0
- New remote suspensions: 0
- New remote Exact PIT: 0

This is a network limitation, not a successful empty acquisition.

## What remains runnable locally
`RUN_FREE_ACQUISITION.bat`, `RUN_FREE_ACQUISITION.ps1`, `RUN_FREE_ACQUISITION.sh` and the resumable acquisition worker are included for execution on a machine with normal Internet/DNS access.
