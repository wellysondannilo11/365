# V17 — DATA QUALITY REPORT

## Demo fixture gate

The bundled fixture contains 7 rows. After adding synthetic identifiers/timestamps only for the purpose of testing the quality gate, the V17 gate returned:

- rows: 7
- events: 7
- duplicate rows: 0
- invalid odds: 0
- invalid timestamps: 0
- PIT violations: 0
- event-time inconsistencies: 0
- gate status: PASS

This PASS is a **schema/quality test of the demo fixture**, not evidence that the dataset is real.

## Fail-closed rule

A source dataset cannot enter the empirical betting research path unless required timestamps, event identity, settlement and odds provenance pass validation.

## Limitation

No real dataset was available in the runtime, so real-data coverage, missingness, source completeness and market coverage cannot be quantified.
