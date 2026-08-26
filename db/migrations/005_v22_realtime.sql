CREATE TABLE IF NOT EXISTS v22_events (
 id BIGSERIAL PRIMARY KEY, event_id TEXT NOT NULL, event_time TIMESTAMPTZ, captured_at TIMESTAMPTZ NOT NULL,
 source TEXT NOT NULL, sequence BIGINT, payload_hash TEXT NOT NULL, payload JSONB NOT NULL,
 UNIQUE(event_id, sequence, payload_hash)
);
CREATE INDEX IF NOT EXISTS idx_v22_events_event_time ON v22_events(event_id, captured_at);
CREATE TABLE IF NOT EXISTS v22_odds_snapshots (
 id BIGSERIAL PRIMARY KEY, event_id TEXT NOT NULL, bookmaker TEXT, market TEXT NOT NULL, selection TEXT NOT NULL,
 line DOUBLE PRECISION, price DOUBLE PRECISION NOT NULL, captured_at TIMESTAMPTZ NOT NULL, source_timestamp TIMESTAMPTZ,
 available_at TIMESTAMPTZ, source TEXT NOT NULL, raw_hash TEXT NOT NULL,
 UNIQUE(event_id, bookmaker, market, selection, line, captured_at, raw_hash)
);
CREATE INDEX IF NOT EXISTS idx_v22_odds_event_captured ON v22_odds_snapshots(event_id, captured_at);
CREATE TABLE IF NOT EXISTS v22_decision_trace (
 trace_id TEXT PRIMARY KEY, event_id TEXT NOT NULL, decision TEXT NOT NULL, why TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL,
 model_version TEXT, feature_version TEXT, pricing_version TEXT, config_version TEXT, data_snapshot_id TEXT,
 pit_status TEXT NOT NULL, inputs JSONB, outputs JSONB, reasons JSONB
);
CREATE TABLE IF NOT EXISTS v22_positions (
 position_id TEXT PRIMARY KEY, event_id TEXT NOT NULL, mode TEXT NOT NULL, market TEXT NOT NULL, selection TEXT NOT NULL,
 entry_odds DOUBLE PRECISION NOT NULL, stake_units DOUBLE PRECISION NOT NULL, status TEXT NOT NULL,
 entry_at TIMESTAMPTZ NOT NULL, exit_at TIMESTAMPTZ, exit_odds DOUBLE PRECISION, pnl_units DOUBLE PRECISION,
 exit_reason TEXT, metadata JSONB
);
CREATE TABLE IF NOT EXISTS v22_observability_events (
 id BIGSERIAL PRIMARY KEY, created_at TIMESTAMPTZ NOT NULL, event_type TEXT NOT NULL, trace_id TEXT, payload JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS v22_dataset_rows (
 row_id TEXT PRIMARY KEY, event_id TEXT, decision TEXT, mode TEXT, decision_time TIMESTAMPTZ, outcome TEXT,
 row_hash TEXT NOT NULL, payload JSONB NOT NULL, created_at TIMESTAMPTZ NOT NULL
);
