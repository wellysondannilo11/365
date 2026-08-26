# CICLO 16 — EXECUTIVE REPORT

## Physical recovery

- Source of truth for implementation: physical Cycle 15 archive.
- Source archive SHA-256: `3a3f72839901d84d833720187269b2bed57d9be5f8013b5011b1c7a0a66cc09d`.
- Protected V8 baseline SHA-256: `608f587b628b8d09c961519e9ca3ec5a664dd68e3091de4c0371937a2adcd967`.
- Prior Cycle 15 code/tests/reports were retained; Cycle 16 adds a separate namespace.

## Implemented

- Hardened fail-closed Exact PIT classifier.
- Immutable-file hashing and streaming CSV ingestion.
- SharpAPI and BeatTheBookie normalizers.
- Frozen H005 semantics requiring explicit opening evidence.
- Paper-bet/settlement/real-CLV ledger functions.
- Temporal OOS and walk-forward helpers.
- Bootstrap, drawdown, execution-stress and multiple-testing utilities.
- Acquisition source registry and runtime DNS/HTTPS probe.
- Operational health state and irreversible real-money lock.
- Cycle 16 reporting, manifests and audit outputs.

## Acquisition execution

Five legitimate historical routes were probed from the runtime: SharpAPI, BeatTheBookie, fabul0us/Hugging Face, The Odds API historical and Betfair historical. Runtime DNS failed for all five; no external bytes were counted as acquired.

The existing local Football-Data odds remain explicitly NON_PIT and were not promoted.

## Economic evidence

| Metric | Cycle 16 |
|---|---:|
| Exact PIT events | 0 |
| Exact PIT observations | 0 |
| Real paper bets | 0 |
| Valid CLV | 0 |
| OOS economic bets | 0 |
| Walk-forward folds | 0 |
| Net units | N.D. |
| ROI | N.D. |
| Max drawdown | N.D. |
| Edge | NOT_PROVEN |
| Real money | DISABLED |

## H005

`H005_CROSS_BOOK_DISPERSION_V1` remains frozen at **2%**, with **Average opening** as reference and **Bet365 opening** as entry. Snapshot-only sources are not relabeled as opening. With zero Exact PIT rows in the materialized candidate, H005 was not economically executed.

## Verification

- Cycle 16 tests: PASS.
- Cycle 15 targeted regression tests: PASS.
- `python -m compileall -q ml`: PASS.
- Full pytest collection: 289 tests.
- Full-suite command reached 99% before the environment timeout; no failure output was observed.
- The 289 collected tests were subsequently executed in smaller collection batches; each batch completed without test failures. Therefore the honest full-suite status remains `TIMEOUT`, not `100% PASS`.

## Decision

**C — INCONCLUSIVE / EDGE NOT PROVEN.**

The cycle materially strengthened the economic execution path and production controls, but the environment still contains no admissible provider-native historical Exact PIT batch. No economic metric was fabricated.
