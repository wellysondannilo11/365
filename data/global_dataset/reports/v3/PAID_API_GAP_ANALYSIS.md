# PAID API GAP ANALYSIS — FREE DATA MASTER V3

This report does not purchase or activate any paid service.

## What free sources can plausibly cover

- StatsBomb Open Data can provide selected competitions/seasons with matches, events, lineups and player participation; shot events include StatsBomb xG in the open-data event payload where available.
- Football-Data.co.uk provides large historical CSV collections containing results, match statistics and betting odds; the existing Robo materialization already supplies the current 5,160-match SHOTS/SOT layer.
- API-Football's current free tier advertises fixtures, events, lineups, players, injuries, statistics and pre-match/in-play odds, but the free tier is capped at 100 requests/day and historical season depth is limited.
- football-data.org free covers a limited set of competitions with fixtures, schedules and tables, with 10 requests/minute on the free plan.
- TheSportsDB has a public/free V1 API, but coverage and method limits are provider-dependent.
- OpenLigaDB is useful as an independent German-football validation source.

## What remains unresolved without paid/commercial feeds

1. Broad, deep historical player-level coverage across all target competitions.
2. Comprehensive injury/suspension history with publication timestamps suitable for strict as-of reconstruction.
3. Global confirmed lineups with publication timestamps.
4. Broad exact timestamped historical bookmaker odds across markets and books.
5. Uniform global event/xG coverage across all target leagues and seasons.
6. Stable global entity IDs and mappings across all providers.

## Scientific conclusion

A paid provider should only be considered after the free pipeline is executed on an Internet-connected machine and the resulting coverage matrix proves which fields remain unavailable. No paid provider is required for the current mission's architecture, and no Value Bet or REAL_MONEY gate is enabled by this analysis.
