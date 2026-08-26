# ROBO DA BET V18 — FINAL REPORT

## Executive verdict

**🟡 SAFE WITH LIMITATIONS**

V18 was executed directly over the V17 archive. The existing Python research layer was regression-tested, V18 hardening was implemented, real-data acquisition was attempted, and a full-system validation was executed.

The runtime could not reach external sources because DNS/network resolution failed. No The Odds API key was present, no Betfair Historical Data package was present, and the archive contained only the 7-row demo fixture.

## Scientific answer

> **AINDA NÃO É POSSÍVEL DETERMINAR** whether the ROBO DA BET has sustainable statistical edge out of sample.

No real ROI, CLV, OOS or edge claim is made.

## Engineering answer

> **FUNCIONANDO PARCIALMENTE**

The Python research/control layer is executable and the final suite passes. Full backend/Maven and Docker/PostgreSQL/Redis execution was not possible in the runtime. Frontend Node test command runs but discovers zero tests; production build could not run because Vite dependencies are absent.

## Tests

- Python tests: **54 passed**
- Python compileall: **PASS**
- V16 self-test: **PASS**
- Frontend `npm test`: **PASS, 0 tests discovered**
- Maven: **NOT AVAILABLE**
- Docker: **NOT AVAILABLE**

## Real data actually used

**None.**

The V18 acquisition runner attempted Football-Data.co.uk and evaluated The Odds API credentials. External DNS failed and no historical API credential was available. No fabricated dataset was introduced.

## First real backtest/OOS

**Not executed**, because the strict PIT gate correctly remained closed.

## Maturity level

**LEVEL 1 — Infrastructure / controlled empirical research layer operational.**

V18 does not advance to Levels 2–7 because no real timestamped odds dataset was acquired.

## Regression result

No known correctable V17→V18 regression was found in the executable Python surface. V18 ended with 54 passing tests.

## Key V18 hardening

- strict PIT odds availability cannot be inferred in strict mode;
- undefined availability evidence is rejected;
- Football-Data event IDs are deterministic;
- PIT validation handles absent `source_time` correctly;
- acquisition and full-system evidence are persisted;
- version labels were advanced to V18.

## Limitations

1. External DNS/network unavailable.
2. The Odds API historical access requires a credential/paid access path.
3. No Betfair historical package was supplied.
4. Maven unavailable.
5. Docker unavailable.
6. Frontend dependencies are not installed and build was not executed.
7. No real PIT odds, OOS, holdout, CLV or ROI evidence exists.

## Final verdict

**SAFE WITH LIMITATIONS**

This is a software/architecture validation, not proof of betting profitability.
