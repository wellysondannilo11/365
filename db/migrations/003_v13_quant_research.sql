CREATE TABLE IF NOT EXISTS raw_records (
 id BIGSERIAL PRIMARY KEY, provider TEXT NOT NULL, endpoint TEXT, event_id TEXT, source_time TIMESTAMPTZ,
 available_at TIMESTAMPTZ, ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(), raw_hash TEXT NOT NULL, payload JSONB NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_raw_hash ON raw_records(raw_hash);
CREATE TABLE IF NOT EXISTS dataset_versions (
 dataset_id TEXT PRIMARY KEY, source TEXT, dataset_hash TEXT NOT NULL, row_count BIGINT NOT NULL,
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(), status TEXT NOT NULL, metadata JSONB
);
CREATE TABLE IF NOT EXISTS feature_lineage_v13 (
 id BIGSERIAL PRIMARY KEY,event_id TEXT NOT NULL,entity_id TEXT,feature_name TEXT NOT NULL,feature_version TEXT NOT NULL,
 event_time TIMESTAMPTZ,source_time TIMESTAMPTZ,available_at TIMESTAMPTZ NOT NULL,ingested_at TIMESTAMPTZ,decision_time TIMESTAMPTZ NOT NULL,
 source TEXT,source_record_ids JSONB,lineage JSONB,value DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS idx_feature_lineage_v13_event_decision ON feature_lineage_v13(event_id,decision_time);
CREATE TABLE IF NOT EXISTS experiments_v13 (
 experiment_id TEXT PRIMARY KEY,code_hash TEXT,dataset_hash TEXT,feature_version TEXT,model TEXT,hyperparameters JSONB,
 markets JSONB,leagues JSONB,period TEXT,threshold DOUBLE PRECISION,stake_policy TEXT,seed INTEGER,result JSONB,status TEXT,created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS model_registry_v13 (
 model_id TEXT PRIMARY KEY,model_name TEXT,version TEXT,dataset_hash TEXT,feature_hash TEXT,code_hash TEXT,
 training_period TEXT,validation_period TEXT,test_period TEXT,holdout_period TEXT,hyperparameters JSONB,seed INTEGER,
 calibrator TEXT,threshold DOUBLE PRECISION,stake_policy TEXT,package_versions JSONB,metrics JSONB,status TEXT,created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS calibrators_v13 (
 calibrator_id TEXT PRIMARY KEY,market TEXT,method TEXT,training_period TEXT,calibration_period TEXT,test_period TEXT,metadata JSONB,created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS decision_snapshots_v13 (
 decision_id TEXT PRIMARY KEY,event_id TEXT,decision_time TIMESTAMPTZ,market TEXT,selection TEXT,line DOUBLE PRECISION,bookmaker TEXT,odds DOUBLE PRECISION,
 p_sport DOUBLE PRECISION,p_market DOUBLE PRECISION,p_hybrid DOUBLE PRECISION,p_raw DOUBLE PRECISION,p_calibrated DOUBLE PRECISION,p_final DOUBLE PRECISION,
 fair_probability DOUBLE PRECISION,fair_odds DOUBLE PRECISION,edge DOUBLE PRECISION,ev DOUBLE PRECISION,uncertainty DOUBLE PRECISION,data_quality DOUBLE PRECISION,
 model_version TEXT,feature_version TEXT,dataset_hash TEXT,risk_state JSONB,stake DOUBLE PRECISION,decision TEXT,reason TEXT,replay_hash TEXT,created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS metrics_v13 (
 id BIGSERIAL PRIMARY KEY,scope TEXT,scope_id TEXT,metric TEXT,value DOUBLE PRECISION,period TEXT,metadata JSONB,created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS drift_v13 (
 id BIGSERIAL PRIMARY KEY,metric TEXT,feature TEXT,value DOUBLE PRECISION,threshold DOUBLE PRECISION,status TEXT,period TEXT,created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS bookmaker_quality_v13 (
 bookmaker TEXT PRIMARY KEY,score DOUBLE PRECISION,as_of TIMESTAMPTZ,method TEXT,metadata JSONB
);
CREATE TABLE IF NOT EXISTS holdout_state_v13 (
 id INTEGER PRIMARY KEY CHECK(id=1),state TEXT NOT NULL,locked_at TIMESTAMPTZ,metadata JSONB
);
INSERT INTO holdout_state_v13(id,state) VALUES(1,'RESEARCH') ON CONFLICT(id) DO NOTHING;
