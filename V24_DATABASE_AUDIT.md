# V24 Database Audit

Added migration `db/migrations/007_v24_production.sql`.

Tables:
- `v24_sessions`
- `v24_snapshots`
- `v24_decisions`
- `v24_positions`
- `v24_settlements`
- `v24_hash_heads`

Constraints cover PAPER/SHADOW modes, decision types, settlement states and unique snapshot/position identities.

Migration syntax was inspected as SQL source, but PostgreSQL execution was **BLOCKED** because no PostgreSQL runtime was available.
