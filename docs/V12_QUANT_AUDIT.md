# Robo da Bet V12 — Quant Audit & Implementation Status

## Audit conclusion
V11 contained a functional skeleton for the decision engine, risk controls, adapters, ledger and a minimal ML suite, but several quantitative claims were stronger than the actual implementation. V12 closes the most important P0 gaps: point-in-time metadata, centralized leakage validation, feature lineage, explicit Sport/Market/Hybrid layer training, market consensus, uncertainty, temporal validation primitives, calibration metrics, and a stricter training gate.

## Status semantics
- IMPLEMENTED AND FUNCTIONAL: code path exists and is exercised by tests.
- IMPLEMENTED BUT INCOMPLETE: real structure exists but production coverage/data is incomplete.
- SCAFFOLD: interface exists without sufficient end-to-end evidence.
- NOT IMPLEMENTED: no claim is made.

## Quantitative status
| Capability | V12 status | Evidence |
|---|---|---|
| Point-in-time fields | IMPLEMENTED AND FUNCTIONAL | `ml/app/schemas.py`, `temporal.py`, tests |
| Feature lineage | IMPLEMENTED AND FUNCTIONAL | `lineage.py`, `features.py` |
| Leakage gate | IMPLEMENTED AND FUNCTIONAL | `leakage.py`, tests |
| Historical odds snapshots | IMPLEMENTED BUT INCOMPLETE | schema + SQL migration; adapter persistence still needs real provider history |
| Market consensus/de-vig | IMPLEMENTED AND FUNCTIONAL | `consensus.py`, tests |
| Sport-only layer | IMPLEMENTED AND FUNCTIONAL | `layer_training.py` |
| Market-only layer | IMPLEMENTED AND FUNCTIONAL | `layer_training.py` |
| Hybrid layer | IMPLEMENTED AND FUNCTIONAL | `layer_training.py` |
| Specialized markets | IMPLEMENTED BUT INCOMPLETE | architecture supports per-market runs; only generic training data is bundled |
| Elo/Poisson/Dixon-Coles | IMPLEMENTED BUT INCOMPLETE | baselines exist; robust parameter estimation requires real historical event data |
| XGBoost/LightGBM/CatBoost | IMPLEMENTED AND FUNCTIONAL when packages available | optional candidates in `models.py` |
| Calibration | IMPLEMENTED AND FUNCTIONAL | isotonic/Platt + OOS metrics |
| Uncertainty | IMPLEMENTED AND FUNCTIONAL | ensemble disagreement + bootstrap helper |
| Walk-forward | IMPLEMENTED BUT INCOMPLETE | temporal walk-forward primitive; production fold policy depends on dataset |
| Final holdout | IMPLEMENTED AS A LOCKED CONTRACT | training refuses to claim final-holdout usage |
| CLV | IMPLEMENTED | ledger + market functions |
| Live remaining goals | IMPLEMENTED BUT INCOMPLETE | model uses live state + pre-match prior; provider history is required for serious validation |
| Risk | IMPLEMENTED | daily stop, loss streak cooldown, exposure bookkeeping |
| Telegram | IMPLEMENTED BUT INCOMPLETE | requires real token/chat id |
| Frontend | IMPLEMENTED BUT INCOMPLETE | real API wiring; runtime browser integration not validated in this environment |

## Important limitation
The bundled `data.csv` is a tiny DEMO dataset. It is not evidence for model quality, profitability, calibration quality, CLV or live performance. Serious historical training requires a sufficiently large real point-in-time dataset with odds snapshots and event availability timestamps.
