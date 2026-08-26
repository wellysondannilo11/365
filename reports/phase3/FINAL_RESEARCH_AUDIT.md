# FINAL RESEARCH AUDIT — GLOBAL FOOTBALL RESEARCH

## Artifact
- Input ZIP: `PACOTE_CONSOLIDADO_ROBO_DA_BET_FUTEBOL_PESQUISA_FINAL_PHASE3(2).zip`
- Input ZIP SHA-256: `30c52e448c566c773503d84030d9672b3311943b1e5e34c2a401703071381dd9`
- ZIP integrity: `unzip -t` PASS
- Files in extracted package: 817

## Real evidence actually materialized
- HISTORICAL_REAL matches: **40**
- Materialized datasets: **2**
- Countries with real rows: **1 (England)**
- Competitions with real rows: **1 (Premier League)**
- Seasons: **2023/24 and 2025/26 pilots**
- Real 1X2 price rows: **10**
- PIT/date-level feature rows: **30**
- Exact PIT odds rows: **0**
- LIVE historical snapshots: **0**
- Historical live odds: **0**

## Acquisition expansion
The research layer now includes a multi-route acquisition manifest and canonical evidence schema. Nine representative acquisition routes were evaluated for this runtime's external-access constraint; none could materialize new bytes because external DNS/network resolution is unavailable. Source capabilities were independently verified through web research, but source discovery is not counted as data ingestion.

## Research executed
- strict provenance audit;
- canonical source_url completion for existing real rows;
- data-quality validation;
- temporal/PIT-safe feature construction;
- market-only 1X2 baseline;
- naive/logistic/random-forest/gradient-boosting comparison;
- card Poisson vs Negative Binomial experiment;
- corner-count descriptive/predictive experiment;
- feature ablation;
- holdout lock discipline;
- source/competition coverage mapping;
- live-engine audit;
- CLV audit;
- multiple-testing audit;
- lower-division/global acquisition mapping.

## Validation executed
- Python self-test: PASS
- Pytest: **164 passed**
- Python compileall: PASS
- Frontend unit tests: **2 passed**
- Frontend production build: **NOT EXECUTED SUCCESSFULLY** because `node_modules`/Vite are absent and external package installation timed out under the runtime network restriction.

## Scientific status
- ROBO > MARKET_ONLY: `NOT_DETERMINED`
- EDGE: `NOT_DETERMINED`
- OOS: `INSUFFICIENT`
- HOLDOUT: `INSUFFICIENT`
- WALK-FORWARD: `INSUFFICIENT`
- CLV: `NOT_DETERMINED`
- Overfitting risk: `HIGH`
- Scientific level: **LEVEL 2 — OBSERVATION**
- REAL_MONEY: **DISABLED**
