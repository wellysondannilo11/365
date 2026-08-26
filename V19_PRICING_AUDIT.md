# V19 — PRICING AUDIT

## Implemented

The V19 pricing core converts explicit expected-goal rates into a normalized scoreline distribution and derives market probabilities from that distribution.

Supported derived families:

- 1X2
- Double Chance
- Over/Under 0.5, 1.5, 2.5, 3.5, 4.5
- BTTS Yes/No
- Asian handicap probability decomposition for half/whole/quarter-compatible lines

Optional Dixon-Coles low-score adjustment is supported and the resulting distribution is renormalized.

## Scientific safeguards

- Probabilities outside [0,1] are rejected.
- Empty/non-normalized scoreline distributions are rejected.
- Fair odds are only returned when probability is positive.
- The engine does not invent live state or odds.
- PRE and LIVE use the same pricing engine with different state inputs.

## Important limitation

The scoreline engine is a statistical pricing mechanism, not evidence of predictive edge. No real historical study was available in the runtime.
