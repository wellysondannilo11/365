# Robo da Bet V16+ — Candidate Execution Status

This candidate is derived from the physically accessible `GLOBAL_DATASET_V8_COMPLETE.zip` artifact. The named V8 SHA supplied by the executive directive was **not re-bound to this candidate**; the original baseline remains immutable and is not overwritten.

## Scientific gates

- `REAL_MONEY = DISABLED`
- `EXACT_PIT` in the local canonical odds layer: 0
- Local Football-Data odds remain `NON_PIT` / `DATE_LEVEL_ONLY`.
- No current paper bet is promoted to a valid historical betting observation solely from those odds.
- A new explicit odds gate now separates existence, numeric validity, source verification, PIT verification, availability-at-decision, provenance and scientific eligibility.

## Engineering changes in this candidate

1. Added `ml/app/v16/odds_verification.py`.
2. Added `ml/app/v16/decision_dataset.py`.
3. Added `ml/app/v16/experiment_registry.py`.
4. Added regression tests for the new scientific gates.
5. Candidate audit identified a provider-semantics issue in `ml/app/adapters/odds.py`: provider `timestamp` is the selected historical snapshot clock and must not be rejected merely because nested `market.last_update` is later. The candidate patch removes that false rejection while retaining the snapshot clock as the PIT clock.

## Promotion rule

No candidate component is promoted to the baseline merely because tests pass. Promotion requires OOS + walk-forward + ablation + adversarial evidence.
