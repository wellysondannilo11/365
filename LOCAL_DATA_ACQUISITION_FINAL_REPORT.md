# ROBO DA BET — DATA ACQUISITION & ENRICHMENT LOCAL 2020–2026

## Verdict

The local acquisition infrastructure is **FUNCTIONAL** for legitimate local-file acquisition and for HTTP(S) execution when the user's machine has normal network/DNS access. The current execution environment has **no external DNS resolution**, so no new remote bytes were counted as acquired.

No synthetic football data was added. Existing canonical data and prospective pre-match artifacts were preserved.

## Required quantitative status

```text
MATCHES_BEFORE      = 7,570
MATCHES_NEW         = 0
MATCHES_AFTER       = 7,570

COMPETITIONS        = 9
SEASONS             = 12
TEAMS               = 387
PLAYERS             = 0

XG                  = 0
SHOTS               = 0
SOT                 = 0
EVENTS              = 0
LINEUPS             = 0
INJURIES            = 0
SUSPENSIONS         = 0

ODDS                = 4,760
EXACT_PIT           = 0
DATE_LEVEL_PIT      = 30
NON_PIT             = 6,368

SOURCES_FOUND       = registry-defined sources
SOURCES_ACCESSIBLE  = 0 remote in this execution environment
SOURCES_DOWNLOADED  = 0 remote
SOURCES_MATERIALIZED= 0 new remote; existing materialized dataset preserved
SOURCES_VALIDATED   = 0 new remote
SOURCES_FAILED      = explicit failures only
SOURCES_BLOCKED     = external DNS/network routes blocked
```

## What was actually acquired

No new remote historical dataset was claimed. The existing 7,570 canonical matches remain the authoritative local backbone. A local-file acquisition pilot was executed against an existing real Football-Data CSV and passed checksum/materialization validation, but the pilot artifact was removed after testing so it does not contaminate the production dataset.

The worker therefore demonstrated the real path:

`FOUND → ACCESSIBLE → DOWNLOAD_STARTED → DOWNLOADED → CHECKSUM_VALIDATED → MATERIALIZED → NORMALIZED → VALIDATED → PROCESSED`

without promoting the artifact to `USED_IN_MODEL`.

## What was not acquired

Remote acquisition was attempted through the new HTTP(S) path. DNS resolution failed in the execution environment (`Temporary failure in name resolution`). This is recorded as an acquisition/network limitation, not as an empty dataset and not as successful acquisition.

The next legitimate execution on the user's machine should prioritize Football-Data.co.uk for result/market history and StatsBomb Open Data for the competitions actually present in its open-data repository. Coverage must be validated after bytes are downloaded; catalogue presence alone never counts as materialization.

## Local mode capabilities

Implemented/preserved:

- configurable `DATA_ROOT`, `RAW_ROOT`, `PROCESSED_ROOT`, `CACHE_ROOT`, `LOG_ROOT`;
- HTTP(S) download with timeout/retry;
- atomic `.part` downloads;
- SHA-256 verification;
- reuse of unchanged local artifacts;
- structured manifest state history;
- explicit `FAILED` / `BLOCKED` states;
- local-file ingestion for offline/restricted environments;
- separate validation/materialization stage;
- provenance timestamps;
- no credential hardcoding;
- no Cloudflare/authentication/robots/paywall bypass;
- resumable artifact-level acquisition;
- explicit distinction between downloaded and materialized data.

## How to execute locally

From the project root:

```bash
python scripts/global/data_acquisition_worker.py --config config/data_acquisition_local.json --url "https://SOURCE/FILE.csv"
```

For a local file:

```bash
python scripts/global/data_acquisition_worker.py --config config/data_acquisition_local.json --path "/path/to/file.csv"
python scripts/global/local_materializer.py
```

The registry/configuration can be expanded with legitimate source URLs and expected SHA-256 values. Credentials, if required by a legitimate provider, must be supplied through the provider's supported environment/configuration mechanism and never committed to the repository.

## Snapshot integrity

Before/after hashes of the existing pre-match artifacts were compared. There was **no hash difference**.

Critical preserved artifacts included:

- `data/master_staff/PREMATCH_FEATURE_STORE.csv`
- `data/real_day_prematch/REAL_DAY_PREMATCH_SNAPSHOT.json`
- `data/real_day_prematch/REAL_DAY_FEATURES.csv`
- snapshot integrity/protection reports.

## Test status

```text
pytest                         PASS
compileall                     PASS
local acquisition tests        PASS (3/3)
checksum/reuse test            PASS
materialization validation     PASS
explicit remote failure test  PASS
full existing test suite       PASS
```

`unzip -t` and final SHA-256 are generated for the delivery artifact.

## Scientific status

```text
GLOBAL_DATASET_STATUS = GLOBAL_PARTIAL
ACQUISITION_STATUS    = REMOTE_BLOCKED_LOCAL_PIPELINE_READY
ENRICHMENT_STATUS     = EXISTING_DATA_PRESERVED / NEW_REMOTE_NOT_ACQUIRED
PIT_STATUS            = DATE_LEVEL_PIT_ONLY
MODEL_STATUS          = RESEARCH_ONLY
EDGE_STATUS           = EDGE_NOT_DETERMINED
VALUE_BET_STATUS      = BLOCKED
REAL_MONEY_STATUS     = DISABLED
```

## Next highest-value acquisition

1. Historical Exact-PIT odds with verified timestamps/timezones.
2. xG/shots/SOT/events for the same canonical matches.
3. Lineups/player-match data and historical availability.
4. Injuries/suspensions with publication/effective timestamps.
5. Expand Brazil/CONMEBOL and the major European leagues with cross-source entity resolution.

The next scientific bottleneck is **real timestamped enrichment**, especially Exact PIT and player availability—not additional architecture.
