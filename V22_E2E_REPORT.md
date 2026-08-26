# V22 E2E Report

### Executed
FastAPI application import, route registration, health/status/metrics/dataset smoke tests and safe external-dependency blocking.

### Controlled component E2E
Provider normalization -> baseline candidate construction -> existing V21 decision service is wired in code. Replay and dataset components have automated tests.

### Not executed
Full Feed -> Spring backend -> PostgreSQL -> Redis -> ML -> pricing -> decision -> ledger -> Telegram -> frontend -> observability runtime E2E, because Maven, Docker/services and external credentials were unavailable.

No simulated result is labeled as a real-feed E2E pass.
