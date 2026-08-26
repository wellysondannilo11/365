# FREE DATA DISCOVERY & GLOBAL ENRICHMENT V4

This is an incremental enrichment layer over the real latest Library ZIP. It does not rebuild the Robo and does not alter protected prematch snapshots.

## Runtime result

The current execution container has DNS/network resolution blocked. Consequently remote bytes acquired in V4 are **0**. Existing local materialized data remains untouched.

## What V4 actually changed

- expanded the source registry beyond football-only providers;
- added Open-Meteo context-provider adapter for historical weather;
- added strict monotonic source-state machine;
- generated competition/season coverage matrix;
- generated master data-gap and paid-gap reports;
- generated temporal/PIT/player/lineup/injury/suspension/xG/event/odds reports;
- generated Sofascore legal/access assessment;
- added V4 acquisition manifest and API readiness matrix;
- preserved all protected snapshots and existing historical data.

## External execution

Run the existing resumable acquisition worker on a machine with normal Internet/DNS access. API keys are environment variables only. Never bypass authentication, paywalls, Cloudflare, robots restrictions or provider controls.

`REAL_MONEY=DISABLED` is mandatory.
