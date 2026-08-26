# ROBO DA BET V16+ — CYCLE 2 EXECUTIVE QUANT REPORT

Dataset SHA-256: `e653c54af7896b0693220c13b0f750ea5329a0f9bbb285647ecb8c388890ee35`
Baseline SHA: `608f587b628b8d09c961519e9ca3ec5a664dd68e3091de4c0371937a2adcd967`
Candidate start SHA: `c1b8b0ef76be571f5be479871cb6d385325e5546e7030a013f11c6dd7ea3db66`

Rows: 8,523
Exact PIT: 0
REAL_MONEY: DISABLED
Betting ROI/units/CLV: NOT_VALIDATED

## Scientific interpretation
All model metrics below are chronological research/OOS metrics. Prices are non-PIT research inputs and cannot establish real betting edge, ROI or CLV.

## btts
| target   | model    | calibration   |    n |   accuracy |   log_loss |    brier |       ece |      mce |   roc_auc |
|:---------|:---------|:--------------|-----:|-----------:|-----------:|---------:|----------:|---------:|----------:|
| btts     | logistic | raw           | 5000 |     0.5294 |   0.692107 | 0.249438 | 0.0477255 | 0.319304 |  0.541398 |

## cards_high
| target     | model    | calibration   |    n |   accuracy |   log_loss |    brier |      ece |      mce |   roc_auc |
|:-----------|:---------|:--------------|-----:|-----------:|-----------:|---------:|---------:|---------:|----------:|
| cards_high | logistic | raw           | 5000 |     0.7006 |   0.694917 | 0.230638 | 0.143176 | 0.402418 |   0.50549 |

## corners_high
| target       | model    | calibration   |    n |   accuracy |   log_loss |   brier |      ece |      mce |   roc_auc |
|:-------------|:---------|:--------------|-----:|-----------:|-----------:|--------:|---------:|---------:|----------:|
| corners_high | logistic | raw           | 5000 |      0.545 |   0.772799 | 0.27997 | 0.170534 | 0.566014 |  0.534859 |

## home_win
| target   | model                  | calibration    |   n |   accuracy |   log_loss |    brier |       ece |       mce |   roc_auc |
|:---------|:-----------------------|:---------------|----:|-----------:|-----------:|---------:|----------:|----------:|----------:|
| home_win | logistic               | raw            | 500 |      0.608 |   0.64841  | 0.229062 | 0.0358351 | 0.0734718 |  0.651389 |
| home_win | logistic               | raw_standalone | 500 |      0.608 |   0.64841  | 0.229062 | 0.0358351 | 0.0734718 |  0.651389 |
| home_win | logistic               | platt          | 500 |      0.606 |   0.650154 | 0.229652 | 0.0508743 | 0.199032  |  0.651389 |
| home_win | random_forest          | raw_standalone | 500 |      0.604 |   0.666013 | 0.236822 | 0.0358384 | 0.126612  |  0.621791 |
| home_win | ensemble               | raw            | 500 |      0.582 |   0.666351 | 0.237645 | 0.0545374 | 0.155093  |  0.613552 |
| home_win | logistic               | isotonic       | 500 |      0.606 |   0.691747 | 0.23123  | 0.0419068 | 0.213361  |  0.656133 |
| home_win | gradient_boosting      | raw_standalone | 500 |      0.554 |   0.701542 | 0.252846 | 0.100336  | 0.310769  |  0.583613 |
| home_win | hist_gradient_boosting | raw_standalone | 500 |      0.528 |   0.709358 | 0.256052 | 0.13536   | 0.419072  |  0.576964 |

## over_2_5
| target   | model                  | calibration    |   n |   accuracy |   log_loss |    brier |       ece |      mce |   roc_auc |
|:---------|:-----------------------|:---------------|----:|-----------:|-----------:|---------:|----------:|---------:|----------:|
| over_2_5 | logistic               | raw            | 500 |      0.568 |   0.682395 | 0.244693 | 0.0379679 | 0.192642 |  0.581087 |
| over_2_5 | logistic               | raw_standalone | 500 |      0.568 |   0.682395 | 0.244693 | 0.0379679 | 0.192642 |  0.581087 |
| over_2_5 | logistic               | platt          | 500 |      0.564 |   0.689315 | 0.247729 | 0.0581373 | 0.230811 |  0.581087 |
| over_2_5 | ensemble               | raw            | 500 |      0.548 |   0.693042 | 0.249705 | 0.0480669 | 0.804197 |  0.557265 |
| over_2_5 | random_forest          | raw_standalone | 500 |      0.522 |   0.694588 | 0.250512 | 0.0569816 | 0.255058 |  0.557585 |
| over_2_5 | gradient_boosting      | raw_standalone | 500 |      0.53  |   0.698478 | 0.252093 | 0.0557037 | 0.524879 |  0.548836 |
| over_2_5 | hist_gradient_boosting | raw_standalone | 500 |      0.52  |   0.735499 | 0.268043 | 0.10673   | 0.417317 |  0.52022  |
| over_2_5 | logistic               | isotonic       | 500 |      0.57  |   1.23022  | 0.2621   | 0.0976993 | 0.796453 |  0.58047  |

