# Local acquisition state machine

`FOUND → ACCESSIBLE → DOWNLOAD_STARTED → DOWNLOADED → CHECKSUM_VALIDATED → MATERIALIZED → NORMALIZED → VALIDATED → PROCESSED → USED_IN_MODEL`

Failure states are `FAILED` and `BLOCKED`. The worker never promotes a downloaded file to materialized/validated/model-used automatically. No authentication bypass, Cloudflare bypass, robots bypass, paywall bypass or credential hardcoding is implemented.
