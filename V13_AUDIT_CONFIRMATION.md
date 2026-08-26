# V13 Audit Confirmation

The V12 source was inspected before V13 changes. Confirmed gaps included: simplified walk-forward, calibration helper capable of fitting/evaluating on the same OOS slice, consensus logic that grouped selections before complete bookmaker-market de-vig, incomplete historical-feature provenance, no immutable raw-record contract, no decision replay artifact, and no dedicated statistical multiple-testing/holdout state modules.

Severity priorities:
- CRITICAL: point-in-time lineage, historical odds availability, calibration separation, holdout contamination.
- HIGH: market consensus grouping/de-vig, reproducibility, decision replay, realistic backtest.
- MEDIUM: drift persistence, frontend research views, bookmaker quality estimation.

V13 corrections are additive and preserve V12 compatibility where possible.
