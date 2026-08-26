# ROBO DA BET V17 — FINAL REPORT

## Executive verdict

**🟡 SAFE WITH LIMITATIONS**

V17 was executed over the V16 archive, the real-data acquisition cycle was attempted, the existing regression suite was rerun, and the full-system validation was performed. The environment did not provide network/DNS access, no The Odds API credential was supplied, and no Betfair historical package was present. The archive contains only 7 demo rows.

Therefore V17 does **not** claim a real betting backtest, real OOS edge, real CLV or real ROI.

## Final scientific answer

> **AINDА NÃO É POSSÍVEL DETERMINAR** se o ROBO DA BET possui edge estatístico sustentável fora da amostra.

The missing evidence is specifically:

1. real historical timestamped odds;
2. enough real events for temporal train/validation/test;
3. independent real OOS predictions;
4. a locked real holdout;
5. genuine entry and closing prices for CLV;
6. benchmark comparison against market-only information;
7. robustness across seasons/leagues/markets/odds buckets;
8. statistical uncertainty and multiple-testing control;
9. reproducible paper-trading evidence under live timing.

## Final engineering answer

The Python research layer is functioning under controlled execution. The full production stack could not be completely exercised because Maven and Docker are unavailable in the runtime and frontend production dependencies are not installed.

## Classification

**LEVEL 1 — Infrastructure / empirical research layer operational; real-data evidence unavailable.**

## Verdict

**🟡 SAFE WITH LIMITATIONS**

No unresolved V16→V17 regression was found in the executable regression suite.

## Mandatory scientific limitation

A positive result cannot be manufactured from the 7-row demo fixture. The demo fixture is explicitly excluded from real betting evidence.

## Release artifact checksum

The authoritative SHA-256 is delivered as a detached checksum alongside the ZIP artifact.
