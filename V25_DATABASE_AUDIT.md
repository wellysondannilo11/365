# V25 Database Audit

**Status: SCHEMA IMPLEMENTED; runtime BLOCKED.**

Added `db/migrations/008_v25_consolidation.sql` with:

- market observations;
- unique snapshot identity;
- price-discovery fields;
- waiting opportunities;
- PAPER/SHADOW positions;
- settlements including half-win/half-loss/push;
- indexes and foreign keys.

PostgreSQL was not executed because no runtime/database service was available. This is therefore not reported as runtime PASS.
