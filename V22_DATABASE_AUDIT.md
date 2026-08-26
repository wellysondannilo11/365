# V22 Database Audit

Added `db/migrations/005_v22_realtime.sql` with tables for realtime events, odds snapshots, decision traces, positions, observability events and research dataset rows, including uniqueness constraints and time/event indexes.

Added a SQLAlchemy `V22Persistence` adapter with conflict-safe inserts and DB health checking.

**Runtime PostgreSQL integration:** NOT EXECUTED — PostgreSQL/Docker were unavailable in the environment. The adapter reports `NOT_CONFIGURED` rather than fabricating connectivity.
