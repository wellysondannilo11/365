# GLOBAL DATA ACQUISITION V6 — FINAL AUDIT

Execution date: 2026-08-20T18:38:41.073619+00:00

## Real data gain
- New canonical matches: **0**.
- New real players materialized: **59** from two public Football Squads cache artifacts for Brasileirão Série A 2024 (Flamengo and Palmeiras).
- New player-match rows: **0**. The squad source is season-roster data, not match participation.
- New lineups/events/xG/injuries/suspensions/Exact PIT: **0**.
- Existing 5,160 SHOTS/SOT were preserved and not counted as new.

## Remote acquisition
The runtime still cannot perform ordinary DNS resolution for arbitrary HTTP clients, so the existing acquisition worker cannot freely crawl remote JSON endpoints. However, a controlled web retrieval channel allowed legitimate public text/CSV artifacts to be verified and two player-squad files plus one Brazil match dataset were actually downloaded and checksumed. JSON-heavy StatsBomb artifacts were verified as publicly accessible but were **not** counted as materialized because the runtime download path rejects JSON content.

## Scientific safeguards
- No synthetic players.
- No lineups inferred from squads.
- No player-match stats inferred from roster data.
- No Exact PIT promotion.
- No snapshots overwritten.
- REAL_MONEY remains DISABLED.

## Next acquisition priorities
1. Run the V6 resumable workers on a normal Internet-connected machine to bulk-sync StatsBomb Open Data.
2. Configure API_FOOTBALL_KEY for the 100-request/day free tier and prioritize players/lineups/events/injuries/suspensions.
3. Add more Football Squads seasons/teams and a legal player database with stable IDs.
4. Add a timestamped odds source; free result/odds files do not solve Exact PIT.
