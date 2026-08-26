# V14.1 Improvement Report

## P0 implemented

1. Strict feature-level availability validation.
2. Explicit rejection of feature timestamps after decision time.
3. Historical feature builder rewritten around prior team state.
4. No current match outcome is inserted into feature history before feature generation.
5. Historical odds snapshots now preserve source timestamps and availability evidence.
6. Market consensus de-vigs within bookmaker + market + line + snapshot before cross-bookmaker aggregation.
7. Stale odds are explicitly filterable.

## P1 implemented

1. Repository pytest import path fixed.
2. Backtest records expanded with market/selection/bookmaker/implied/fair/edge fields.
3. Betting metrics expanded: bets, profit, yield, ROI, hit rate, drawdown, volatility, Sharpe-like, Sortino-like, average odds and CLV.
4. Research API expanded for datasets, experiments, validation and data-quality status.
5. Frontend research pages now request their corresponding API endpoint instead of showing one generic status object.
6. Experiment registry made persistent and immutable.
7. Reproducibility manifest utility added.
8. V14 data acquisition migration added.

## Remaining external blocker

Exact timestamped historical odds plus a sufficiently large real football dataset are still required before any real OOS/holdout/profitability claim can be made.
