# V25 Regression Audit

## Python regression

Full pytest suite: **134 tests PASS**.

Python compileall: **PASS**.

Existing V20–V24 tests remained in the suite and continued passing after V25 integration.

## Frontend regression

Node source-level tests: **2 PASS**.

Vite production build: **BLOCKED** because dependencies were not installed.

## External runtime regression

- Maven/Spring: BLOCKED — Maven unavailable.
- Docker: BLOCKED — Docker unavailable.
- PostgreSQL: BLOCKED — no runtime service.
- Redis: BLOCKED — no runtime service.
- Real feed: BLOCKED — credential unavailable.
- Telegram real: BLOCKED — credentials unavailable.

## Exact blocked command results

- `mvn -q -DskipTests package` → `mvn: command not found`
- `npm run build` → `vite: not found`
- `docker compose config` → `docker: command not found`
