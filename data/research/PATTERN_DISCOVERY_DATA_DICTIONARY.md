# Pattern Discovery Data Dictionary

All derived features are generated from materialized real historical observations. Rolling features are shifted: only matches strictly before the current kickoff contribute.

Key fields: `home_goals_for_5`, `away_goals_for_5`, `home_shots_for_5`, `away_shots_for_5`, `home_sot_for_5`, `away_sot_for_5`, `rest_home_days`, `rest_away_days`, `matches_home_7d`, `matches_away_7d`, `strength_attack_diff`, `strength_defense_diff`.

Context fields `motivation_state`, `importance_state`, `derby_state`, `leg_state` are explicitly `UNKNOWN` because no auditable pre-match competition-state source is materialized.

Gender is explicit; current materialized sample contains MALE only.
