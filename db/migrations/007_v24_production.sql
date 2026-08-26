-- V24 production observation layer. Real-money execution is intentionally absent.
CREATE TABLE IF NOT EXISTS v24_sessions (
  session_id TEXT PRIMARY KEY,
  mode TEXT NOT NULL CHECK (mode IN ('PAPER','SHADOW')),
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  stopped_at TIMESTAMPTZ,
  status TEXT NOT NULL DEFAULT 'RUNNING',
  provider TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE IF NOT EXISTS v24_snapshots (
  snapshot_id TEXT PRIMARY KEY,
  event_id TEXT NOT NULL,
  provider TEXT NOT NULL,
  bookmaker TEXT,
  market TEXT,
  selection TEXT,
  line NUMERIC,
  odds DOUBLE PRECISION,
  source_timestamp TIMESTAMPTZ NOT NULL,
  captured_at TIMESTAMPTZ NOT NULL,
  payload JSONB NOT NULL,
  row_hash TEXT NOT NULL,
  UNIQUE(event_id,provider,bookmaker,market,selection,line,source_timestamp,odds)
);
CREATE INDEX IF NOT EXISTS idx_v24_snapshots_event_time ON v24_snapshots(event_id,source_timestamp);
CREATE TABLE IF NOT EXISTS v24_decisions (
  decision_id TEXT PRIMARY KEY,
  session_id TEXT,
  event_id TEXT NOT NULL,
  snapshot_id TEXT,
  decision TEXT NOT NULL CHECK(decision IN ('BET','NO BET','HOLD','REDUCE','EXIT','REASSESS')),
  mode TEXT NOT NULL CHECK(mode IN ('PAPER','SHADOW')),
  decision_time TIMESTAMPTZ NOT NULL,
  fair_probability DOUBLE PRECISION,
  fair_odds DOUBLE PRECISION,
  edge DOUBLE PRECISION,
  ev DOUBLE PRECISION,
  stake_units DOUBLE PRECISION DEFAULT 0,
  reason TEXT,
  model_version TEXT NOT NULL,
  feature_version TEXT NOT NULL,
  pricing_version TEXT NOT NULL,
  payload JSONB NOT NULL,
  row_hash TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_v24_decisions_event_time ON v24_decisions(event_id,decision_time);
CREATE TABLE IF NOT EXISTS v24_positions (
  position_id TEXT PRIMARY KEY,
  decision_id TEXT NOT NULL UNIQUE,
  event_id TEXT NOT NULL,
  mode TEXT NOT NULL CHECK(mode IN ('PAPER','SHADOW')),
  status TEXT NOT NULL CHECK(status IN ('OPEN','SETTLED','EXITED')),
  entry_odds DOUBLE PRECISION NOT NULL,
  stake_units DOUBLE PRECISION NOT NULL,
  opened_at TIMESTAMPTZ NOT NULL,
  closed_at TIMESTAMPTZ,
  payload JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS v24_settlements (
  settlement_id TEXT PRIMARY KEY,
  position_id TEXT NOT NULL UNIQUE,
  result TEXT NOT NULL CHECK(result IN ('WIN','LOSS','VOID')),
  closing_odds DOUBLE PRECISION,
  pnl_units DOUBLE PRECISION NOT NULL,
  clv DOUBLE PRECISION,
  settled_at TIMESTAMPTZ NOT NULL,
  payload JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS v24_hash_heads (
  dataset_version TEXT PRIMARY KEY,
  head_hash TEXT,
  row_count BIGINT NOT NULL DEFAULT 0,
  verified_at TIMESTAMPTZ
);
