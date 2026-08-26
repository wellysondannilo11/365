# V12 Historical Training Contract

1. Raw source records must preserve `event_time`, `source_time`, `available_at`, `ingested_at`, `decision_time`.
2. A feature is legal only when `available_at <= decision_time`.
3. Closing prices are evaluation/CLV data for earlier decisions, never earlier features.
4. The final holdout is locked until the research process is frozen.
5. Compare Sport Only, Market Only and Hybrid using the same temporal OOS windows.
6. Calibration is evaluated OOS; global calibration is used when sample size is insufficient for a subgroup.
7. Model selection is based on probabilistic quality and stability, not ROI alone.
8. Strategy discovery must log experiment count and preserve the final holdout.
9. Live models require historical live snapshots; a pre-match dataset is not sufficient evidence for live performance.
