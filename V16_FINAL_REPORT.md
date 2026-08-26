# ROBO DA BET V16 — FINAL QUANTITATIVE, ENGINEERING & SCIENTIFIC REPORT

## Executive verdict

**🟡 SAFE WITH LIMITATIONS**

V16 preserves the V15 architecture and adds the empirical real-data layer, but the environment did not contain provider credentials or a real historical PIT odds dataset and had no outbound network/DNS access for acquisition. Therefore V16 cannot honestly claim a real betting backtest, OOS edge, CLV or profitability.

## Implemented

- Real-data quality gate.
- Strict provider-timestamp historical odds normalization.
- The Odds API historical event/snapshot methods.
- TheStatsAPI documented football match endpoint adapter.
- Expanded temporal football features.
- Empirical temporal runner.
- Dataset fingerprinting.
- Robustness grouping and EV threshold sensitivity.
- Paper-trading signal ledger.
- Optional API-key authentication gate.
- Frontend/backend version alignment.
- Docker Compose syntax correction.
- V15 regression audit and corrections.

## Validation executed

- `pytest -q`: **49 passed**.
- `python -m compileall -q ml/app`: **PASS**.
- `python scripts/self_test.py`: **PASS**.
- `python -m ml.scripts.run_self_test`: **PASS**.
- Docker Compose YAML parse: **PASS**.
- Negative PIT tests: **PASS**.
- Event atomicity tests: **PASS**.
- Cluster bootstrap tests: **PASS**.
- Historical snapshot timestamp tests: **PASS**.
- Controlled empirical runner: **PASS**.

### Not executed

- Maven: **NOT EXECUTED — Maven unavailable in runtime**.
- Docker build/compose runtime: **NOT EXECUTED — Docker unavailable in runtime**.
- Frontend install/build: **NOT EXECUTED — npm dependency installation timed out because network access is unavailable**.
- Real provider acquisition: **NOT EXECUTED — network/DNS unavailable and no provider credentials supplied**.

## Real-data status

The supplied project contains only 7 DEMO rows. No real historical odds dataset was bundled.

**Real events:** NOT AVAILABLE.

**Real timestamped odds:** NOT AVAILABLE.

**Real PIT betting dataset:** NOT AVAILABLE.

**Real backtest:** NOT AVAILABLE.

**Real OOS:** NOT AVAILABLE.

**Real holdout:** NOT AVAILABLE.

**Real CLV:** NOT AVAILABLE.

**Real ROI:** NOT AVAILABLE.

**Edge:** NOT CLAIMED.

## Source findings

The current source documentation confirms that The Odds API offers historical snapshots and returns the closest snapshot at or before a requested timestamp; its historical data is paid. Betfair provides timestamped Exchange historical data from April 2015 via purchased datasets/API. Football-Data provides broad historical results/stats/odds but does not establish exact odds publication timestamps. TheStatsAPI provides football context and stored opening/last-seen odds, with exact PIT semantics requiring a real-response POC. StatsBomb Open Data is useful for selected football event/lineup research but is not a bookmaker odds source. Flashscore remains complementary only.

## Final classification

**LEVEL 1 — Infrastructure complete and empirical layer prepared, but real betting evidence is still unavailable.**

## What still prevents proof of sustainable statistical edge?

1. A legally usable real historical dataset with sufficient event coverage.
2. Provider-native timestamps for the historical odds used at decision time.
3. Reliable event identity joins between football data and odds data.
4. Enough real events to run temporal training/validation/test with a locked holdout.
5. Real OOS predictions generated without later information.
6. Genuine entry and closing prices to measure CLV.
7. Statistical uncertainty and robustness that survive temporal, market, league and odds-bucket analysis.
8. Evidence that the model adds predictive/value information beyond a market-only benchmark.
9. A sufficiently large and independent holdout evaluated only after the entire research process is frozen.
10. Paper/shadow trading evidence showing that the backtest/OOS behavior persists under live information timing and execution constraints.

Until those conditions are met, the scientifically correct conclusion remains:

> **Ainda não sabemos se o ROBO DA BET possui edge estatístico sustentável.**
