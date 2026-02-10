-- Backtest database initialization
-- Runs once on first container start (via docker-entrypoint-initdb.d)

-- Enable TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================================================
-- OHLCV Table (TimescaleDB hypertable)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ohlcv (
    symbol      TEXT             NOT NULL,
    exchange    TEXT             NOT NULL,
    market_type TEXT             NOT NULL DEFAULT 'etf',
    ts          TIMESTAMPTZ      NOT NULL,
    open        DOUBLE PRECISION NOT NULL,
    high        DOUBLE PRECISION NOT NULL,
    low         DOUBLE PRECISION NOT NULL,
    close       DOUBLE PRECISION NOT NULL,
    volume      DOUBLE PRECISION NOT NULL,

    CONSTRAINT valid_ohlcv_market_type CHECK (market_type IN (
        'futures','options','stock','crypto','forex','index','etf','bond','cfd','warrant'
    ))
);

-- Convert to TimescaleDB hypertable (auto-partitions by time)
-- chunk_time_interval = 7 days (good balance for 1m data)
SELECT create_hypertable(
    'ohlcv', 'ts',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);

-- Composite index for the primary query pattern:
-- WHERE symbol = X AND exchange = Y AND ts BETWEEN A AND B
CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_exchange_ts
    ON ohlcv (symbol, exchange, ts DESC);

-- Unique constraint to prevent duplicate bars
CREATE UNIQUE INDEX IF NOT EXISTS idx_ohlcv_unique
    ON ohlcv (symbol, exchange, market_type, ts);

-- Enable TimescaleDB compression (huge storage savings for historical data)
ALTER TABLE ohlcv SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol, exchange, market_type',
    timescaledb.compress_orderby = 'ts'
);

-- Auto-compress chunks older than 30 days
SELECT add_compression_policy('ohlcv', INTERVAL '30 days', if_not_exists => TRUE);

-- ============================================================================
-- Backtests Table (job tracking + results)
-- ============================================================================

CREATE TABLE IF NOT EXISTS backtests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_name   TEXT            NOT NULL,
    pinescript      TEXT            NOT NULL,
    symbol          TEXT            NOT NULL,
    exchange        TEXT            NOT NULL,
    timeframe       TEXT            NOT NULL,
    start_date      DATE,
    end_date        DATE,
    initial_capital NUMERIC(20,2)   NOT NULL DEFAULT 10000,
    params          JSONB           NOT NULL DEFAULT '{}',
    mode            TEXT            NOT NULL DEFAULT 'magnifier',

    -- Lifecycle tracking
    status          TEXT            NOT NULL DEFAULT 'pending',
    progress        INTEGER         NOT NULL DEFAULT 0,
    progress_message TEXT           NOT NULL DEFAULT '',
    error_message   TEXT,
    submitted_at    TIMESTAMPTZ     NOT NULL DEFAULT now(),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,

    -- Denormalized summary stats (populated on completion, for fast listing)
    total_return    NUMERIC(12,4),
    sharpe_ratio    NUMERIC(8,4),
    max_drawdown    NUMERIC(8,4),
    win_rate        NUMERIC(8,4),
    total_trades    INTEGER,
    profit_factor   NUMERIC(8,4),
    final_value     NUMERIC(20,2),

    -- Full result payload (equity curve, trades, orders, charts, etc.)
    result_json     JSONB,

    CONSTRAINT valid_status CHECK (status IN ('pending','running','completed','failed')),
    CONSTRAINT valid_mode CHECK (mode IN ('standard','magnifier'))
);

-- Index for listing backtests (most recent first)
CREATE INDEX IF NOT EXISTS idx_backtests_submitted
    ON backtests (submitted_at DESC);

-- Index for finding active jobs (pending/running)
CREATE INDEX IF NOT EXISTS idx_backtests_active
    ON backtests (status)
    WHERE status IN ('pending', 'running');
