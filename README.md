# ROBO DA BET — FINAL CONSOLIDATION V26–V28

This package is the final engineering consolidation of the supplied V25 baseline. It does **not** create V29/V30/V31. The engineering objective is closed; subsequent improvement is driven by real observations and scientific evidence.

## Scientific boundary
- Real-money execution is disabled.
- Fake/demo/replay data is engineering evidence only.
- `EDGE = NOT DETERMINED` until sufficient real PIT observations, settlements and validation exist.
- `source_timestamp`, `captured_at`, `received_at`, `decision_time` and `commence_time` remain distinct.
- Raw observations are persisted separately from decisions/settlements.

## Operational flow
`REAL PROVIDER → EVENTS/ODDS → RAW SNAPSHOT → QUALITY/PIT → PRICING → MARKET EXPRESSION → BET/NO BET/WATCH/WAIT → PAPER/SHADOW → POSITION → SETTLEMENT → CLV → DATASET → ANALYTICS`

## Real provider
The existing The Odds API adapter is retained. It uses the authorized API key from `THE_ODDS_API_KEY`, retries transient errors, tracks provider health/rate-limit headers, and fails closed on missing credentials or invalid timestamps. The provider's current odds API covers live and upcoming events, while its scores API supplies score/result state; the system keeps these data paths separate and never substitutes `commence_time` for an observation timestamp.

## Persistence
- PostgreSQL is the primary empirical store when configured/reachable.
- `v25_observation_snapshots` stores raw point-in-time market observations.
- `v25_dataset_rows` stores auditable decisions/settlements.
- JSONL remains a forensic mirror/fallback only.
- Redis is ephemeral state/cache/health only; it is never the historical source.

## Observation runner
```bash
PYTHONPATH=ml python scripts/run_observation.py --mode SHADOW --interval 30
```
Use `--mode PAPER` only for simulated paper positions. There is no real-money execution path.

The runner records database/Redis/provider health, persists raw snapshots, reconstructs operational risk/open positions after restart, and stops safely when the provider credential is unavailable.

## Local regression
```bash
PYTHONPATH=ml pytest -q
python -m compileall -q ml scripts tests
PYTHONPATH=ml python scripts/self_test.py
cd frontend && npm test
cd frontend && npm run build
```
The frontend production build requires installed npm dependencies; if the environment cannot install them, it remains BLOCKED rather than being marked PASS.

## Current scientific status
This package contains **no real provider observations from the audit environment** because `THE_ODDS_API_KEY` was not available. Therefore:
- real events = 0
- real snapshots = 0
- real BETs = 0
- real ROI = NOT DETERMINED
- real CLV = NOT DETERMINED
- real edge = NOT DETERMINED

The next phase is historical-real byte materialization followed by the temporal empirical protocol; no new software version is required.

## Auditoria final operacional
A última auditoria não criou uma nova versão. Foram corrigidos diretamente no pacote: passagem das credenciais do provider/Telegram no Compose, healthcheck/ordenação do Redis, healthcheck parametrizado do PostgreSQL, referência do JAR Spring e fail-closed do runner quando a infraestrutura primária está indisponível.

No ambiente desta auditoria não havia `THE_ODDS_API_KEY`, PostgreSQL ou Redis; portanto a observação real não foi iniciada. O runner bloqueou corretamente e nenhum dado sintético foi contado como real.

## Card Markets extension

Card markets are integrated into the V25 quantitative architecture through a provider-agnostic card feature/model layer and the existing Market Expression / decision conventions. Supported market identifiers are `CARD_TOTALS`, `CARD_HOME`, and `CARD_AWAY`, with OVER/UNDER and integer/half/quarter settlement handling.

The card model is deliberately fail-closed. It requires observed referee/team/H2H inputs with sample sizes and source lineage; it never fabricates referee or team-card statistics. The baseline Poisson/Negative-Binomial selector and default feature weights are **engineering baselines, not empirical evidence** and must be calibrated on real, point-in-time data before any scientific promotion.

The current real-data status remains unchanged unless an external provider supplies the required credentials and card data. Missing card-data sources are `BLOCKED`/`NOT DETERMINED`; fixtures and controlled E2E tests are not empirical evidence.

### Card data-provider boundary

A provider-neutral `CardDataProvider` contract is included. An optional API-Football implementation can retrieve referee/match card events when `API_FOOTBALL_KEY` is supplied. The adapter explicitly marks its availability evidence as `CAPTURED_AT_ONLY`; it does **not** claim exact historical publication timestamps. Therefore it cannot by itself prove historical PIT for a past decision unless the surrounding acquisition process captured the source before that decision.

## Final empirical-validation pass

This final pass remained football-only and did not create a new version. A quantitative defect in the Card Markets implementation was corrected: `CARD_HOME` and `CARD_AWAY` no longer inherit the same total-card expectation used by `CARD_TOTALS`; LIVE card observations are side-aware; card PIT now checks capture timestamps as well as source timestamps.

Local regression after the correction: 164/164 Python tests PASS, frontend 2/2 PASS, compileall PASS, self-test PASS, API smoke PASS, security scan PASS.

