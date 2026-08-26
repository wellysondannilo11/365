# EMPIRICAL RESEARCH REPORT — PHASE 2

## Scientific status
`NOT_DETERMINED` for betting edge. The research pipeline was executed against **40 historical-real football matches**, but the sample is too small and split across seasons/fields to support a profitability claim.

### 1X2 market-only
- N = 10
- Log Loss = 0.884949
- Multiclass Brier = 0.515481
- Favorite strategy: 10 bets, 6 wins, PnL = -0.5100 units, ROI = -5.10%
- CLV = NOT_DETERMINED because decision-time/closing timestamps are absent.

### Existing Robo-style temporal feature pipeline
The research run used pre-match historical features based only on strictly prior calendar dates. A logistic model using goal/form/card features produced a temporal OOS window of 5 and a locked final holdout of 6. This demonstrates the split/lineage path, not robust generalization.

OOS: Brier 0.336125; Log Loss 0.874243.
Holdout: Brier 0.526945; Log Loss 1.510856.

### Cards
Card totals were modeled with prior-date team/referee information. Poisson and Negative Binomial were both executed; neither is promoted because N=30 and OOS/holdout are tiny.

### Limitations
- No timestamped odds snapshots.
- No overlapping historical odds+cards dataset in the materialized bytes, so Robo betting decisions cannot be reconstructed honestly for all 40 matches.
- No CLV.
- No statistically meaningful walk-forward with repeated folds.
- No robust multiple-testing conclusion.
