# ROBO DA BET V16 — SOURCE AUDIT

## Current evidence

The source documentation was independently checked during the V16 audit. The project itself does not contain provider credentials and does not ship a real historical PIT odds dataset.

### Football-Data.co.uk

Useful for real historical results, match statistics and bookmaker odds columns. Its current download documentation distinguishes pre-closing/opening and closing odds and warns that Pinnacle public API delivery has been unreliable since July 2025. The CSV data does not establish the exact moment an opening price became available, so it is not sufficient alone for strict decision-time odds reconstruction.

### The Odds API

The current historical API provides snapshots and returns the closest snapshot equal to or earlier than a requested timestamp. The documentation states 10-minute historical snapshots for featured markets from 2020 and 5-minute snapshots from September 2022; historical access is paid. This is suitable for strict snapshot-based PIT research when credentials and quota are available.

### TheStatsAPI

Current documentation advertises football fixtures/results/stats/xG plus bookmaker odds and stored opening/last-seen prices. The current public historical-odds page also advertises movement history on higher tiers. Exact decision-time availability must still be verified from an actual provider response before treating it as equivalent to The Odds API snapshot PIT.

### Betfair Historical Data

Betfair's official developer documentation states that historical Exchange data is time-stamped, available from April 2015, and can be purchased/downloaded or accessed through its Historical Data API after purchase. It is appropriate for Exchange market/price/settlement research and independent market validation.

### StatsBomb Open Data

StatsBomb provides selected competitions/seasons as JSON for research. It is useful for event/lineup football features but is not a bookmaker historical-odds source. Attribution requirements apply.

### Flashscore

Flashscore exposes broad live results, statistics, xG, lineups and odds-comparison information. However, this audit did not establish a reproducible historical timestamped odds series suitable for strict PIT. It remains complementary only; no scraping bypass, CAPTCHA bypass or rate-limit circumvention is implemented.

## Acquisition attempt

A direct Football-Data CSV acquisition was attempted in the execution environment and failed because the runtime has no outbound DNS/network access. No real records were fabricated as a fallback.

The project therefore remains blocked from a real betting OOS/backtest until a legally usable real dataset or provider credential is supplied in an environment with network access.
