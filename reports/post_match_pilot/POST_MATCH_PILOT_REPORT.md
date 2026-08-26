# POST-MATCH PILOT — FORENSICS + COVERAGE AUDIT

Audit timestamp (UTC): `2026-08-20T16:57:22.525871+00:00`

## Snapshot integrity
- Snapshot file: `data/real_day_prematch/REAL_DAY_PREMATCH_SNAPSHOT.json`
- Snapshot SHA-256: `97f83c1d992a8ea36bca44a8e14bb4d21e4c1d8024463e715f1bf24cba7c5c5c`
- Prospectively recorded matches: **5**
- Original snapshots were not modified.

## Post-match status
The five 20/08/2026 fixtures are scheduled for later on the audit date. At this execution time, authoritative post-match results are not yet available. Therefore the forensic section remains **PENDING** and no score, winner, Brier, Log Loss, ROI or CLV has been invented.

| Jogo | Status | Resultado | Avaliação |
|---|---|---|---|
| LDU Quito x Mirassol | NOT_COMPLETED_AT_AUDIT | UNKNOWN | NOT_SETTLEABLE |
| Olimpia x Vasco | NOT_COMPLETED_AT_AUDIT | UNKNOWN | NOT_SETTLEABLE |
| Macará x Santos | NOT_COMPLETED_AT_AUDIT | UNKNOWN | NOT_SETTLEABLE |
| Corinthians x Rosario Central | NOT_COMPLETED_AT_AUDIT | UNKNOWN | NOT_SETTLEABLE |
| Botafogo x Cienciano | NOT_COMPLETED_AT_AUDIT | UNKNOWN | NOT_SETTLEABLE |

### Scientific interpretation
`SAMPLE_SIZE = 0 SETTLED` for this post-match execution. The prospective sample remains preserved for later settlement. A result cannot be used to claim edge or no-edge before the games end.

## Coverage diagnosis
The current materialized feature store contains strong historical match counts in a limited set of competitions, but several of the five pilot clubs have zero local historical rows in the feature store. This blocks independent team-specific pricing and is the principal coverage bottleneck.

See `TEAM_COVERAGE_5_PILOT_TEAMS.csv` and `DATA_COVERAGE_2020_2026.csv`.
