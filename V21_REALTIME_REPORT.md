# V21 REALTIME REPORT

### Implemented

- Provider interfaces are decoupled from the decision engine.
- Feed health tracks freshness and failures.
- Live snapshots require timezone-aware timestamps and reject future data.
- Live market snapshots fail closed on stale/missing/future data.
- Retry/backoff is available through `ResilientPoller`.
- `POST /v21/live/scan` orchestrates a provider-neutral live scan into the V21 decision service.
- Existing V20 live repricing remains available and was not replaced.

### External execution limitation

No external sports/odds credentials were configured in this environment. Therefore live observation against a real provider is **NOT EXECUTED**. No fake provider result is presented as real data.
