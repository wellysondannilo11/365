# V18 — DATA QUALITY REPORT

## Demo fixture

The bundled fixture contains **7 rows / 7 events**. Existing quality validation passed for its structural fields, but this is not real-data evidence.

## V18 strict gate

The strict research path now requires explicit:

- `available_at`
- `source_timestamp`
- `captured_at`
- provider availability evidence
- valid odds
- canonical event identity

The gate rejects undefined availability such as `PREMATCH_ODDS_SET_NO_EXACT_TIMESTAMP`.

## Fail-closed

No strict PIT dataset was registered. Therefore no real backtest, OOS, ROI or CLV calculation was permitted.
