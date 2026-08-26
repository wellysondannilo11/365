# DATA ACQUISITION WORKER

The worker provides resumable, provenance-first downloading for legitimate local execution.
It does **not** bypass DNS, authentication, rate limits, robots rules, paywalls, or access controls.

Pipeline:

`FOUND → ACCESSIBLE → DOWNLOADED → MATERIALIZED → VALIDATED → PROCESSED → USED_IN_MODEL`

Only a later parser/validator may promote a downloaded raw artifact to `MATERIALIZED`.
Checksums are recorded in `data/global_dataset/registry/DATA_ACQUISITION_MANIFEST.json`.

`REAL_MONEY` remains `DISABLED`.
