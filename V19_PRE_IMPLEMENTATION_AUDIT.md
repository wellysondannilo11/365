# V19 — PRE-IMPLEMENTATION AUDIT

## Base

The implementation was performed directly on `ROBO_DA_BET_V18_COMPLETE_REAL_DATA.zip` and preserved the existing V18 research/control architecture.

## V18 observed state

- Python research layer: executable.
- Strict PIT guards: present and tested.
- Historical odds acquisition adapters: present, but no provider-native timestamped dataset was available.
- Holdout: locked by contract.
- Walk-forward validation: present.
- Calibration/CLV/bootstrap modules: present, not empirically validated on real PIT odds.
- Paper ledger: present.
- Backend: Spring Boot source present; Maven unavailable in runtime.
- Frontend: React/Vite source present; dependencies absent and V18 build was not executable.
- Docker/PostgreSQL/Redis: compose and migrations present; Docker unavailable.

## Main V19 gap

V18 did not expose a single reusable pricing core capable of turning an event state into a scoreline distribution and then into fair probabilities, fair prices, derived markets and market dislocations.

## V19 changes

1. Added a reusable `PricingEngine` for PRE and LIVE states.
2. Added normalized Poisson scoreline distribution with optional Dixon-Coles low-score adjustment.
3. Added fair probability and fair-odds derivation for 1X2, double chance, totals, BTTS and Asian handicap representations.
4. Added settlement-aware EV/fair-odds logic for win/push/half-win/half-loss/loss.
5. Added canonical market normalization, de-vig and consensus utilities.
6. Added PIT-aware market dislocation discovery.
7. Added price movement timeline and CLV helpers.
8. Added immutable V19 paper-bet ledger records.
9. Added confidence classification with documented criteria.
10. Added market-efficiency research utility.
11. Added V19 API endpoints for pricing, market normalization, consensus, dislocations and paper signals.
12. Added Market Intelligence frontend surface without enabling live execution.
13. Added V19 acquisition, validation, performance and security evidence scripts.

## Risk matrix

| Component | Exists | Complete before V19 | Changed | Main risk |
|---|---:|---:|---:|---|
| PIT | YES | YES | Hardened integration | Real provider timestamps absent |
| Odds normalization | YES | PARTIAL | Extended | Source semantics |
| Scoreline pricing | NO | NO | NEW | Model misspecification |
| Derived markets | NO | NO | NEW | Settlement semantics |
| Fair odds | PARTIAL | PARTIAL | NEW | Asian/void rules |
| Market consensus | YES | PARTIAL | Extended | Average is not truth |
| Dislocation | NO | NO | NEW | Model uncertainty |
| Price movement | PARTIAL | NO | NEW | Timestamp quality |
| CLV | YES | PARTIAL | Integrated | Closing-line comparability |
| Paper ledger | YES | PARTIAL | Extended | Decision immutability |
| OOS | LOCKED | NO | Preserved | No real dataset |
| Holdout | LOCKED | YES | Preserved | Must remain untouched |
| Backend | PARTIAL | NO | Extended API | Maven unavailable |
| Frontend | PARTIAL | NO | Extended UI | Build dependencies unavailable |
