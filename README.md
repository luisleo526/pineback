# US Stock Backtesting System

A full-stack, verifiable and reproducible backtesting platform with a no-code visual strategy builder, PineScript v6 compiler, and TradingView-style results.

> **Live demo**: [interview.4pass.io](https://interview.4pass.io)

---

## Metrics

Every backtest produces a comprehensive set of performance metrics:

- **CAGR / Annualized Return** — compound annual growth rate
- **Annualized Volatility** — standard deviation of returns, annualized
- **Sharpe Ratio** — risk-adjusted return (excess return / volatility)
- **Sortino Ratio** — downside-risk-adjusted return
- **Max Drawdown** — largest peak-to-trough decline (% and duration)
- **Profit Factor** — gross profit / gross loss
- **Win Rate** — percentage of winning trades
- **Expectancy** — average profit per trade
- **Total Trades, Best/Worst Trade, Avg Win/Loss, Avg Duration**

## Architecture

```
Browser (Vue 3 SPA)
  ├─ /           Landing page (project documentation)
  └─ /app        Strategy Builder + Backtest Dashboard
  └─ /result/:id Full-page backtest results
        │
        │ POST /api/backtests ── compile PineScript ── BackgroundTask
        │ GET  /api/backtests/{id} ── poll progress (0-100%) / get result
        │
FastAPI (uvicorn)
  ├── PineScript v6 Compiler (tokenizer → parser → AST → codegen)
  ├── 37 Technical Indicators (ta.py)
  ├── vectorbt Portfolio.from_signals() (standard + magnifier mode)
  └── TimescaleDB via PgBouncer
        ├── ohlcv (hypertable, ~1.4M 1-minute SPY bars, 2008-2021)
        └── backtests (job tracking + result storage)
```

## Features

| Feature | Description | Use Case |
|---------|-------------|----------|
| No-code strategy builder | Visual condition builder with 40+ indicators, AND/OR logic, custom variables, math expressions | Non-programmers can build and test trading strategies |
| PineScript v6 compiler | Tokenizer → Parser → AST → Python codegen | Execute TradingView-compatible strategies programmatically |
| Magnifier mode | Iterates sub-bars for realistic intra-bar fill prices on higher timeframes | Avoid unrealistic bar-close fills on 1h/4h/1d backtests |
| OHLCV chart + markers | Candlestick + volume (synced panes) with horizontal arrow markers at exact fill prices | Visually verify timing and price accuracy of trades |
| Real-time progress | Background jobs with DB-persisted progress (0-100%), 2s frontend polling | Know when long backtests will finish |
| 12 strategy templates | Pre-built classic strategies (MACD, RSI, BB, SuperTrend, etc.) with long+short signals | Quick-start with proven strategies, then customize |
| Configurable parameters | Order size, commission, slippage, timeframe, date range, magnifier toggle | Model different broker scenarios |
| Infrastructure as code | Fully parameterized Terraform for AWS EC2 + Route 53 | One-command cloud deployment to any AWS account |

## Quick Start (Local Development)

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### 1. Start the database

```bash
cd server/docker
docker compose up -d
cd ../..
```

TimescaleDB on port 5433, PgBouncer on port 5434.

### 2. Install Python dependencies

```bash
pip install -r server/requirements.txt
```

### 3. Ingest SPY data

```bash
python -m server.ingest
```

Loads ~1.4M 1-minute bars (SPY, 2008-2021) into TimescaleDB. Takes about 20 seconds.

### 4. Start the backend

```bash
uvicorn server.main:app --reload --port 8000
```

### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** — landing page at `/`, app at `/app`.

### How to Verify

1. Open `/app`, click **Load Template → MACD Crossover**
2. Set dates (e.g., 2019-01-01 to 2020-12-31), click **Run Backtest**
3. Watch the progress bar, then click **View** to see results
4. Check: Overview (16 metrics), Chart (OHLCV with trade markers), Trades (entry/exit table)

## Docker Deployment

```bash
docker compose -f docker-compose.prod.yml up -d --build
# Wait for DB (~20s), then ingest:
docker compose -f docker-compose.prod.yml exec app python -m server.ingest
# Open http://localhost
```

## Cloud Deployment (AWS via Terraform)

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
# Edit: key_pair_name, repo_url, domain_name, hosted_zone_name, admin_email
terraform init && terraform apply
# Output: https://your-domain.example.com
```

Requires: AWS account with a Route 53 hosted zone and an EC2 key pair. All resources are parameterized — see `terraform.tfvars.example`.

## Key Assumptions

- **SPY is the only symbol** — ~1.4M 1-minute bars from 2008-01-22 to 2021-05-06
- **Strategies are stateless** — no persistent bar-to-bar variables (`var`/`varip`)
- **Configurable execution costs** — commission (default 0.1%), slippage (default 0.05%), order size (default 100% equity)
- **Magnifier mode** gives realistic intra-bar fills; standard mode fills at bar close
- **No authentication** — single-user tool, not SaaS

## AI / Agent Workflow

- Built using **Cursor IDE** with **Claude** (agent mode)
- Used **Cursor Skills** for domain knowledge:
  - PineScript v6 language reference (syntax, indicators, strategy patterns)
  - vectorbt magnifier backtesting technique
  - TimescaleDB OHLCV schema design and ingestion
  - FastAPI backtest server patterns
  - Frontend charting with lightweight-charts
- Strategy builder migrated from an existing Vue 3 project using agent-guided refactoring
- **40+ incremental commits** reflecting the AI-driven development process
- Systematic verification: all 12 templates tested end-to-end (compiler → signals → trades)

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy, psycopg2, vectorbt, TimescaleDB, PgBouncer |
| **Frontend** | Vue 3, Vite, Tailwind CSS, lightweight-charts (Series Primitives), shepherd.js |
| **Infrastructure** | Docker, Terraform, AWS EC2, Route 53, nginx, Let's Encrypt |
| **Data** | SPY 1-minute OHLCV, 2008-2021 (~1.4M candles, ~120MB CSV via Git LFS) |

## Bonus Features

| Feature | Use Case |
|---------|----------|
| No-code visual strategy builder (40+ indicators) | Non-programmers can create strategies without writing code |
| Magnifier mode with sub-bar execution | Realistic fill prices on higher timeframes |
| Real-time progress tracking (0-100%) | Monitor long-running backtests |
| 12 pre-built strategy templates (long+short) | Quick-start backtesting without building from scratch |
| OHLCV candlestick chart with horizontal arrow markers at exact fill prices | Visually verify trade entry/exit accuracy |
| TradingView-style performance dashboard (16 metrics) | Comprehensive strategy evaluation |
| Dedicated result page with Overview/Chart/Trades tabs | Clear, focused result presentation |
| Configurable order sizing (% equity or fixed qty) | Test different position sizing strategies |
| Infrastructure as Code (Terraform, fully parameterized) | One-command deployment to any AWS account |
| Interactive guided tutorial (shepherd.js) | Reviewer can experience the full workflow in 3 minutes |
