# V25 Pre-Implementation Audit — V24 Baseline

## Scope

The real V24 archive was extracted and inspected before V25 changes. Inventory covered Python/ML, FastAPI, Spring proxy, React/Vite frontend, PostgreSQL migrations, Redis configuration, Docker Compose, feed adapters, pricing, selection, live, paper/shadow, dataset, replay, ledger, notifications, XLSX, tests and documentation.

| Component | Status | Implemented? | Integrated? | Tested? | E2E? | Real data? | Risk | Action |
|---|---|---:|---:|---:|---:|---:|---|---|
| Python/ML | PARTIAL | YES | YES | YES | PARTIAL | NO | Medium | Consolidate V25 decision path |
| Backend | PARTIAL | YES | YES | YES | PARTIAL | NO | Medium | Add V25 routes and validate |
| Frontend | PARTIAL | YES | V24 | LIMITED | NO | NO | Medium | Wire V25 endpoints |
| PostgreSQL | PARTIAL | Schema YES | Runtime NO | Migration files only | NO | NO | High | Add V25 migration; runtime remains external |
| Redis | PARTIAL | Config YES | Runtime NO | Unit-level | NO | NO | Medium | Add explicit V25 health adapter |
| Real feed | READY/BLOCKED | YES | V24 | Provider unit tests | NO | NO | High | Preserve PIT and fail closed |
| Pricing | YES/PARTIAL | YES | YES | YES | YES fixture | NO | Medium | Add MarketExpressionEngine |
| Asian Handicap | PARTIAL | YES | PARTIAL | Existing tests | PARTIAL | NO | High | Correct quarter-line semantics |
| Live | PARTIAL | YES | V24 live snapshot | YES | Fixture | NO | High | Add V25 live reprice path |
| PAPER | YES | YES | YES | YES | Fixture | NO | Medium | Add position/settlement lineage |
| SHADOW | YES | YES | YES | YES | Fixture | NO | Medium | Preserve separation |
| Dataset | YES | YES | YES | YES | YES fixture | NO | Medium | V25 hash-chain dataset |
| Replay | YES | YES | YES | YES | Fixture | NO | Medium | Preserve deterministic replay |
| Telegram | PARTIAL | YES | Existing V20 | Unit | NO real | NO | Medium | V25 idempotent provider |
| XLSX | YES | YES | YES | YES | Fixture | NO | Low | Expand V25 tabs |
| Observability | PARTIAL | YES | V24 | YES | NO | NO | Medium | Add V25 infra health |
| Docker | CONFIGURED | YES | YES | NOT EXECUTED | NO | NO | High | External Docker required |
| Spring/Maven | CONFIGURED | YES | YES | NOT EXECUTED | NO | NO | High | Maven unavailable |

## Material V24 gaps found

1. V24's real decision session was still primarily a market-only baseline rather than an explicit multi-market expression engine.
2. Existing Asian Handicap probability logic did not correctly decompose quarter lines such as `-0.25` and `+0.75`.
3. Existing V24 live state stored snapshots but did not itself provide a complete V25 market-expression repricing layer.
4. Price discovery lacked a consolidated opening/current/velocity/acceleration/divergence abstraction.
5. Position settlement needed append-only dataset lineage instead of mutating the original decision row.
6. V24 frontend remained wired to V24 endpoints.
7. PostgreSQL/Redis existed in the architecture but were not proven runtime-connected in the available environment.
8. Real The Odds API observation was blocked by absent credentials.
9. Model infrastructure existed, but the V24 real observation session did not automatically feed a trained model into final pricing; this was retained as an explicit scientific boundary rather than fabricated.

## Rule applied

Every gap that could be safely implemented without replacing V24 architecture was implemented in V25. External-runtime limitations remain marked BLOCKED/NOT EXECUTED.
