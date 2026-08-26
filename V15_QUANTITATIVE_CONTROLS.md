# V15 Quantitative Controls

## Evidence hierarchy

1. Real provider data.
2. Provider timestamps and source records.
3. Point-in-time dataset.
4. Leakage/data-quality gates.
5. Temporal validation.
6. Validation-only model selection.
7. OOS evaluation.
8. Locked holdout.
9. Statistical uncertainty.
10. Paper/shadow validation.

Synthetic data is only a software fixture. It is never quantitative evidence.

## Event atomicity

`event_id` is the atomic unit for temporal partitioning. Multiple rows for one event are expected because one match may have many markets/bookmakers. These rows must never cross a train/validation/test/holdout boundary.

## PIT

For decision time `T`, a record is usable only if:

`available_at <= T`

Provider source timestamps may not be replaced by kickoff time, result time, ingestion time or another inferred timestamp.

## Model validation

No random split is used. The research flow is temporal and the final holdout remains isolated from research decisions.

## Betting ROI

`ROI = sum(profit) / sum(stake)`.

`bankroll_return = sum(profit) / initial_bankroll`.

## CLV

For decimal odds, the current price-based CLV convention is:

`entry_odds / closing_odds - 1`

which is positive when the entry price is better than the closing price for the same selection/line.

## Uncertainty

Betting uncertainty is bootstrapped by event cluster rather than by individual bet. This is conservative for datasets containing several bets on one match.

## Evidence gate

No edge or profitability claim is valid unless real OOS/holdout evidence survives the full validation and statistical audit.
