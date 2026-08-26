# V18 — PIT AUDIT

## Rule

`available_at <= decision_time`

and, where applicable:

`source_timestamp <= decision_time`

## V18 hardening

- Strict odds normalization can no longer infer PIT availability when `strict_pit=True` and `available_at` is absent.
- Provider availability evidence is checked.
- Future timestamps are rejected as errors.
- `ingested_at` is never used as a substitute for provider availability.
- Provider snapshot, bookmaker update, market update and source timestamp remain distinct.

## Negative controls

V18 tests reject:

1. future timestamp;
2. future odds;
3. undefined odds availability;
4. unsupported strict PIT metadata.

## Result

**PASS at control/test level; real provider PIT dataset NOT AVAILABLE.**
