# Robo da Bet V16+ Cycle 2 — Intelligence & Benchmark Design

## Goal
Run a reproducible, research-only intelligence benchmark on the existing V16 candidate using chronological historical outcomes, strict event-level OOS splits, calibration, feature ablation, market-vs-model divergence, pricing research, odds buckets, stake simulations, and volume diagnostics without converting non-PIT prices into real betting evidence.

## Scope
1. Audit and rerun the existing candidate tests.
2. Build a chronological research feature table from historical matches using only prior events.
3. Benchmark market-only, Logistic Regression, Random Forest, Gradient Boosting, HistGradientBoosting, and an ensemble.
4. Evaluate calibration with raw, Platt, and Isotonic methods inside validation-only fitting.
5. Run feature ablations and market/model divergence analysis.
6. Produce theoretical pricing/EV metrics using explicitly NON_PIT prices only.
7. Compare research-only stake rules and opportunity volume.
8. Preserve Exact PIT/real-money gates and classify all betting metrics as NOT_VALIDATED until PIT+settlement exists.

## Data Integrity Rules
- Baseline ZIP is immutable and is never edited.
- Candidate is the only working artifact.
- Historical feature construction may use prior match outcomes because they precede the next event; no current-event outcome is used as a feature.
- Non-PIT odds may be used only as a research benchmark/pricing input and never as validated entry prices.
- Final holdout is never used for model/threshold/calibration selection.
- All experiment configurations and dataset hashes are recorded.
- REAL_MONEY remains DISABLED.

## Outputs
- `reports/cycle2/CYCLE2_EXECUTIVE_REPORT.md`
- `reports/cycle2/CYCLE2_MODEL_RESULTS.csv`
- `reports/cycle2/CYCLE2_ABLATION_RESULTS.csv`
- `reports/cycle2/CYCLE2_MARKET_DIVERGENCE.csv`
- `reports/cycle2/CYCLE2_ODDS_BUCKETS.csv`
- `reports/cycle2/CYCLE2_SIZING_SIMULATION.csv`
- `reports/cycle2/CYCLE2_EXPERIMENT_REGISTRY.jsonl`
