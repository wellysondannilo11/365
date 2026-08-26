CREATE TABLE IF NOT EXISTS v23_observations (row_id TEXT PRIMARY KEY,event_id TEXT,decision TEXT NOT NULL,mode TEXT NOT NULL CHECK(mode IN ('PAPER','SHADOW')),decision_time TIMESTAMPTZ NOT NULL,payload JSONB NOT NULL,row_hash TEXT NOT NULL,prev_hash TEXT,created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE INDEX IF NOT EXISTS idx_v23_obs_event_time ON v23_observations(event_id,decision_time);
CREATE TABLE IF NOT EXISTS v23_provider_quality (id BIGSERIAL PRIMARY KEY,provider TEXT NOT NULL,checked_at TIMESTAMPTZ NOT NULL,status TEXT NOT NULL,latency_ms DOUBLE PRECISION,source_timestamp TIMESTAMPTZ,age_seconds DOUBLE PRECISION,details JSONB);
CREATE TABLE IF NOT EXISTS v23_model_approvals (model_version TEXT PRIMARY KEY,dataset_hash TEXT NOT NULL,approved_at TIMESTAMPTZ,approved_by TEXT,status TEXT NOT NULL CHECK(status IN ('CANDIDATE','APPROVED','REJECTED','RETIRED')));
CREATE INDEX IF NOT EXISTS idx_v22_odds_source_time ON v22_odds_snapshots(source,source_timestamp);
