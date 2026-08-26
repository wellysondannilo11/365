# DATA ACQUISITION REPORT — PHASE 3

## Materialized real data
- epl_2324_real_pilot.csv: 30 matches, EPL 2023/24 pilot, SHA-256 `430d5e66f1acde23a1ddd610ad666f828de955ff835840444ca98441bb9bf5e9`.
- epl_2025_2026_web_verified_pilot.csv: 10 matches, EPL 2025/26 pilot, SHA-256 `4d2a6f73cbf20bfe2eb6dac2b7cc25033d749b6795bad1efe2db9ad4ad64a377`.
- Total historical-real rows processed: **40**.

## Expansion
Web research confirmed additional historical-data routes (Football-Data, StatsBomb Open Data, TheStatsAPI, The Odds API, Betfair Historical Data, API-Football, Sportmonks), but this execution container cannot resolve external hosts, so no new external bytes were promoted to HISTORICAL_REAL.

## Integrity
No DEMO/MOCK/FIXTURE row was promoted.
