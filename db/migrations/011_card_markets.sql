-- Card-market extension. No real-money execution. Provider-agnostic and append-only.
CREATE TABLE IF NOT EXISTS v25_card_features (
  feature_id TEXT PRIMARY KEY,
  event_id TEXT NOT NULL,
  decision_time TIMESTAMPTZ NOT NULL,
  referee_id TEXT,
  referee_cards_avg DOUBLE PRECISION,
  referee_sample_size INTEGER NOT NULL DEFAULT 0,
  home_cards_avg DOUBLE PRECISION,
  home_sample_size INTEGER NOT NULL DEFAULT 0,
  away_cards_avg DOUBLE PRECISION,
  away_sample_size INTEGER NOT NULL DEFAULT 0,
  h2h_cards_avg DOUBLE PRECISION,
  h2h_sample_size INTEGER NOT NULL DEFAULT 0,
  match_importance DOUBLE PRECISION,
  match_intensity DOUBLE PRECISION,
  card_model TEXT,
  card_model_version TEXT NOT NULL,
  feature_version TEXT NOT NULL,
  source TEXT,
  source_timestamp TIMESTAMPTZ,
  captured_at TIMESTAMPTZ NOT NULL,
  quality TEXT NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  row_hash TEXT NOT NULL UNIQUE,
  previous_hash TEXT
);
CREATE INDEX IF NOT EXISTS idx_v25_card_features_event_time ON v25_card_features(event_id,decision_time);

CREATE TABLE IF NOT EXISTS v25_card_market_observations (
  observation_id TEXT PRIMARY KEY,
  event_id TEXT NOT NULL,
  snapshot_id TEXT,
  feature_id TEXT,
  bookmaker TEXT,
  market TEXT NOT NULL CHECK(market IN ('CARD_TOTALS','CARD_HOME','CARD_AWAY')),
  selection TEXT NOT NULL CHECK(selection IN ('OVER','UNDER')),
  line NUMERIC NOT NULL,
  odds DOUBLE PRECISION NOT NULL CHECK(odds > 1),
  fair_probability DOUBLE PRECISION,
  fair_odds DOUBLE PRECISION,
  edge DOUBLE PRECISION,
  ev DOUBLE PRECISION,
  decision TEXT NOT NULL CHECK(decision IN ('BET','NO BET','WATCH','WAIT_FOR_PRICE','HOLD','REDUCE','EXIT','REASSESS','REVERSE')),
  mode TEXT NOT NULL CHECK(mode IN ('PAPER','SHADOW')),
  source_timestamp TIMESTAMPTZ,
  captured_at TIMESTAMPTZ NOT NULL,
  decision_time TIMESTAMPTZ NOT NULL,
  row_hash TEXT NOT NULL UNIQUE,
  previous_hash TEXT,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_v25_card_market_event_time ON v25_card_market_observations(event_id,decision_time);
CREATE INDEX IF NOT EXISTS idx_v25_card_market_market ON v25_card_market_observations(market,selection,line);
