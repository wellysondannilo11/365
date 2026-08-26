# Context Intelligence + Player Impact + Global Pattern Discovery

Run: 2026-08-20T16:06:04.375384+00:00

## Scientific status
- REAL_MONEY = DISABLED
- Current materialized sample: **3,694 real matches**.
- Current coverage: 3 countries, 6 competitions, 3 seasons.
- Competition-season pairs: 9 (this is distinct from competition count).
- PIT validated odds: 0.
- Historical LIVE snapshots: 0.
- Player/injury/lineup datasets: not materialized; no player conclusions were fabricated.

## Core findings
- Home advantage is directly measurable in the current sample, but it is descriptive and not a claim of betting edge.
- Division/competition differences are reported with sample sizes and FDR adjustment.
- Rolling team form features are strictly shifted to pre-match information and are used only where prior history exists.
- OOS/HOLDOUT model tests are separated temporally.

## Context limitations
Objective motivation, aggregate qualification state, derby status, injuries, suspensions, lineups, player impact, xG and historical LIVE cannot be reconstructed reliably from the current materialized datasets. These remain `INSUFFICIENT_DATA` rather than being inferred.

## Odds/PIT limitation
The existing odds are primarily `NON_PIT` and some records are `PIT_DATE_ONLY`; they are not promoted to exact PIT. Therefore no temporal market edge is claimed.

## Gender
All current materialized matches are male. Female football remains structurally separate and currently has zero materialized rows.

See CSV/JSON outputs under `data/research/` and the audit JSON for exact counts.
