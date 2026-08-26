# V14 Data Acquisition

## Supported input formats

- CSV
- JSON
- Parquet

## Required raw principles

RAW records are append-only, hashed and deduplicated by deterministic payload hash. The original payload is retained in the raw record.

## Historical source adapters

### Football-Data.co.uk

Adapter: `ml/app/adapters/football_data.py`

Provides historical results, match statistics and betting odds. Its opening/pre-closing odds are useful for real historical research, but the CSV does not provide an exact odds publication timestamp. Therefore the adapter marks them `PREMATCH_ODDS_SET_NO_EXACT_TIMESTAMP` and the strict PIT layer does not silently convert them into exact availability timestamps.

### The Odds API

Adapter: `ml/app/adapters/odds.py`

Includes a historical snapshot method. Exact historical use requires an API key and paid historical access.

### StatsBomb Open Data

Adapter: `ml/app/adapters/statsbomb.py`

Prepared for selected historical match/event/lineup data. It is a football event-data source, not a bookmaker odds source.

### Betfair

No downloader was executed in this environment. It remains a documented external candidate for timestamped exchange historical data.

## Acquisition command

`python ml/scripts/acquire_football_data.py --season 2425 --league E0`

The command is intentionally external-data dependent. It does not synthesize data if the source is unavailable.
