# US Stock Backtesting System

A full-stack backtesting platform with a no-code strategy builder, PineScript v6 compiler, and TradingView-style results.

> **Live demo**: [interview.4pass.io](https://interview.4pass.io)

## Quick Start

```bash
# Start database (TimescaleDB + PgBouncer)
cd server/docker && docker compose up -d && cd ../..

# Ingest SPY data (~2M 1-minute bars, 2008-2021)
python -m server.ingest

# Start backend
uvicorn server.main:app --reload --port 8000

# Start frontend (in another terminal)
cd frontend && npm install && npm run dev
# Open http://localhost:5173
```

## Documentation

Full documentation available at [interview.4pass.io](https://interview.4pass.io) (landing page).

<!-- Expanded in commit 22 -->
