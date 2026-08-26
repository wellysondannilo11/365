# V17 — DATA ACQUISITION REPORT

## Execution status

**ATTEMPTED — BLOCKED BY ENVIRONMENT / CREDENTIALS**

The V17 acquisition runner was executed against the configured source classes.

### Network

`network_probe`: **FAIL**

Reason observed during execution:

`URLError: <urlopen error [Errno -3] Temporary failure in name resolution>`

### The Odds API

Status: **NOT AVAILABLE**

Reason: `ROBO_ODDS_API_KEY` was not present.

### Betfair Historical Data

Status: **NOT AVAILABLE**

Reason: no purchased historical package/credentials were supplied and no unsafe endpoint assumption was made.

### Football-Data.co.uk

Status: **NOT EXECUTED**

Reason: network/DNS unavailable.

### StatsBomb Open Data

Status: **NOT EXECUTED**

Reason: network/DNS unavailable.

### Flashscore

Status: **NOT AVAILABLE**

Reason: no safe reproducible historical PIT acquisition endpoint was configured. No anti-bot/CAPTCHA/rate-limit bypass was attempted.

## Dataset actually present

The V16 archive contains `data.csv` with **7 DEMO rows**. It is not promoted to real-data evidence.

## Required next acquisition

Supply one of:

1. The Odds API historical football snapshots with a valid key and sufficient quota; or
2. Betfair Historical Data with the purchased timestamped exchange data; or
3. another legally usable dataset with event identity, historical odds, provider timestamps and settlement.

The pipeline must remain fail-closed until those requirements are met.
