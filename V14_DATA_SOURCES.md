# ROBO DA BET — Data Source Assessment

## Environment result

The execution environment used for this build does **not** provide outbound network access from the project runtime. Therefore no external historical dataset was silently downloaded or fabricated.

Status:

- HISTORICAL_DATA_ACQUIRED_IN_RUNTIME: **NO**
- HISTORICAL_DATA_IN_BUNDLE: **NO**
- DEMO DATA: **7 rows only; smoke tests only**

## Sources researched

### Football-Data.co.uk
Provides free historical football results, match statistics and betting odds. The site states that from 2019/20 it collects an initial odds set after market opening and a second closing set, while earlier seasons have pre-closing odds. The CSVs do not expose an exact odds-publication timestamp, so these files are suitable for real historical research but **not sufficient by themselves for exact timestamp-level PIT odds reconstruction**.

Official source: https://www.football-data.co.uk/data

### The Odds API
Provides historical odds as timestamped snapshots, with the closest snapshot at or before a requested timestamp. Historical data is paid. This is a strong candidate for exact PIT odds research when a valid API key and quota are available.

Official source: https://the-odds-api.com/historical-odds-data/

### Betfair Historical Data
Provides timestamped historical exchange data; the specification states availability from May 2015. This is suitable for exact time-series market research when purchased/accessed.

Official source: https://historicdata.betfair.com/Betfair-Historical-Data-Feed-Specification.pdf

## Decision

The V14.1 codebase supports external acquisition through adapters and explicitly distinguishes:

- `EXACT_TIMESTAMPED_HISTORICAL_ODDS`
- `PREMATCH_BOUNDED_ODDS_NO_EXACT_TIMESTAMP`
- `CURRENT_ODDS`

The strict PIT builder rejects datasets that lack exact `available_at` timestamps unless the experiment explicitly uses a bounded-availability protocol outside the strict PIT contract.
