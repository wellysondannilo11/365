# V14 Audit Confirmation — Code-Real Findings

Date: 2026-08-19

## Initial state

The V14 bundle contained 108 project files, a 7-row demo CSV, a FastAPI ML service, a Spring Boot proxy, a React/Vite frontend, PostgreSQL migrations, Redis configuration, research modules, adapters, model/experiment registries, PIT/leakage utilities and tests.

## Findings confirmed in code

| Component | Initial status | Evidence | Impact | Severity | Action |
|---|---|---|---|---|---|
| pytest import path | PARTIAL | `pytest -q` initially failed with `ModuleNotFoundError: ml` | Test suite was not directly runnable from repository root | P1 | Added `pythonpath = .` |
| Row-level PIT | IMPLEMENTED | `ml/app/leakage.py` | Base timestamps were checked | — | Preserved |
| Feature-level PIT | PARTIAL | `audit_point_in_time()` fell back to row `available_at` for every feature | A future feature could inherit a safe row timestamp | P0 | Strict feature availability validation added |
| Historical feature builder | PARTIAL | Original builder used global shift/rolling and did not maintain team-specific prior histories | Cross-team contamination / temporal feature risk | P0 | Replaced with team-state prior-only builder |
| Odds snapshot | PARTIAL | Snapshot selection existed | Historical exact availability was not guaranteed | P0 | Strict timestamp handling + stale filtering + source evidence added |
| Market consensus | PARTIAL | `research/market.py` de-vigged groups but overround was aggregated incorrectly across bookmakers | Market probability could be mathematically distorted | P0 | Per-bookmaker/per-snapshot de-vig and aggregation rewritten |
| Backtest | PARTIAL | Basic simulation existed | Metrics/decision fields were incomplete | P1 | Expanded records and metrics |
| Research frontend | PARTIAL | Research pages rendered one generic status payload | Pages were not endpoint-specific | P1 | Pages now request their corresponding Research API endpoint |
| Research API | PARTIAL | Several endpoints returned static NOT AVAILABLE payloads | Limited research observability | P1 | Added datasets/experiments/validation/data-quality endpoints |
| Real historical data | MISSING | Bundle contained only 7 demo rows | No real OOS evidence possible | P0 external | Real-data adapters prepared; acquisition blocked by runtime network |
| Exact historical odds | MISSING in bundle | No timestamped historical odds source present | Exact PIT odds validation impossible | P0 external | The Odds API/Betfair adapters documented as external dependencies |
| Model selection | PARTIAL | Pipeline evaluated candidates but did not expose a persistent validation selection artifact | Research traceability incomplete | P1 | Experiment/reproducibility infrastructure strengthened |
| Holdout | IMPLEMENTED | `HoldoutGuard` state machine present | Runtime guard exists, but no real holdout exists | — | Preserved; no holdout evaluation performed |

## External limitation confirmed

The execution environment had no usable outbound network access from the project runtime. Attempts to download Football-Data CSVs failed at DNS/network resolution. No external data was fabricated or copied into the project.

## Final V14.1 interpretation

The project is materially more rigorous as an ingestion/PIT research base, but it is **not a real historical validation result**. The correct research status remains:

- REAL HISTORICAL DATA: NOT ACQUIRED IN RUNTIME
- REAL OOS: NOT AVAILABLE
- HOLDOUT EVALUATION: NOT AVAILABLE
- PROFITABILITY EVIDENCE: NOT AVAILABLE
