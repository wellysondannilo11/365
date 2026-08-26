# MODEL COMPARISON REPORT — PHASE 3

{
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
  },
  "RANDOM_FOREST": {
    "oos": {
      "N": 5,
      "Brier": 0.2626712351915401,
      "LogLoss": 0.718506727217329
    },
    "holdout": {
      "N": 6,
      "Brier": 0.2571285169450787,
      "LogLoss": 0.7074031815602413
    }
  },
  "GRADIENT_BOOSTING": {
    "oos": {
      "N": 5,
      "Brier": 0.4725217683452391,
      "LogLoss": 2.612963089124708
    },
    "holdout": {
      "N": 6,
      "Brier": 0.5421339815243077,
      "LogLoss": 1.865510007425667
    }
  },
  "NAIVE": {
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
  }
}