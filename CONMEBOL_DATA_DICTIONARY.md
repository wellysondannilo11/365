# CONMEBOL DATA DICTIONARY

`canonical_match_id`: deterministic SHA-256-derived match identity.
`competition`: Copa Libertadores or Copa Sudamericana.
`season`: competition season year.
`gender`: MEN for all materialized rows in this phase.
`stage`: normalized competition stage.
`group`: group label where source supplied it.
`match_date`: match date from source.
`home_team`, `away_team`: source team names, not aggressive entity-resolved aliases.
`home_goals`, `away_goals`: 90-minute/result score as represented by source; penalty shootout score is separately parsed when present.
`pit_status`: UNKNOWN for these historical results because decision-time market timestamps are absent.
`data_type`: HISTORICAL_REAL.
