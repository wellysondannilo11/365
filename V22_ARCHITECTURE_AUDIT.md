# ROBO DA BET V22 — Architecture Audit

## Scope
Audit performed directly against `ROBO_DA_BET_V21_FINAL.zip` before V22 changes. The V21 archive contained 333 files and preserved V12–V21 research/report history, backend, frontend, PostgreSQL migrations, ML/Python services, Redis configuration, Docker Compose, tests and paper/shadow artifacts.

## Findings
- V21 had a strong quantitative/research foundation and a provider-agnostic realtime abstraction, but no concrete external odds adapter.
- V21's primary operational ledger/research store was JSONL, not PostgreSQL.
- The Spring backend was mainly a proxy to the Python ML API; no substantive domain persistence lived in Spring.
- Frontend was functional but narrow: essentially a V21 status/ledger screen.
- Docker and PostgreSQL/Redis were defined, but the environment used for this audit did not provide Docker and no DB credentials/service were available.
- V21's live engine accepted normalized payloads but did not itself acquire a real feed.
- V21 did not provide a complete replay/dataset/observability layer for real-feed observations.

## V22 changes
- Added authorized The Odds API v4 adapter, credential-safe and provider-agnostic.
- Added normalization for event/market/bookmaker/selection/price/PIT timestamps.
- Added FeedManager, provider health and external dependency blocking.
- Added V22 dataset store and PostgreSQL persistence adapter/schema.
- Added replay snapshot engine.
- Added position HOLD/REDUCE/EXIT and independent reversal assessment.
- Added structured observability, counters and Prometheus text endpoint.
- Added V22 API surface and frontend V22 status/research view.
- Added a market-only baseline scan path. It is explicitly labeled a baseline, not an AI edge model.
- Preserved paper/shadow-only operation and no bookmaker execution path.
