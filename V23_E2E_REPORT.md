# V23 E2E Report

Controlled code path: provider normalization → quality/freshness → baseline candidate → V21 decision service → dataset/replay/persistence is wired. Full provider → Spring → PostgreSQL → Redis → ML → decision → ledger → Telegram → frontend runtime E2E was not executed because required services/credentials were unavailable.
