# ROBO DA BET V16 — DATA QUALITY REPORT

## Result

**REAL DATA GATE: BLOCKED — NO REAL PROVIDER DATA AVAILABLE IN THE DELIVERED RUNTIME.**

The bundled `data.csv` contains 7 rows labelled `DEMO`. It lacks the event identity, provider timestamp and outcome-availability structure required for a real PIT betting dataset.

The V16 quality layer now blocks datasets with:

- duplicate rows;
- invalid odds;
- invalid timestamps;
- `available_at > decision_time`;
- inconsistent `event_id -> event_time` mappings;
- other blocking temporal defects.

The gate is intentionally fail-closed.

## Required real-data minimum

A betting research dataset must contain, at minimum:

`event_id`, `event_time`, `decision_time`, `source_time`, `available_at`, `ingested_at`, outcome/result fields, and timestamped odds when the experiment evaluates value/ROI/CLV.

Opening/closing labels without an exact publication/availability timestamp are not silently promoted to PIT odds.
