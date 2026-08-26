# LOCAL DATA REDISCOVERY REPORT V7

The V6 ZIP was recursively inspected after extraction.

Key verified local assets:

- `data/enrichment/free_data/MATCH_STATISTICS_FREE.csv`: 5,160 rows.
- `data/enrichment/free_data/PLAYER_MASTER_V6.csv`: 59 rows.
- `data/enrichment/free_data/PLAYER_ENTITY_RESOLUTION_V6.csv`: 59 rows.
- `data/master_staff/PLAYER_MATCH`-type engine tables: empty.
- `data/master_staff/LINEUP_RECORDS.csv`: 0 rows.
- `data/master_staff/INJURY_RECORDS.csv`: 0 rows.
- `data/master_staff/SUSPENSION_ENGINE_RECORDS.csv`: 0 rows.
- `data/processed/odds_observations_real_nonpit.csv`: existing non-PIT odds materialization.
- `data/master_staff/PREMATCH_FEATURE_STORE.csv`: protected snapshot.
- `data/real_day_prematch/REAL_DAY_PREMATCH_SNAPSHOT.json`: protected snapshot.

No hidden local dataset was promoted to a canonical layer merely because it existed in a report or engine scaffold.
