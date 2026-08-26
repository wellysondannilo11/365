# ROBO DA BET — FREE GLOBAL ENRICHMENT MASTER V5

## Run on a normal Internet-connected machine

```bash
python scripts/v5/run_v5_discovery.py
```

### Optional API keys

Create `.env` outside version control or export variables in the shell:

```text
API_FOOTBALL_KEY=
FOOTBALL_DATA_API_KEY=
SPORTMONKS_TOKEN=
THESPORTSDB_API_KEY=
THE_ODDS_API_KEY=
SPORTRADAR_API_KEY=
```

The V5 adapters never embed credentials.

## Acquisition order

1. StatsBomb Open Data
2. Football-Data.co.uk uncovered seasons/leagues
3. API-Football free quota for P0 fields
4. OpenLigaDB / TheSportsDB for targeted gaps
5. Open-Meteo after venue geocoding
6. odds providers only after PIT feasibility is proven

## State machine

`DISCOVERED → ACCESSIBLE → DOWNLOADED → CHECKSUMMED → MATERIALIZED → NORMALIZED → VALIDATED → PROCESSED → USED_IN_MODEL`

Terminal states: `BLOCKED`, `FAILED`.

## Scientific rules

- no synthetic football records;
- no post-match leakage;
- no DATE_LEVEL → EXACT_PIT promotion;
- no snapshot rewrite;
- no real-money activation;
- every acquired artifact gets checksum + provenance;
- conflicts remain explicit until resolved.

## Current environment result

The present execution environment has DNS resolution blocked. `REMOTE_BYTES_ACQUIRED=0`. This is an acquisition limitation, not a claim that the public sources lack data.
