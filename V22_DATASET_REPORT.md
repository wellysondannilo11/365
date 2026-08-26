# V22 Dataset Report

The project now creates `data/research/robo_bet_dataset_v22.jsonl` when the V22 real-feed scan receives observations. Each row receives a deterministic content hash and includes decision/mode/context payload.

PostgreSQL persistence is also prepared in `v22_dataset_rows`.

At audit time the dataset contains **0 real observations**, because the external provider credential was unavailable. This is correctly reported as zero, not converted from demo data.
