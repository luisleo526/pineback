# Backtest System — Architecture Overview

Skills that teach agents the domain knowledge needed to build a
**pure backtest system** with a simple fullstack frontend.

These skills are **generic** — they describe concepts, patterns, and pitfalls,
not a specific codebase. An agent can use them to build a backtest system
from scratch or maintain an existing one.

They are **market-agnostic** — they apply to crypto, stocks, futures, forex,
or any instrument that produces OHLCV candles.

## Skill Map

```
  +---------------------------------+
  |  timescale-ohlcv-ingestion      |  Data layer
  |  Store & retrieve candles       |
  +--------------+------------------+
                 |
  +--------------v------------------+
  |  pinescript-compiler            |  Strategy definition
  |  PineScript v6 → Python        |
  |  + Technical indicator library  |
  +--------------+------------------+
                 |
  +--------------v------------------+
  |  vectorbt-magnifier-backtest    |  Execution engine
  |  Standard + magnifier modes     |
  +--------------+------------------+
                 |
  +--------------v------------------+
  |  fastapi-backtest-server        |  Backend API
  |  REST endpoints, async jobs     |
  +--------------+------------------+
                 |
  +--------------v------------------+
  |  backtest-results-frontend      |  Presentation
  |  Charts, tables, stats          |
  +---------------------------------+
```

## Architecture Principles

- **1-minute base data** — all OHLCV stored at 1m resolution; higher timeframes
  derived via resampling
- **4-signal model** — strategies produce `(long_entry, long_exit, short_entry,
  short_exit)` boolean Series — the universal contract between compiler and
  execution engine
- **PineScript as lingua franca** — users write/validate on TradingView, then
  the same code runs in the backtest engine
- **Magnifier for realism** — higher-TF backtests iterate sub-bars to find
  exact signal trigger points, not just bar-close
- **DataSource protocol** — abstract interface allows plugging in new data
  providers (disk, TimescaleDB, API) without changing the execution engine
