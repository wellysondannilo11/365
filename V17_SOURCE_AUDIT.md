# ROBO DA BET V17 — SOURCE AUDIT

## Scope

This audit distinguishes sources that can support strict Point-in-Time betting research from sources that are useful only as secondary football context.

## Source classification

| Source | V17 class | Intended use | Current blocker |
|---|---|---|---|
| The Odds API | A | Historical bookmaker snapshots with provider snapshot timestamp | Paid historical access + API key + network |
| Betfair Historical Data | A | Timestamped Exchange market/price research | Purchased data/credentials + network |
| Football-Data.co.uk | B/C | Historical results, match stats, opening/closing odds | No exact publication timestamp per row; network unavailable in runtime |
| StatsBomb Open Data | C/D | Selected event/lineup football features | Not an odds source; network unavailable |
| Flashscore | D | Complementary results/stat context | No validated reproducible historical odds PIT series; no scraping bypass implemented |

## Evidence reviewed

- Football-Data states that since 2019/20 it collects a pre-closing set and a closing set of odds, with collection times described on its fixtures page. It also warns about Pinnacle data reliability after July 2025. This makes Football-Data valuable for secondary research, but the dataset must not be silently treated as an exact provider-native decision-time snapshot.
- The Odds API documents historical odds snapshots, with the API returning the closest snapshot equal to or earlier than the requested timestamp. Featured-market history starts in June 2020; snapshot frequency is 10 minutes initially and 5 minutes from September 2022. Historical access is paid.
- Betfair documents its Historical Data service as timestamped Exchange data available for purchase/download.

## V17 execution evidence

The runtime performed a real network probe and source acquisition attempts. DNS/network resolution failed. No credentials were present for The Odds API. No purchased Betfair historical dataset was present. No source data was fabricated.

## Decision

The V17 main betting evidence pipeline remains **closed** until an A-class timestamped odds dataset is supplied or acquired in a network-enabled environment.
