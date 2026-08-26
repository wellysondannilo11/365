-- V25 consolidation: market expression, price discovery, waiting opportunities,
-- live position management and dataset lineage. No real-money execution.
CREATE TABLE IF NOT EXISTS v25_market_observations (
  observation_id TEXT PRIMARY KEY,
  event_id TEXT NOT NULL,
  snapshot_id TEXT NOT NULL,
  provider TEXT NOT NULL,
  bookmaker TEXT,
  market TEXT NOT NULL,
  line NUMERIC,
  selection TEXT NOT NULL,
  odds DOUBLE PRECISION NOT NULL CHECK (odds > 1),
  source_timestamp TIMESTAMPTZ NOT NULL,
  captured_at TIMESTAMPTZ NOT NULL,
  opening_price DOUBLE PRECISION,
  current_price DOUBLE PRECISION,
  price_velocity DOUBLE PRECISION,
  price_acceleration DOUBLE PRECISION,
  fair_probability DOUBLE PRECISION,
  fair_odds DOUBLE PRECISION,
  edge DOUBLE PRECISION,
  ev DOUBLE PRECISION,
  uncertainty DOUBLE PRECISION,
  decision TEXT NOT NULL CHECK(decision IN ('BET','NO BET','WATCH','HOLD','REDUCE','EXIT','REASSESS','REVERSE')),
  mode TEXT NOT NULL CHECK(mode IN ('PAPER','SHADOW')),
  decision_id TEXT NOT NULL UNIQUE,
  row_hash TEXT NOT NULL,
  previous_hash TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_v25_snapshot_identity ON v25_market_observations(event_id,provider,bookmaker,market,selection,line,source_timestamp,odds);
CREATE INDEX IF NOT EXISTS idx_v25_event_time ON v25_market_observations(event_id,source_timestamp);
CREATE INDEX IF NOT EXISTS idx_v25_market ON v25_market_observations(market,selection,line);

CREATE TABLE IF NOT EXISTS v25_waiting_opportunities (
  watch_id TEXT PRIMARY KEY,
  event_id TEXT NOT NULL,
  market TEXT NOT NULL,
  selection TEXT NOT NULL,
  target_odds DOUBLE PRECISION NOT NULL CHECK(target_odds > 1),
  current_odds DOUBLE PRECISION NOT NULL CHECK(current_odds > 1),
  fair_odds DOUBLE PRECISION,
  created_at TIMESTAMPTZ NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('WATCH','TRIGGERED','EXPIRED','CANCELLED')),
  decision_id TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS v25_positions (
  position_id TEXT PRIMARY KEY,
  event_id TEXT NOT NULL,
  decision_id TEXT NOT NULL UNIQUE,
  mode TEXT NOT NULL CHECK(mode IN ('PAPER','SHADOW')),
  market TEXT NOT NULL,
  selection TEXT NOT NULL,
  line NUMERIC,
  entry_odds DOUBLE PRECISION NOT NULL,
  stake_units DOUBLE PRECISION NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('OPEN','CLOSED','SETTLED')),
  opened_at TIMESTAMPTZ NOT NULL,
  closed_at TIMESTAMPTZ,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS v25_settlements (
  settlement_id TEXT PRIMARY KEY,
  position_id TEXT NOT NULL UNIQUE REFERENCES v25_positions(position_id),
  result TEXT NOT NULL CHECK(result IN ('WIN','HALF_WIN','PUSH','HALF_LOSS','LOSS','VOID')),
  closing_odds DOUBLE PRECISION,
  pnl_units DOUBLE PRECISION NOT NULL,
  clv DOUBLE PRECISION,
  settled_at TIMESTAMPTZ NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE IF NOT EXISTS v25_watchlist (
  watch_id TEXT PRIMARY KEY,
  event_id TEXT NOT NULL,
  market TEXT NOT NULL,
  selection TEXT NOT NULL,
  line NUMERIC,
  target_odds DOUBLE PRECISION NOT NULL CHECK(target_odds > 1),
  current_odds DOUBLE PRECISION NOT NULL CHECK(current_odds > 1),
  fair_odds DOUBLE PRECISION,
  created_at TIMESTAMPTZ NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('WATCH','TRIGGERED','EXPIRED','CANCELLED'))
);
