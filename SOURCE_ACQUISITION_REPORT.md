# SOURCE ACQUISITION REPORT — FREE DATA V2

| Source | Discovery | Remote access in current runtime | New remote bytes | Local materialized evidence | Grade |
|---|---|---|---:|---|---|
| Football-Data.co.uk | VERIFIED | BLOCKED by DNS | 0 | 5,160 match-stat rows reused from checksum-tracked local CSVs | A |
| StatsBomb Open Data | VERIFIED | BLOCKED by DNS | 0 | Adapter present; no StatsBomb bytes materialized | A |
| API-Football | VERIFIED | BLOCKED/no key in runtime | 0 | Adapter/config ready; no API responses materialized | A |
| football-data.org | VERIFIED | BLOCKED | 0 | Registry/adapter path ready | B |
| OpenLigaDB | VERIFIED | BLOCKED | 0 | Registry target; no rows materialized | B |
| TheSportsDB | VERIFIED | BLOCKED | 0 | Registry target; no rows materialized | C |

## Acquisition state rule
`FOUND != ACCESSIBLE != DOWNLOADED != MATERIALIZED != VALIDATED != PROCESSED != USED_IN_MODEL`.

No discovery-only source is counted as acquired.

## Current network block
The execution container cannot resolve external DNS hosts (`Temporary failure in name resolution`). Therefore no new remote dataset bytes are claimed. The local enrichment layer uses only real, checksum-tracked artifacts already present in the input ZIP.

## Local evidence
The input ZIP contains Football-Data CSVs with match statistics and odds. These were matched to the canonical backbone and produced 5,160 enriched fixtures for shots/SOT. Their provenance is retained in `data/enrichment/free_data/MATCH_STATISTICS_FREE.csv`.
