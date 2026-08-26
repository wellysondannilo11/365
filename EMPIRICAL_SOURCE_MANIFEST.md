# EMPIRICAL_SOURCE_MANIFEST — FOOTBALL ONLY

## Source 1 — Football-Data.co.uk
- Type: historical football results/statistics/odds
- Coverage: season-by-season, multiple English and European leagues
- Web verification: PASS
- Local byte acquisition: BLOCKED
- Scientific status: NOT_PROCESSED

## Source 2 — AnishKhetani/premier-league-data
- Type: historical EPL results + bookmaker odds
- Coverage documented by source: 1993-94 onward, 12,700+ matches
- Opening/closing 1X2, Over/Under 2.5 and Asian Handicap fields documented
- Web verification: PASS
- Local byte acquisition: BLOCKED
- Scientific status: NOT_PROCESSED

## Source 3 — DataHub English Premier League
- Type: historical EPL results + match statistics
- Coverage: 1993/94 onward
- Fields documented: referee, shots, fouls, corners, yellow/red cards where available
- Web verification: PASS
- Local byte acquisition: BLOCKED
- Scientific status: NOT_PROCESSED

## Source 4 — API providers
- The Odds API: BLOCKED — credential absent
- API-Football: BLOCKED — credential absent

## Rule
A source is not classified as `HISTORICAL_REAL_PROCESSED` until its bytes are loaded into the local pipeline and pass the data-quality/PIT gates.
