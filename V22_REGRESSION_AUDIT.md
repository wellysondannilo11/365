# V22 Regression Audit

## Python regression
- Full pytest suite: **101 tests collected, 101 PASS**.
- `python -m compileall -q ml tests`: **PASS**.
- Legacy V20/V21 tests remain in the suite and passed.
- V22 added five focused tests covering provider normalization/credential blocking, replay/dataset, position actions and feed health.

## API smoke
FastAPI TestClient successfully exercised `/health`, `/v22/status`, `/v22/metrics`, `/v22/dataset`.
Missing credentials correctly produced HTTP 503 for `/v22/feed/poll` and `/v22/scan`.

## External/runtime regressions
- Maven: NOT EXECUTED — Maven unavailable.
- npm test/build: NOT EXECUTED — dependency installation timed out.
- Docker Compose: NOT EXECUTED — Docker unavailable.
- PostgreSQL/Redis: NOT EXECUTED — services unavailable.
- Real feed: NOT EXECUTED — credential unavailable.
- Telegram real delivery: NOT EXECUTED — credential unavailable.
