# BASELINE COMPARISON REPORT — PHASE 3

Market-only 1X2 is the only price baseline available. Model comparisons below use a binary home-win target, not a complete 1X2 Robo betting run.

{
  "MARKET_ONLY_1X2": {
    "N": 10,
    "bets": 10,
    "wins": 6,
    "pnl": -0.51,
    "roi": -0.051000000000000004,
    "brier": 0.5154813570796579,
    "log_loss": 0.8849490612858123,
    "clv": "NOT_DETERMINED"
  },
  "NAIVE_HOME_WIN": {
    "oos": {
      "N": 5,
      "Brier": 0.2664819944598338,
      "LogLoss": 0.7261422986986559
    },
    "holdout": {
      "N": 6,
      "Brier": 0.26823638042474607,
      "LogLoss": 0.72965431588725
    }
  },
  "LOGISTIC": {
    "oos": {
      "N": 5,
      "Brier": 0.3361248329218337,
      "LogLoss": 0.8742431435902391
    },
    "holdout": {
      "N": 6,
      "Brier": 0.5269449877060333,
      "LogLoss": 1.510855864546853
    }
  }
}