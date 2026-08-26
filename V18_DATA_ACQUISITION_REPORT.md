# V18 — DATA ACQUISITION REPORT

## Result

**ATTEMPTED — BLOCKED BY RUNTIME NETWORK / CREDENTIALS**

### Runtime network

`network_probe`: **FAIL**

Observed error:

`URLError: <urlopen error [Errno -3] Temporary failure in name resolution>`

### The Odds API

**NOT AVAILABLE** — `THE_ODDS_API_KEY` / `ROBO_ODDS_API_KEY` absent.

### Betfair Historical Data

**NOT AVAILABLE** — no purchased historical package or credentials present.

### Football-Data.co.uk

**ATTEMPTED** — direct season CSV acquisition was configured for 2023/24, 2024/25 and 2025/26 Premier League (`E0`), but DNS failed before download. No raw artifact was created.

### StatsBomb Open Data

**NOT EXECUTED** because the runtime could not reach external sources.

### Flashscore

**NOT USED**. No scraping bypass, CAPTCHA bypass, anti-bot circumvention or terms circumvention was attempted.

## Dataset actually available

The archive contains only the 7-row demo fixture. It remains a software fixture and is explicitly excluded from real betting evidence.

## Acquisition manifest

`data/manifests/V18_ACQUISITION_ATTEMPTS.json`

## Conclusion

No real dataset was successfully ingested in V18. No synthetic replacement was created.
