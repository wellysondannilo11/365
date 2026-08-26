# Cycle 15 Exact PIT & Economic Research Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a fail-closed Exact PIT ingestion/economic research path, H005 evaluation, and prospective collection without fabricating evidence.

**Architecture:** Keep legacy cycle modules immutable and add a focused `cycle15` package. Adapters normalize provider-native snapshots into a canonical observation contract; the PIT gate requires provider timestamp, kickoff, provenance and raw hash. Economic research consumes only admitted PIT rows, while NON_PIT research remains explicitly segregated.

**Tech Stack:** Python, pandas, requests, pytest, JSON/CSV artifacts.

**Spec:** CEO Cycle 15 mandate in conversation.

## Global Constraints

- Never promote date-level timestamps to Exact PIT.
- Never use `received_at` or file modification time as provider timestamp.
- REAL_MONEY remains DISABLED.
- V8 baseline remains immutable.
- Economic metrics from NON_PIT data are research-only.

---

### Task 1: Canonical Exact PIT contract

**Files:**
- Create: `ml/app/research/cycle15/pit.py`
- Test: `tests/research/test_cycle15_pit.py`

- [ ] Write failing tests for timestamp ordering, provenance, raw hash, kickoff and date-only rejection.
- [ ] Run the tests and confirm failure.
- [ ] Implement the minimal canonical validator/classifier.
- [ ] Run the tests and confirm pass.

### Task 2: Historical snapshot adapters

**Files:**
- Create: `ml/app/research/cycle15/sources.py`
- Test: `tests/research/test_cycle15_sources.py`

- [ ] Test SharpAPI-shaped CSV normalization.
- [ ] Test BeatTheBookie long-form normalization.
- [ ] Test chunked CSV processing.
- [ ] Implement adapters and source registry metadata.

### Task 3: H005 economic evaluator

**Files:**
- Create: `ml/app/research/cycle15/h005.py`
- Test: `tests/research/test_cycle15_h005.py`

- [ ] Test exact 2% rule and settlement calculation.
- [ ] Test PIT-only admission.
- [ ] Test research-only NON_PIT segregation.
- [ ] Implement frozen H005 evaluator and bootstrap utility.

### Task 4: Prospective collector and production gate

**Files:**
- Create: `ml/app/research/cycle15/prospective.py`
- Create: `ml/app/research/cycle15/production.py`
- Test: `tests/research/test_cycle15_operational.py`

- [ ] Test missing credentials fail closed.
- [ ] Test raw persistence/hash/provenance.
- [ ] Test production trading lock remains disabled.
- [ ] Implement collector and operational gate.

### Task 5: Cycle runner and artifacts

**Files:**
- Create: `ml/app/research/cycle15/run_cycle15.py`
- Create: `tests/research/test_cycle15_runner.py`

- [ ] Test artifact generation from local candidate data.
- [ ] Implement source inventory, PIT population, H005 research-only analysis, and all requested C15 artifacts.
- [ ] Run targeted tests.
- [ ] Run compileall and project regression suite.
- [ ] Package candidate and diff.
