# ROBO DA BET V16+ — CICLO 4

## Estado

- EXACT_PIT: **0**
- Scientifically eligible decisions: **0**
- Settlements: **0**
- CLV: **0**
- OOS PIT: **0**
- Walk-forward PIT: **0**
- REAL_MONEY: **DISABLED**
- EDGE: **NOT_PROVEN**

## Acquisition

The Odds API adapter exists locally, but no physical historical snapshot response is materialized. The runtime network probe is `BLOCKED_EXTERNAL`. Therefore the historical provider track is `BLOCKED_EXTERNAL` and no exact PIT rows are promoted.

Official provider documentation states that historical odds are returned as snapshots at a requested timestamp, with the closest snapshot equal to or earlier than the requested time; the historical endpoint is paid. citeturn0search0turn0search1

## Local data

The available `odds_observations_real_nonpit.csv` contains historical opening/closing/date-level odds, explicitly classified as NON_PIT. It is not promoted to exact PIT.

## Scientific conclusion

Because there are zero exact-PIT prices, there are zero scientifically eligible paper bets, settlements and CLVs. Consequently this cycle cannot establish or reject betting edge. The correct verdict is **C — INCONCLUSIVE**, with `EDGE = NOT_PROVEN`.

## What was validated locally

- PIT gate: price must be present, valid, provenance-backed and timestamped at/before decision.
- Future price rejection.
- Date-level evidence rejection.
- Decision snapshot required fields.
- Deterministic settlement mechanics.
- CLV temporal semantics.
- The Odds API parser keeps provider snapshot timestamp distinct from nested bookmaker/market update timestamps.
