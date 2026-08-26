# V25 Architecture Audit

## Result

**PASS for the local V25 Python/API architecture. PARTIAL for full production infrastructure because PostgreSQL, Redis, Docker and Maven runtimes were unavailable.**

V25 is layered under `ml/app/v25` and integrated into the existing `ml/app/api.py`. V20–V24 modules remain present.

## Main path

`provider → normalize → feed health/PIT → MarketExpressionEngine → value/risk filters → PAPER/SHADOW dataset → position/repricing → settlement → analytics/XLSX`

The V25 path is callable through FastAPI and through `ml/scripts/run_v25_observation.py`.

## Important boundary

The real observation path currently uses the **market baseline** unless a model probability or scoreline distribution is explicitly supplied. This is intentional. No untrained or nonexistent model is claimed as active.

## Production blockers

- no `THE_ODDS_API_KEY` in environment;
- Docker binary unavailable;
- Maven binary unavailable;
- no confirmed PostgreSQL runtime;
- no confirmed Redis runtime;
- no Telegram credentials;
- frontend package dependencies were not installed in the environment.
