# ROBO DA BET — MASTER RESEARCH REPORT

## Current classification

**LEVEL 1 — Infrastructure complete, without real historical evidence.**

## Research question

The system is now structured to test whether model probabilities add information beyond simple baselines and market prices while enforcing point-in-time constraints. It has not yet answered that question on real historical data in this runtime.

## Current evidence

- 35 automated Python tests pass.
- Self-test passes.
- Compile/import checks pass.
- FastAPI smoke tests pass.
- Deliberate future-feature leakage is rejected.
- Synthetic pipeline smoke test passes.

None of these is evidence of betting profitability.

## Real data status

No real dataset was available inside the V14 ZIP and external network access from the runtime was unavailable. The project therefore contains adapters and validation infrastructure, not fabricated historical results.

## Required next real-data package

At minimum:

- multi-season fixtures/results;
- canonical team/competition/season identifiers;
- exact event timestamps where available;
- historical odds snapshots with exact timestamps and bookmaker IDs;
- market/selection/line;
- source record IDs and raw hashes;
- enough observations to support temporal OOS and a locked final holdout.

## Required acceptance criteria

A real-data run should not be labeled quantitatively validated unless:

1. PIT leakage audit is clean.
2. Baselines are evaluated.
3. Model selection is frozen before final holdout.
4. Calibration is fit only on allowed historical validation data.
5. Test is OOS and untouched by selection.
6. Holdout remains locked until final evaluation.
7. Decisions are reproducible from stored snapshot/lineage information.
8. Bootstrap confidence intervals and multiple-testing controls are reported.
9. Results are stable enough across periods/markets to justify further paper trading.
10. No known leakage or survivorship/selection contamination remains.

## Profitability

`NOT AVAILABLE`.

No ROI, CLV, edge or profit figure from the 7-row demo dataset is used as evidence.
