# Cycle 16 Recovery + Economic Execution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate the physical Cycle 15 candidate, strengthen the Exact PIT/H005/economic pipeline, exercise production controls, and deliver a complete Cycle 16 candidate without fabricating economic evidence.

**Architecture:** Keep the Cycle 15 namespace intact and add a focused `ml.app.cycle16` layer. The layer separates raw-source normalization, fail-closed PIT admission, frozen H005 signal generation, economic ledger/CLV/OOS analytics, acquisition probing, and promotion gating. Existing Cycle 15 code remains available for lineage and regression.

**Tech Stack:** Python 3, pandas, NumPy, pytest, standard-library hashing/JSON/CSV/pathlib/urllib.

**Spec:** CEO Cycle 16 recovery + physical delivery mandate in the active conversation.

## Global Constraints

- Baseline SHA: `608f587b628b8d09c961519e9ca3ec5a664dd68e3091de4c0371937a2adcd967`.
- H005 threshold remains exactly `0.02`.
- H005 reference remains `Average opening`; entry remains `Bet365 opening`.
- `DATE_LEVEL_PIT != EXACT_PIT`.
- `provider_timestamp <= decision_timestamp < kickoff_timestamp`.
- No `received_at`, download time, file time, or inferred timestamp may become provider time.
- Fixtures are test-only and never economic evidence.
- `REAL_MONEY = DISABLED`.

---

### Task 1: Harden Exact PIT contract

**Files:**
- Modify: `ml/app/cycle16/exact_pit.py`
- Create: `tests/cycle16/test_exact_pit_hardening.py`

- [ ] Write tests for missing required fields, invalid raw hash, provider-after-decision, decision-at-kickoff, and valid provider-native timestamp.
- [ ] Run the focused test file and confirm the new assertions fail against the old implementation where behavior differs.
- [ ] Implement deterministic classification with explicit `NON_PIT` for absent provider timestamp/evidence and `PIT_INVALID` for malformed/contradictory temporal records.
- [ ] Require provenance hash material and validate SHA-256 shape.
- [ ] Add `temporal_evidence` and `opening_semantics` fields without treating them as timestamps.
- [ ] Re-run the focused tests and the existing Cycle 16 PIT tests.

### Task 2: Build source ingestion and provenance layer

**Files:**
- Modify: `ml/app/cycle16/source_adapters.py`
- Create: `ml/app/cycle16/ingest.py`
- Create: `tests/cycle16/test_ingest.py`

- [ ] Write tests for SharpAPI CSV normalization, BeatTheBookie normalization, JSON/JSONL parsing, raw-file SHA propagation, and chunked CSV iteration.
- [ ] Run tests to verify RED.
- [ ] Implement streaming/chunked ingestion for CSV and line-oriented JSON plus ZIP member inspection.
- [ ] Normalize `sportsbook` correctly for SharpAPI and preserve source-native timestamps.
- [ ] Normalize BeatTheBookie `odds_datetime`, match date, bookmaker, market, selection and source record identifiers.
- [ ] Generate `raw_hash` from immutable source bytes when available and a deterministic `provenance_hash` from source metadata.
- [ ] Re-run focused ingestion tests.

### Task 3: Freeze H005 semantics

**Files:**
- Modify: `ml/app/cycle16/h005.py`
- Create: `tests/cycle16/test_h005_strict.py`

- [ ] Write tests proving H005 refuses rows lacking explicit opening semantics, accepts only EXACT_PIT, selects Bet365 entry rows, and uses exactly 2% threshold.
- [ ] Run tests RED.
- [ ] Implement strict matching of `Average` reference and `Bet365` entry at the same event/market/selection/opening snapshot.
- [ ] Reject single-snapshot datasets as H005 opening evidence instead of relabeling them.
- [ ] Preserve the frozen hypothesis identifier and threshold.
- [ ] Re-run focused tests.

### Task 4: Add economic ledger, settlement, CLV and temporal OOS analytics

**Files:**
- Create: `ml/app/cycle16/economic.py`
- Create: `tests/cycle16/test_economic.py`

- [ ] Write tests for paper bet creation, win/loss settlement, real CLV, unavailable CLV, chronological OOS split, and fold construction.
- [ ] Run tests RED.
- [ ] Implement flat-unit paper ledger with immutable decision IDs and source evidence references.
- [ ] Implement settlement from explicit result labels only; no result inference from odds.
- [ ] Implement real CLV only from a later provider snapshot and separate `CLV_PROXY`/`CLV_UNAVAILABLE`.
- [ ] Implement chronological train/validation/test and purged walk-forward helpers.
- [ ] Re-run focused tests.

### Task 5: Add statistical robustness and multiple-testing registry

