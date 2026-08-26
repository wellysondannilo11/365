# ROBO DA BET V15 — FINAL ENGINEERING, QUANTITATIVE & REGRESSION AUDIT

## Executive status

**V15 was implemented on top of the supplied V14.2 architecture. No parallel application was created.**

The project remains **LEVEL 1 — infrastructure complete without real historical evidence**. This is intentional: the bundled dataset is still DEMO and does not contain sufficient real historical timestamped odds/event data to support a defensible real OOS, holdout, ROI or CLV claim.

## V15 objectives completed

- Atomic event-aware temporal splitting.
- Holdout allocation by unique event, not raw rows.
- Walk-forward fold boundaries that cannot split one event across partitions.
- Row-level PIT support for odds/prediction values whose availability is represented by the record-level `available_at` clock.
- Event-cluster bootstrap for betting ROI uncertainty.
- ROI definition changed to profit / total stake; bankroll return is reported separately.
- The Odds API historical snapshot normalizer with an explicit provider timestamp requirement.
- API/backend version alignment to 15.0.0.
- Backend Docker build corrected to compile the application and copy the actual V15 artifact instead of relying on a missing stale JAR.
- Additional regression and negative tests.
- Documentation updated to state V15 controls and evidence limitations.

## Quantitative audit

### Point-in-Time

The system rejects `available_at > decision_time`, future source timestamps, ingestion-before-source anomalies, and feature-level availability violations. Historical feature construction remains prior-only and requires an explicit outcome/statistics availability timestamp before a completed match can enter historical state.

### Temporal validation

`event_id` is now the atomic temporal unit. If an event has multiple rows (bookmakers, markets, selections), all rows remain in the same temporal partition. An event identifier with inconsistent event timestamps is rejected instead of being silently split.

### Model selection

The research pipeline selects a champion using validation data and evaluates that champion on the test window. The final holdout remains locked and is not used for model selection, calibration or threshold tuning.

### Betting performance

`roi = total_profit / total_stake`.

`bankroll_return = total_profit / initial_bankroll`.

These are intentionally reported separately so a large initial bankroll does not dilute the definition of betting ROI.

### Uncertainty

The betting bootstrap resamples **events**, not individual bets. This prevents multiple bets attached to one match from being incorrectly treated as independent observations.

## Regression audit

### Regression/risk found and corrected

1. **Backend Docker artifact mismatch** — the previous Dockerfile attempted to copy `target/robobet-api-10.0.0.jar` while the Maven project version was different and no target artifact was shipped. V15 uses a multi-stage Maven build and copies the V15 artifact.
2. **Event splitting risk** — row-index temporal folds could split a multi-row event. V15 makes event groups atomic.
3. **Holdout sizing risk** — holdout was previously calculated by rows. V15 calculates it by unique events.
4. **Metric semantics** — the former `roi` represented profit divided by initial bankroll while `yield` represented profit divided by stake. V15 makes ROI the stake-based metric and retains bankroll return separately.
5. **Historical odds normalization gap** — V15 adds a strict historical snapshot normalizer that requires an actual provider snapshot timestamp and never substitutes kickoff/result time.
6. **Version drift** — API and Maven versions are aligned to 15.0.0.

### Risks that remain documented

- The environment used for this delivery does not provide Maven or Docker, so the Java/Docker image was not executed locally.
- The frontend dependencies were not successfully installed/build-validated in the delivery environment; the existing architecture remains intact and the backend Docker build is now self-contained.
- Production endpoints do not yet implement authentication/authorization. This remains a deployment security gate and the system should stay behind trusted infrastructure until that is addressed.
- Real historical provider credentials/data are absent. No profitability evidence is inferred from synthetic fixtures.

## Validation executed

- `pytest -q`: **44 passed**.
- Python `compileall`: **PASS**.
- Existing self-test: **PASS**.
- Controlled walk-forward fixture: **PASS**.
- Multi-row event temporal isolation: **PASS**.
- Negative PIT tests: **PASS**.
- Cluster bootstrap tests: **PASS**.
- Historical odds timestamp normalization tests: **PASS**.

## Not claimed

The project does **not** claim:

- real profitability;
- real positive ROI;
- real CLV edge;
- OOS superiority;
- holdout superiority;
- statistically proven betting edge;
- live validation.

Those remain **NOT AVAILABLE — INSUFFICIENT REAL DATA**.

## Final level

**LEVEL 1 — Infrastructure complete without real historical evidence.**

The next level requires actual provider data with legally usable historical timestamps and successful execution of the real-data PIT/OOS/holdout pipeline.
