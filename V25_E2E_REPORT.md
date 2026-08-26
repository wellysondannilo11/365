# V25 E2E Report

## Controlled E2E executed

A fake-provider V25 cycle was executed through the real V25 session code:

`provider → normalization → feed health → scoreline pricing → market expression → BET/NO BET → PAPER dataset → hash verification → XLSX export`

Result:

- feed status: `FEED_ONLINE` using controlled fixture;
- observations: 8;
- events: 1;
- snapshots: 3;
- decisions: 8;
- BET: 1;
- NO BET: 7;
- hash chain: valid;
- XLSX export: PASS.

This is a software E2E fixture, **not real betting evidence**.

## Full external E2E

Blocked by missing PostgreSQL/Redis/Docker/Maven/real feed credentials.
