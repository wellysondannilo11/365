# V20 IMPLEMENTATION REPORT

Implemented incrementally on V19.

## Added
- Selective opportunity engine with configurable thresholds and explicit NO BET reasons.
- Global ranking and one-best-market-per-event selection boundary.
- Fractional Kelly/capped stake sizing with uncertainty and correlation penalties.
- Portfolio risk limits for event/day/simultaneous exposure.
- Live repricing engine with fail-closed minimum sample.
- Position management: HOLD/REDUCE/EXIT/REASSESS and independent reverse candidate detection.
- Immutable V20 paper ledger, settlement and XLSX export.
- Today/month/all performance, market and league aggregation.
- Optional Telegram provider abstraction.
- V20 API routes and frontend surfaces.

## Preserved
- V19 pricing engine and derived markets.
- V19 PIT/leakage/holdout controls.
- Existing adapters and research modules.
- Existing backend/frontend architecture.
