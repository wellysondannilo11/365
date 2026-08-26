# ROBO DA BET V16+ — EXECUTION REPORT

Date: 2026-08-24
Mode: Candidate / Research Only
REAL_MONEY: DISABLED
EDGE: NOT_PROVEN

## 1. Execution truth

The execution used the physically accessible `GLOBAL_DATASET_V8_COMPLETE.zip` as the working research artifact. The supplied named V8 SHA was not overwritten or rebound to this candidate. The candidate is therefore **not the baseline** and is not a promotion of the baseline.

The Library contains substantial later/recovered V8/V10/V11/V17–V25 artifacts. Historical reports explicitly state that later components must remain isolated until the physical golden baseline can be independently compared and regression-tested.

## 2. Baseline/data evidence

Accessible canonical dataset:
- 8,523 canonical matches.
- 12,216 processed historical odds rows in the dedicated non-PIT odds layer.
- 5,160 matches with shots/SOT enrichment.
- Exact PIT odds: 0.
- Decision timestamps in canonical dataset: 0 populated rows.
- Canonical PIT status: 7,321 NON_PIT; 1,172 UNKNOWN; 30 PIT_DATE_ONLY.

The 12,216-row odds layer has zero `odds_timestamp` values and is explicitly classified `NON_PIT`.

## 3. P0 executed

### Odds verification hardening

Added:
- `ml/app/v16/odds_verification.py`

Explicit gates:
- ODDS_EXISTS
- ODDS_NUMERICALLY_VALID
- ODDS_SOURCE_VERIFIED
- ODDS_PIT_VERIFIED
- ODDS_AVAILABLE_AT_DECISION
- ODDS_PROVENANCE_VERIFIED
- ODDS_SCIENTIFICALLY_ELIGIBLE

Local non-PIT odds cannot pass the scientific eligibility gate.

### Decision dataset

Added:
- `ml/app/v16/decision_dataset.py`

It freezes event/decision time, market, price, source timestamps, features, versions, probability, fair price, EV, realistic EV, gates, stake, decision and provenance.

### Decision replay

Added:
- `ml/app/v16/decision_replay.py`

Replay requires:
- decision_id
- decision_time
- dataset_version
- feature_version
- model_version

It produces a deterministic replay hash and explicitly fails when required metadata is absent or replay is non-reproducible.

### Experiment registry

Added:
- `ml/app/v16/experiment_registry.py`

Every recorded experiment carries hypothesis, baseline, change, dataset, train/validation/OOS periods, metrics and promotion status.

## 4. Provider semantics correction

The accessible The Odds API adapter contained a temporal validation problem: it treated nested bookmaker/market `last_update` clocks as if they were the historical snapshot selector. The provider snapshot timestamp must remain the PIT clock; nested update timestamps are retained as metadata.

The candidate removes the false rejection while retaining the scientific requirement:

`provider snapshot/source timestamp <= decision_time`

This does **not** create Exact PIT data. It only prevents a valid provider snapshot from being rejected for the wrong reason.

## 5. Tests

Full candidate test suite:

**235 tests passed.**

Also executed:
- Python compilation: PASS.
- New V16 scientific gate tests: PASS.
- Decision replay reproducibility tests: PASS.
- Existing regression suite: PASS.

## 6. First quantitative intelligence benchmark

A chronological market-implied 1X2 predictive benchmark was executed on the accessible canonical dataset.

OOS sample: 1,425 matches.

Results:
- Accuracy: 48.9123%
- Brier: 0.616262
- Log Loss: 1.025660

Important: this is a **prediction benchmark only**. It is NOT betting ROI evidence because the canonical odds are not proven Exact PIT.

## 7. Betting benchmark status

| Metric | Result |
|---|---:|
| Exact PIT odds | 0 |
| Timestamped bookmaker observations scientifically verified | 0 |
| Scientific betting decisions | 0 |
| Valid paper bets from historical PIT | 0 |
| Settlements | 0 |
| CLV | NOT_AVAILABLE |
| ROI OOS | NOT_DETERMINED |
| Units OOS | NOT_DETERMINED |
| Monthly forecast | NOT_DETERMINED |
| Edge | NOT_PROVEN |
| Real money | DISABLED |

## 8. Why betting ROI was not fabricated

The local historical Football-Data odds are opening/closing/reference observations without decision-time availability proof. The project policy explicitly prohibits promotion of those observations to Exact PIT.

Therefore no ROI, units, CLV or monthly profitability claim was generated from them.

## 9. Remaining blockers

### BLOCKED_EXTERNAL
- Real historical bookmaker snapshot acquisition requires a source with timestamped historical snapshots and valid access.
- API-Football / StatsBomb / other provider acquisition remains dependent on external access/keys where applicable.

### INSUFFICIENT_DATA
- Exact PIT odds.
- Real timestamped bookmaker observations.
- Historical CLV.
- Valid historical paper-bet population.
- Settled historical paper-bet population.

### DOCUMENTED_ONLY / RESEARCH_ONLY
- Advanced model comparisons and betting promotion remain research-only until PIT is available.
- Date-level shots/SOT remain usable for carefully lagged feature research but are not automatically PIT-safe.

## 10. Promotion decision

`KEEP BASELINE`

The candidate is **not promoted** merely because the engineering tests pass.

Promotion requires:

`OOS + WALK_FORWARD + ABLATION + ADVERSARIAL + REPRODUCIBILITY`

and, for betting claims, a valid Exact PIT price population.

## 11. Candidate artifact

`ROBO_DA_BET_V16_CANDIDATE_2026-08-24.zip`

The final ZIP SHA-256 is recorded outside the ZIP in the execution manifest to avoid a self-referential archive hash.

## 12. Executive conclusion

The first execution cycle materially improved the **evidence controls**, not the claimed profitability.

The Robo is now stricter about what may qualify as a scientific betting observation, and the provider adapter has been corrected for the documented snapshot/update semantic mismatch.

However:

**EDGE remains NOT_PROVEN.**

The next scientifically decisive step remains acquisition of real Exact PIT bookmaker snapshots. Until that exists, any claim of historical betting ROI, CLV or monthly profit would be unsupported.