## shots_high
| target     | model    | calibration   |    n |   accuracy |   log_loss |    brier |      ece |     mce |   roc_auc |
|:-----------|:---------|:--------------|-----:|-----------:|-----------:|---------:|---------:|--------:|----------:|
| shots_high | logistic | raw           | 5000 |     0.5006 |   0.793596 | 0.289003 | 0.184367 | 0.54427 |  0.568879 |

## sot_high
| target   | model    | calibration   |    n |   accuracy |   log_loss |    brier |      ece |      mce |   roc_auc |
|:---------|:---------|:--------------|-----:|-----------:|-----------:|---------:|---------:|---------:|----------:|
| sot_high | logistic | raw           | 5000 |     0.5866 |   0.741338 | 0.263956 | 0.144909 | 0.392239 |  0.580887 |

## Home-win feature ablation
| feature_set         | model    | calibration   |   log_loss |    brier |       ece |   accuracy |   n |
|:--------------------|:---------|:--------------|-----------:|---------:|----------:|-----------:|----:|
| MARKET_INTELLIGENCE | logistic | raw           |   0.646787 | 0.22851  | 0.045138  |      0.606 | 500 |
| MARKET              | logistic | raw           |   0.646787 | 0.22851  | 0.045138  |      0.606 | 500 |
| FULL                | logistic | raw           |   0.64841  | 0.229062 | 0.0358351 |      0.608 | 500 |
| CARDS               | logistic | raw           |   0.649256 | 0.229346 | 0.0239068 |      0.614 | 500 |
| CORNERS             | logistic | raw           |   0.651441 | 0.230441 | 0.0451992 |      0.602 | 500 |
| BASELINE            | logistic | raw           |   0.651768 | 0.230564 | 0.0241027 |      0.598 | 500 |
| MOMENTUM            | logistic | raw           |   0.652946 | 0.231213 | 0.0349793 |      0.6   | 500 |
| SHOTS_SOT           | logistic | raw           |   0.655961 | 0.232677 | 0.0392208 |      0.582 | 500 |

## Market-only benchmark
| target   |    n |   accuracy |   log_loss |    brier |       ece |
|:---------|-----:|-----------:|-----------:|---------:|----------:|
| home_win | 2500 |     0.6344 |   0.63167  | 0.221048 | 0.0445236 |
| over_2_5 | 1000 |     0.587  |   0.675288 | 0.241232 | 0.0429359 |

## Official status
`EDGE = NOT_PROVEN`
`ROI_OOS = NOT_DETERMINED`
`UNITS_OOS = NOT_DETERMINED`
`CLV = NOT_AVAILABLE`
`EXACT_PIT = 0`
`REAL_MONEY = DISABLED`

## Direct common-sample comparison — Home Win

The direct comparison uses the same chronology-safe 500-event OOS test window and the same non-PIT price population. Lower Log Loss/Brier is better.

| Configuration | Accuracy | Log Loss | Brier | ECE | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Market-only | 0.610 | 0.646162 | 0.228408 | 0.029541 | 0.648129 |
| Robo baseline logistic | 0.598 | 0.651768 | 0.230564 | 0.024103 | 0.638950 |
| Robo + market features | 0.606 | 0.646787 | 0.228510 | 0.045138 | 0.651162 |
| Robo full | 0.608 | 0.648410 | 0.229062 | 0.035835 | 0.651389 |

**Finding:** market information materially improves the Robo baseline, but the full candidate does **not** beat the market-only benchmark on this common OOS window. Market-only has the lowest Log Loss/Brier and better ECE; the Robo full model has slightly higher ROC-AUC but worse probability quality.

## Calibration

For Home Win and Over 2.5, raw logistic probabilities were better than Platt and Isotonic on the executed OOS window. Calibration is therefore **not promoted** as an improvement in this cycle.

## Feature ablation

On the common 2,951-event comparison population, the first OOS window produced: baseline Log Loss 0.651768; market features 0.646787; cards 0.649256; full 0.648410; corners 0.651441; momentum 0.652946; shots/SOT 0.655961. This supports **market features as the clearest positive incremental component**, while the tested full stack does not outperform the market-feature configuration.

## Research-only pricing

On the same 500-event OOS window using non-PIT odds: market-only mean theoretical EV was **-6.35%**; Robo full mean theoretical EV was **-2.83%**, with 37% of Robo-full rows showing positive point-estimate EV. This is **counterfactual research only** and is not evidence of betting ROI because the price timestamps are not Exact PIT.

## Markets

Home Win is the strongest tested predictive target in this run (Robo full ROC-AUC 0.6514; Log Loss 0.6484). Over 2.5 is second (ROC-AUC 0.5811; Log Loss 0.6824). BTTS, corners, shots and SOT are weaker; cards-high shows high raw accuracy (0.7006) but ROC-AUC ~0.5055 and therefore should not be interpreted as useful predictive edge.

## Odds buckets

Market-implied research EV remained negative across every tested odds bucket. No bucket is promoted. The best observed bucket was still negative and therefore does not establish value.

## Sizing

The theoretical flat-stake simulation scales linearly with stake and remains negative across 0.25U–2U. No sizing rule is promoted. 2U remains a hard ceiling.

## Promotion decision

**Classification: C — INCONCLUSIVE / NO ROBUST EDGE DEMONSTRATED.** The cycle demonstrates that the intelligence pipeline can produce chronological OOS benchmarks, and that adding market information improves the baseline model, but the candidate full model does not yet outperform the market-only benchmark. No component is promoted to real-money use.
