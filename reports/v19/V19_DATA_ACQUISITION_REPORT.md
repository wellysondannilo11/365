# V19 — DATA ACQUISITION REPORT

## Result

**ATTEMPTED — BLOCKED BY RUNTIME NETWORK / CREDENTIALS**

The V19 acquisition runner executed a fresh network probe and source matrix.

### Sources

- Football-Data.co.uk: NOT EXECUTED because DNS/network resolution failed.
- The Odds API: NOT AVAILABLE because `THE_ODDS_API_KEY` / `ROBO_ODDS_API_KEY` is absent.
- Betfair Historical Data: NOT EXECUTED because network was unavailable and no purchased historical package exists in the archive.
- StatsBomb Open Data: NOT EXECUTED because network was unavailable.

Observed runtime error:

`URLError: <urlopen error [Errno -3] Temporary failure in name resolution>`

## Real data used

**None.**

The seven-row DEMO fixture remains a software fixture and is not promoted to evidence.

## Artifact

`data/manifests/V19_ACQUISITION_ATTEMPTS.json`
