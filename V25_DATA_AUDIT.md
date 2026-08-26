# V25 Data Audit

PIT semantics remain strict:

- `source_timestamp` is provider/source time;
- `captured_at` is ingestion time;
- kickoff/commence time is never used as source availability;
- stale/future/missing timestamps block decisions.

V25 observations contain event/snapshot/decision lineage and hash-chain fields. Fake fixtures are never classified as real data.
