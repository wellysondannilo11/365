CREATE TABLE IF NOT EXISTS raw_ingestion_batches_v14 (
  batch_id TEXT PRIMARY KEY,
  source TEXT NOT NULL,
  provider TEXT,
  endpoint TEXT,
  schema_version TEXT NOT NULL,
  dataset_version TEXT NOT NULL,
  source_hash TEXT,
  row_count BIGINT NOT NULL DEFAULT 0,
  status TEXT NOT NULL,
  metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS dataset_records_v14 (
  dataset_id TEXT NOT NULL,
  version TEXT NOT NULL,
  event_id TEXT NOT NULL,
  decision_time TIMESTAMPTZ,
  event_time TIMESTAMPTZ,
  source TEXT,
  source_record_ids JSONB,
  row_hash TEXT NOT NULL,
  PRIMARY KEY(dataset_id,event_id,version)
);
CREATE TABLE IF NOT EXISTS odds_snapshots_v14 (
  snapshot_id TEXT PRIMARY KEY,
  event_id TEXT NOT NULL,
  bookmaker TEXT NOT NULL,
  market TEXT NOT NULL,
  selection TEXT NOT NULL,
  line DOUBLE PRECISION,
  price DOUBLE PRECISION NOT NULL,
  captured_at TIMESTAMPTZ NOT NULL,
  source_timestamp TIMESTAMPTZ,
  available_at TIMESTAMPTZ,
  source TEXT NOT NULL,
  source_record_id TEXT,
  raw_hash TEXT NOT NULL,
  availability_evidence TEXT
);
CREATE INDEX IF NOT EXISTS idx_odds_snapshots_v14_event_time ON odds_snapshots_v14(event_id,captured_at);
CREATE TABLE IF NOT EXISTS validation_runs_v14 (
  validation_id TEXT PRIMARY KEY,
  dataset_id TEXT,
  dataset_hash TEXT,
  train_period TEXT,
  validation_period TEXT,
  test_period TEXT,
  holdout_period TEXT,
  status TEXT NOT NULL,
  metrics JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS data_quality_reports_v14 (
  report_id TEXT PRIMARY KEY,
  dataset_id TEXT,
  dataset_hash TEXT,
  status TEXT NOT NULL,
  report JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