**Files:**
- Create: `ml/app/cycle16/statistics.py`
- Create: `tests/cycle16/test_statistics.py`

- [ ] Write tests for bootstrap confidence intervals, drawdown, slippage/delay stress, and Holm-Bonferroni correction.
- [ ] Run tests RED.
- [ ] Implement deterministic bootstrap with seeded RNG.
- [ ] Implement sensitivity as reporting-only, never altering frozen H005.
- [ ] Implement multiple-testing registry with hypothesis IDs and correction metadata.
- [ ] Re-run focused tests.

### Task 6: Acquisition probing and operational controls

**Files:**
- Create: `ml/app/cycle16/acquisition.py`
- Create: `ml/app/cycle16/operations.py`
- Create: `tests/cycle16/test_acquisition_operations.py`

- [ ] Write tests for source registry, blocked DNS classification, retries/backoff configuration, idempotent raw persistence, health state, kill switch, and real-money lock.
- [ ] Run tests RED.
- [ ] Implement source registry entries for SharpAPI, BeatTheBookie, fabul0us/Hugging Face, The Odds API historical, Betfair historical, and prospective collection.
- [ ] Implement a runtime acquisition probe that records DNS/HTTPS/auth status without bypassing controls.
- [ ] Implement atomic raw persistence and idempotent observation keys.
- [ ] Implement health/heartbeat and hard real-money lock.
- [ ] Re-run focused tests.

### Task 7: End-to-end Cycle 16 runner and reports

**Files:**
- Modify: `ml/scripts/run_cycle16.py`
- Create/modify: `reports/cycle16/*`
- Create: `tests/cycle16/test_cycle16_runner_e2e.py`

- [ ] Write an offline integration test using test-only fixture data that exercises RAW → PIT → H005 → paper → settlement → CLV → OOS → statistics → promotion without mixing fixture results into production evidence.
- [ ] Run RED.
- [ ] Implement runner that scans `data/cycle16/raw` and `data/cycle16/incoming`, processes materialized sources in chunks, produces audit counts and keeps NON_PIT separate.
- [ ] Add all mandatory Cycle 16 artifacts and explicit statuses (`PROVEN`, `VERIFIED`, `EXECUTED`, `BLOCKED`, `INCONCLUSIVE`, `NOT_AVAILABLE`).
- [ ] Run the integration test and existing Cycle 15 regression tests.

### Task 8: Execute acquisition attempts and scientific evaluation

**Files:**
- Create: `reports/cycle16/CYCLE16_ACQUISITION_ATTEMPTS.json`
- Create: `reports/cycle16/CYCLE16_SOURCE_REGISTRY.json`
- Create: `reports/cycle16/CYCLE16_PIT_STATUS.json`
- Create: `reports/cycle16/CYCLE16_ECONOMIC_SUMMARY.json`

- [ ] Run the runtime acquisition probe against all configured legitimate routes.
- [ ] Process every locally materialized candidate source available in the workspace.
- [ ] Do not promote the existing 12,216 non-PIT odds rows.
- [ ] If no eligible Exact PIT source bytes exist, record exact route failures and preserve zero economic counts.
- [ ] If eligible bytes exist, execute H005 with frozen semantics and generate only evidence-backed paper bets.

### Task 9: Production infrastructure verification

**Files:**
- Modify: `ml/app/cycle16/operations.py`
- Create: `tests/cycle16/test_production_e2e.py`

- [ ] Test the offline operational state machine from raw arrival through audit/kill-switch/promotion.
- [ ] Run RED.
- [ ] Implement state transitions and failure recovery.
- [ ] Verify real-money lock remains impossible to bypass through the Cycle 16 path.
- [ ] Re-run operational tests.

### Task 10: Package, manifest, diff and final verification

**Files:**
- Create: `CYCLE16.diff`
- Create: `CYCLE16_MANIFEST.json`
- Create: `CYCLE16_EXECUTION_METADATA.json`
- Create: `CYCLE16_COMPLETENESS.json`
- Create: `CYCLE16_FINAL_DECISION.md`
- Create: `CYCLE16_EXECUTIVE_REPORT.md`

- [ ] Run `python -m compileall -q ml`.
- [ ] Run `pytest -q` and record collected/passed/failed/errors/timeout honestly.
- [ ] Compare the final tree against the Cycle 15 candidate and list created/modified/deleted files.
- [ ] Generate a unified diff against the Cycle 15 physical candidate tree.
- [ ] Generate complete candidate and code-delivery ZIPs.
- [ ] Compute SHA-256 for every required delivery artifact.
- [ ] Verify ZIP integrity with `unzip -t`.
- [ ] Produce final CEO decision without promoting non-PIT research.
