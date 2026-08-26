# DATA ACQUISITION REPORT — PHASE 2

## Status
`PARTIAL` for expansion, `SUCCESS` for processing of all real historical material currently present in the package.

### Materialized real data
- 30 EPL matches from 2023/24 with match statistics, referee and cards. SHA-256: `430d5e66f1acde23a1ddd610ad666f828de955ff835840444ca98441bb9bf5e9`.
- 10 EPL matches from 2025/26 with 1X2 prices/results. SHA-256: `4d2a6f73cbf20bfe2eb6dac2b7cc25033d749b6795bad1efe2db9ad4ad64a377`.
- Total historical-real processed: **40 matches**.

### Expansion attempt
The package's documented public routes include DataHub EPL and Football-Data-derived GitHub data. Web verification confirms DataHub publishes 33 EPL season CSV resources and the GitHub derivative publishes 12,700+ EPL results with bookmaker odds. The execution container, however, still cannot resolve external hosts; direct attempts to `raw.githubusercontent.com` and `datahub.io` failed at DNS. Therefore no external bytes were claimed as locally acquired in this run.

## Integrity rule
No DEMO, MOCK, FIXTURE or synthetic row was promoted to historical-real.
