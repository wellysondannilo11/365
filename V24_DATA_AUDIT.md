# V24 Data Audit

V24 distinguishes:
- `source_timestamp`: provider/source clock;
- `captured_at`: local ingestion clock;
- `commence_time`: fixture schedule.

V24 never substitutes kickoff for source timestamp.

Missing source timestamps block decisions. Future timestamps block decisions. Live stale source timestamps block decisions.

A V23 bug where feed freshness arguments were reversed was corrected so provider timestamp age is actually measured against ingestion time.
