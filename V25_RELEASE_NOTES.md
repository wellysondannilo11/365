# ROBO DA BET V25

V25 is a consolidation layer over V20–V24. It does not enable real-money execution.

## New capabilities
- explicit MarketExpressionEngine;
- Asian Handicap quarter-line settlement and fair pricing;
- total quarter-line settlement;
- opening/current price discovery and movement metrics;
- configurable minimum/preferred odds with a distinct NEW_ENTRY gate;
- WAIT/observation-ready architecture through market analysis output;
- independent position reassessment and reversal evaluation;
- V25 empirical dataset with hash chain;
- V25 XLSX tabs for PAPER, SHADOW, RESULTS, MARKETS, LEAGUES, BOOKMAKERS, NO BET, PRICE MOVEMENT and POSITIONS;
- V25 FastAPI endpoints;
- V25 PostgreSQL migration;
- optional PostgreSQL/Redis runtime health adapters;
- V25 live re-pricing fixture path;
- frontend V25 dashboard wiring and tests.

## Scientific boundary
The real-feed session requires `THE_ODDS_API_KEY`. Fake fixtures are test evidence only. Until sufficient real PIT observations exist, `EDGE = NOT DETERMINED`.

## Real money
No real-money execution path is enabled by V25.
