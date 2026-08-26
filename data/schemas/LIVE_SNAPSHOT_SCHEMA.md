# LIVE SNAPSHOT SCHEMA

Every snapshot is append-only and ordered by `snapshot_timestamp`.

Required temporal fields:
- canonical_match_id
- snapshot_timestamp
- match_minute
- period
- source
- source_timestamp

Observed state fields may be NULL when the provider does not expose them. NULL is never replaced by an estimate during acquisition.

Evidence classes allowed for scientific use: `LIVE_REAL` only when the source timestamp and match identity are verified; otherwise `LIVE_REAL_UNVERIFIED`.
