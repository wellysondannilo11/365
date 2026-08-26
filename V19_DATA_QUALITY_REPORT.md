# V19 — DATA QUALITY REPORT

## Real-data status

No real dataset was acquired. V19 therefore does not claim real data quality.

## Strict rules

- Odds must have valid prices.
- Strict PIT requires `available_at` and `source_timestamp`.
- Decision-time filtering rejects future market observations.
- Ingestion time is not substituted for availability time.
- Missing temporal evidence remains a hard scientific gate.

## Bundled fixture

The seven DEMO rows remain fixtures only and are excluded from ROI/OOS/edge claims.