Public historical research confirmed that Football-Data.co.uk contains real football results, bookings, referees and historical odds. Its odds files do not establish exact publication timestamps for every quote, so they cannot by themselves provide strict betting PIT. API-Football exposes fixture card events but requires credentials and its current adapter only proves capture time, not historical publication time.

Accordingly the final scientific status remains LEVEL 2: ready for real observation, not empirically validated for profitability. Real events/snapshots/decisions/settlements remain zero in this audit runtime; ROI, CLV, OOS, holdout and edge remain NOT DETERMINED.

## Global Football Research Execution

The current research package preserves the existing architecture and adds a global football acquisition/research layer under `scripts/run_global_research.py`, `reports/phase3/`, `data/manifests/`, and `data/canonical/CANONICAL_RESEARCH_SCHEMA.md`.

Important scientific rule: source discovery is never counted as processed evidence. Only successfully materialized bytes enter `HISTORICAL_REAL` or `LIVE_REAL`. The runtime used for this execution could not resolve external hosts, so the empirical dataset remains limited to the 40 real rows already present in the package. `REAL_MONEY` remains disabled.

## Specialist+ Intelligence Engine

The package now contains a version-neutral `ml/app/intelligence/` layer rather than a new V29/V30/V31/V32 release. It adds:
- strict evidence/provenance classes and PIT states in `ml/app/intelligence_evidence.py`;
- a stateful LIVE engine with timestamp ordering, stale-feed rejection, match-state classification, tempo and pressure diagnostics in `ml/app/intelligence/live.py`;
- a fail-closed LIVE pricing layer in `ml/app/intelligence/pricing.py`;
- an explicit football market catalog covering result, goals, BTTS, handicap, cards, corners, next-event and player-market families;
- a global competition coverage registry spanning the requested regions/divisions without treating the registry as empirical evidence;
- provider-neutral acquisition adapters for The Odds API, API-Football and Sportmonks;
- a unified `FootballIntelligencePipeline` that requires PIT, verified price, validated model and minimum sample before returning BET;
- an executable global acquisition audit at `scripts/run_global_intelligence.py` that records actual acquisition outcomes, hashes materialized bytes and never labels discovery as processed evidence.

### Acquisition execution result
The specialist+ acquisition runner was executed against the latest ZIP in the library. The runtime had no external DNS/network resolution, so all 11 attempted external routes failed with their actual runtime error. No new external bytes were counted, and no synthetic data was promoted. The existing package evidence remains unchanged.

`FOUND=11`, `ACQUIRED=0`, `MATERIALIZED=0`, `PROCESSED_NEW=0`, `PIT_VALIDATED_NEW=0`, `USED_IN_MODEL_NEW=0`.

The implementation is therefore **code-complete for the new orchestration and integrity controls, but not empirically validated for global coverage or profitability** until real provider credentials/network access and timestamped datasets are supplied.

## Master Staff — Value Pricing + Context Intelligence (2026-08-20)
This package was evolved in-place from the latest Library package; no artificial V29/V30/V31/V32 project was created and no historical canonical rows were replaced.

### Evidence-state contract
`FOUND` is source discovery only. `DOWNLOADED`/`ACQUIRED` requires bytes. `MATERIALIZED` requires locally persisted bytes. `PROCESSED` requires successful parsing/canonicalization. `PIT_VALIDATED` requires a defensible observation timestamp at or before decision time. `USED_IN_MODEL` requires explicit feature/model admission. Missing evidence stays `UNKNOWN`, `INSUFFICIENT_DATA`, or `UNVERIFIED`.

### New in-place capabilities
- temporal H2H windows 3/5/10/20 with prior-only construction;
- rest/congestion features from prior match timestamps;
- rivalry registry with fail-closed empirical status;
- player/injury/suspension/lineup/live schemas with empty evidence-safe datasets;
- independent value-pricing gate with EXACT/VALID PIT enforcement;
- target coverage registry for major/lower-tier and women competitions, without treating routes as materialized evidence;
- acquisition audit and final provenance/hash manifests;
- round-analysis reference pricing that can produce `WATCH` but never promotes DATE_LEVEL_PIT to `VALUE_BET`;
- 24h/LIVE architecture remains fail-safe and `REAL_MONEY=DISABLED`.

### Execution boundary
The runtime attempted the expanded historical acquisition registry. External DNS resolution was unavailable, so **0 new external bytes were materialized**. The 4,864 existing real canonical matches were preserved exactly. Public sources were recorded as `FOUND`/reference only. StatsBomb Open Data provides selected competitions with matches/events/lineups; The Odds API documents timestamped historical snapshots, but access requires the applicable historical-data plan. These facts do not mean their bytes were acquired in this run.

### Current scientific status
- `REAL_MATCHES=4864`
- `NEW_REAL_DATA_MATERIALIZED=0`
- `PIT_VALIDATED=0`
- `LIVE_SNAPSHOTS=0`
- `SETTLEMENTS=0`
- `EDGE=NOT_DETERMINED`
- `REAL_MONEY=DISABLED`

The next empirical step is to run the same acquisition layer in an environment with outbound DNS/network access and the required provider credentials, then re-run PIT, leakage, calibration, OOS, holdout, walk-forward and market backtests. No engineering state should be promoted to scientific evidence merely because a route exists.
