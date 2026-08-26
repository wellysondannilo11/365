# Robo da Bet V16+ Cycle 2 Intelligence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a reproducible research runner that quantifies whether V16 intelligence improves prediction quality and theoretical opportunity quality without claiming non-PIT betting performance.

**Architecture:** A single research module consumes the existing canonical historical dataset, creates chronology-safe prior-event features, evaluates model families on expanding OOS folds, and writes machine-readable result artifacts. Existing PIT/replay modules remain unchanged and are used as scientific gates rather than bypassed.

**Tech Stack:** Python, pandas, NumPy, scikit-learn, pytest.

**Spec:** `docs/superpowers/specs/2026-08-24-robo-v16-cycle2-intelligence-design.md`

## Global Constraints
- Baseline SHA remains `608f587b628b8d09c961519e9ca3ec5a664dd68e3091de4c0371937a2adcd967` and immutable.
- Candidate SHA at cycle start is `c1b8b0ef76be571f5be479871cb6d385325e5546e7030a013f11c6dd7ea3db66`.
- `REAL_MONEY = DISABLED`.
- `EXACT_PIT = 0` unless fresh evidence proves otherwise.
- Non-PIT odds cannot be labeled validated ROI, CLV, or edge.

### Task 1: Research runner contracts
**Files:** Create `tests/research/test_cycle2.py`, Create `ml/app/research/cycle2.py`
- [ ] Write failing tests for chronology-safe feature generation, model result schema, no-PIT classification, and odds normalization.
- [ ] Run the focused tests and verify they fail for the intended missing-module reasons.
- [ ] Implement the minimal data structures and helpers.
- [ ] Run focused tests and verify they pass.

### Task 2: Chronological feature and target construction
**Files:** Modify `ml/app/research/cycle2.py`, Test `tests/research/test_cycle2.py`
- [ ] Add prior-event rolling features for Elo delta, recent goals, form, rest, shots, SOT, corners, and cards.
- [ ] Build targets for home win, over 2.5 goals, BTTS, and research-only high-total event targets when source fields exist.
- [ ] Add explicit feature lineage/status fields.
- [ ] Test that current-event goals are never present in generated predictors.

### Task 3: Walk-forward model benchmark
**Files:** Modify `ml/app/research/cycle2.py`, Test `tests/research/test_cycle2.py`
- [ ] Add market-only, logistic, random forest, gradient boosting, histogram gradient boosting, and ensemble candidates.
- [ ] Select champions using validation only; evaluate once on each OOS test fold.
- [ ] Preserve a final locked holdout.
- [ ] Record accuracy, log loss, Brier, ECE/MCE, ROC-AUC where binary metrics are defined.

### Task 4: Calibration and ablation
**Files:** Modify `ml/app/research/cycle2.py`, Test `tests/research/test_cycle2.py`
- [ ] Compare raw, Platt, and Isotonic calibration using validation-only fitting.
- [ ] Run baseline, market, form, shots/SOT, corners, cards, momentum/rest, and market-intelligence feature sets where data exists.
- [ ] Classify each component KEEP/RESEARCH/REMOVE/NOT_ELIGIBLE based on OOS evidence.

### Task 5: Pricing, divergence, odds buckets, sizing, volume
**Files:** Modify `ml/app/research/cycle2.py`, Test `tests/research/test_cycle2.py`
- [ ] Calculate normalized market probabilities from available non-PIT prices.
- [ ] Calculate research-only fair odds, raw EV, realistic EV, and uncertainty-adjusted EV.
- [ ] Bucket opportunities by requested odds ranges.
- [ ] Simulate 0.25U/0.50U/1U/1.5U/2U sizing under explicit counterfactual assumptions, never calling it OOS betting validation.
- [ ] Record approved/watch/rejected/insufficient-data counts and rates.

### Task 6: Execute and publish Cycle 2 artifacts
**Files:** Modify `ml/scripts/run_v16_research.py` or add `ml/scripts/run_cycle2.py`; Create `reports/cycle2/*`
- [ ] Add a deterministic CLI entry point with input path, output directory, and seed.
- [ ] Run the full Cycle 2 research on `data/canonical/football_historical_real_canonical.csv`.
- [ ] Write all CSV/JSONL artifacts and executive report.
- [ ] Run the full pytest suite and record exit code.
- [ ] Verify baseline ZIP SHA and candidate start SHA are unchanged in provenance records.
