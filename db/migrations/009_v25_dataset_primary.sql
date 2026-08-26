-- V25 empirical dataset primary persistence. JSONL remains a local forensic mirror.
CREATE TABLE IF NOT EXISTS v25_dataset_rows (
  observation_id TEXT PRIMARY KEY,
  event_id TEXT,
  mode TEXT NOT NULL CHECK(mode IN ('PAPER','SHADOW')),
  decision TEXT NOT NULL,
  decision_time TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL,
  row_hash TEXT NOT NULL UNIQUE,
  previous_hash TEXT,
  payload JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_v25_dataset_event_time ON v25_dataset_rows(event_id,created_at);
CREATE INDEX IF NOT EXISTS idx_v25_dataset_decision ON v25_dataset_rows(decision,created_at);
