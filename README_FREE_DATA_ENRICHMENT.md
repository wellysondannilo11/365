# Robo da Bet — Free Data Enrichment

This extension preserves the existing architecture and prospective artifacts. It adds a reproducible local enrichment layer instead of replacing the Robo.

## Local execution

Windows:
- `RUN_FREE_ACQUISITION.bat`
- `RUN_FREE_ACQUISITION.ps1`

Linux/WSL:
- `./RUN_FREE_ACQUISITION.sh`

The enrichment job scans already-materialized public Football-Data CSVs, resolves fixtures using normalized team names plus date, deduplicates source rows, records source SHA-256 provenance and writes:

- `data/enrichment/free_data/MATCH_STATISTICS_FREE.csv`
- `data/enrichment/free_data/FOOTBALL_CANONICAL_ENRICHED_FREE.csv`
- `data/global_dataset/reports/FREE_SOURCE_COVERAGE_MATRIX.csv`
- `data/global_dataset/reports/DATA_ENRICHMENT_FINAL_REPORT.md`
- `data/global_dataset/reports/SOURCE_ACQUISITION_REPORT.md`
- `data/global_dataset/reports/ACQUISITION_FAILURE_REPORT.md`
- `data/global_dataset/reports/PREMATCH_DATA_READINESS_REPORT.md`

Remote providers remain separate. Configure legitimate API keys only through environment variables. Never commit credentials.

## Provider priorities

1. StatsBomb Open Data for event/lineup/player layers where the open repository actually covers the requested competition/season.
2. API-Football for complementary fixtures/events/lineups/players/injuries/statistics when the user's free key and quota permit it.
3. football-data.org for results/fixtures and supported historical resources.
4. OpenLigaDB for independent German-football validation.
5. TheSportsDB as a lower-priority complementary source.
6. Football-Data.co.uk for public historical match statistics and market columns where available.

No source is counted as acquired merely because its catalogue or endpoint exists.
