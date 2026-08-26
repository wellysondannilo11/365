# RELEASE V24

## Scope

V24 is the controlled real-observation release of Robo da Bet.

It preserves the V20–V23 stack and strengthens:
- source timestamp semantics;
- feed freshness;
- bookmaker-aware market baseline;
- empirical immutable dataset;
- PAPER/SHADOW separation;
- live snapshot quality;
- replay;
- export;
- kill switch;
- operational APIs.

## Safety

Real-money execution is disabled.

## Start

```bash
PYTHONPATH=ml python ml/scripts/run_v24_observation.py --mode SHADOW
```

Provide `THE_ODDS_API_KEY` before real observation.

## Scientific status

**EDGE = NOT DETERMINED.**

No synthetic or replay result is treated as evidence of profitability.
