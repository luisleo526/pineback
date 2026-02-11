---
name: timescale-ohlcv-ingestion
description: Market-agnostic OHLCV candle storage in TimescaleDB — hypertable schema design, compression policies, ingestion pipelines, resampling, and the DataSource protocol. Use when storing, ingesting, or querying historical OHLCV candle data for a backtest system.
---

# TimescaleDB OHLCV Ingestion

Market-agnostic OHLCV storage in TimescaleDB — schema, ingestion, resampling.

For system-wide architecture context, see [architecture.md](../architecture.md).

## Key Decisions

### Store at 1-Minute Resolution Only

All data enters as 1m bars. Higher timeframes (5m, 15m, 1h, 4h, 1d) are
derived via resampling in Python. This means:

- One table, one ingestion pipeline, one dedup strategy
- Magnifier-mode backtesting needs the fine-grained data anyway
- No materialized view maintenance per timeframe

### Schema

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE ohlcv (
    symbol      TEXT             NOT NULL,
    exchange    TEXT             NOT NULL,
    market_type TEXT             NOT NULL DEFAULT 'crypto',
    ts          TIMESTAMPTZ      NOT NULL,
    open        DOUBLE PRECISION NOT NULL,
    high        DOUBLE PRECISION NOT NULL,
    low         DOUBLE PRECISION NOT NULL,
    close       DOUBLE PRECISION NOT NULL,
    volume      DOUBLE PRECISION NOT NULL,
    CONSTRAINT valid_market_type CHECK (market_type IN (
        'crypto','stock','futures','options','forex',
        'index','etf','bond','cfd','warrant'))
);

SELECT create_hypertable('ohlcv', 'ts',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE);

-- Primary query: one symbol, date range
CREATE INDEX idx_ohlcv_sym_ts ON ohlcv (symbol, exchange, ts DESC);

-- Dedup: no duplicate bars
CREATE UNIQUE INDEX idx_ohlcv_unique
    ON ohlcv (symbol, exchange, market_type, ts);

-- Compression: 70-90% savings for historical data
ALTER TABLE ohlcv SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol, exchange, market_type',
    timescaledb.compress_orderby = 'ts');
SELECT add_compression_policy('ohlcv', INTERVAL '30 days', if_not_exists => TRUE);
```

**Why 7-day chunks:** ~10K rows/week/symbol at 1m. Good balance between
chunk count and per-chunk size.

**Why `market_type` as metadata, not logic:** Stocks have overnight gaps,
crypto doesn't. This column is informational — it helps understand expected
gaps and schedule ingestion, but the storage layer doesn't enforce
market-specific rules.

**Compressed chunks are read-only.** Backfilling historical data requires
decompressing first (`SELECT decompress_chunk(...)`). The compression policy
re-compresses automatically.

### Resampling

```python
RESAMPLE_RULES = {
    "1m": "1min", "3m": "3min", "5m": "5min", "15m": "15min",
    "30m": "30min", "1h": "1h", "4h": "4h", "1d": "1D",
}

def resample_ohlcv(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    if timeframe == "1m":
        return df
    return df.resample(RESAMPLE_RULES[timeframe]).agg({
        "open": "first", "high": "max", "low": "min",
        "close": "last", "volume": "sum",
    }).dropna()  # Critical: partial periods produce NaN
```

For API-facing queries where latency matters, use TimescaleDB continuous
aggregates instead of Python resampling:

```sql
CREATE MATERIALIZED VIEW ohlcv_1h WITH (timescaledb.continuous) AS
SELECT symbol, exchange, time_bucket('1 hour', ts) AS ts,
       first(open, ts) AS open, max(high) AS high,
       min(low) AS low, last(close, ts) AS close, sum(volume) AS volume
FROM ohlcv GROUP BY symbol, exchange, time_bucket('1 hour', ts);
```

### DataSource Protocol

Abstract data loading so the backtest engine doesn't care where data lives:

```python
class DataSource(Protocol):
    def load_1m(self, symbol: str, exchange: str,
                start: str | None = None, end: str | None = None
    ) -> pd.DataFrame:
        """UTC DatetimeIndex, columns: open, high, low, close, volume."""
        ...
```

Implementations: DiskSource (local .npz/.parquet), TimescaleSource (SQL),
APISource (live data vendor). The backtest engine takes any DataSource.

### Ingestion Pattern

Any ingestion pipeline should be **resume-capable**:

1. Query `SELECT max(ts)` for the symbol to find where you left off
2. Fetch from that point forward
3. Bulk insert with `ON CONFLICT (symbol, exchange, market_type, ts) DO NOTHING`
4. Retry on rate limits (sleep 10s) and network errors (backoff)

Design the fetcher with a **provider interface** so new data sources
(CCXT, yfinance, broker APIs) slot in without changing the pipeline:

```python
class DataProvider(Protocol):
    def fetch_ohlcv(self, symbol: str, timeframe: str,
                    since: datetime, limit: int = 1000) -> list[OHLCVBar]: ...
```

## Pitfalls

| Pitfall | Prevention |
|---------|-----------|
| Timestamps without timezone | Always `TIMESTAMPTZ` + UTC |
| Missing `.dropna()` after resample | NaN breaks indicator calculations |
| Inserting into compressed chunks | Decompress first; policy re-compresses |
| Naive (tz-unaware) DatetimeIndex | Always `tz='UTC'` — pandas raises TypeError on mixed joins |
| Volume=0 bars | Valid data; handle in indicator code, not storage |
