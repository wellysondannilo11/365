# ROBO DA BET V13 — Quant Research

## Status
V13 adds a research-grade temporal validation layer, immutable raw-record contract, historical feature builders, bookmaker/market consensus primitives, nested temporal validation, OOS calibration separation, statistical bootstrap/multiple-testing helpers, holdout state machine, decision replay primitives and a separated backtest engine.

## Evidence status
- Bundled dataset: DEMO, 7 rows. **Not evidence**.
- Historical odds: schema/adapters supported, but real historical provider data is **NOT AVAILABLE** in the bundle.
- Real OOS backtest: **NOT AVAILABLE**.
- Final holdout: contract/guard exists; no real holdout evaluation has been performed.
- Profitability: **NOT AVAILABLE**.
- Maven: **NOT TESTED** in this environment.
- Docker: **NOT TESTED** in this environment.
- Frontend build: **NOT TESTED** in this environment.

## Point-in-time rule
A row/feature is eligible only when `available_at <= decision_time`. The V13 validator also rejects `source_time > decision_time`, invalid timestamps, and ingestion before source publication.

## Model layers
SPORT_ONLY, MARKET_ONLY and HYBRID remain explicit. No layer is treated as superior without OOS comparison against historical baselines.

## Calibration
Calibration must be fitted on validation data and applied to an untouched test period. V13 exposes Isotonic and Platt helpers and reliability metrics. Small samples are not silently treated as calibrated.

## Backtest
The backtest engine consumes probabilities and odds available at decision time. Closing odds are only used for CLV when present.

## Live
The current live signal remains a heuristic until historical live event data exists. It must not be represented as a validated probability model.
