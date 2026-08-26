# V25 Market Expression Engine Audit

`MarketExpressionEngine` is a new explicit V25 layer.

It evaluates supported rows across H2H, AH/spreads, totals, BTTS, double chance and DNB when model pricing is available. It can use:

- scoreline distribution;
- explicit model probability; or
- bookmaker-aware market consensus.

It computes probability, fair odds, edge, EV, uncertainty, market quality and a ranking score.

Default selection is one principal expression per event. Other positive candidates remain observable as NO BET / rejected expressions rather than being silently discarded.
