-- Raw point-in-time observations. Distinct from decisions and settlements.
CREATE TABLE IF NOT EXISTS v25_observation_snapshots (
  snapshot_id TEXT PRIMARY KEY,
  event_id TEXT NOT NULL,
  provider TEXT NOT NULL,
  bookmaker TEXT,
  market TEXT,
  selection TEXT,
  line NUMERIC,
  odds DOUBLE PRECISION NOT NULL CHECK (odds > 1),
  source_timestamp TIMESTAMPTZ NOT NULL,
  captured_at TIMESTAMPTZ NOT NULL,
  received_at TIMESTAMPTZ NOT NULL,
  mode TEXT NOT NULL CHECK(mode IN ('PRE','LIVE')),
  payload JSONB NOT NULL,
  row_hash TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_v25_snapshots_event_time ON v25_observation_snapshots(event_id,source_timestamp);
CREATE INDEX IF NOT EXISTS idx_v25_snapshots_captured ON v25_observation_snapshots(captured_at);
