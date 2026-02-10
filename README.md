# PineBack

A full-stack backtesting platform that speaks **PineScript v6** — the same language used by TradingView's global algo-trading community.

Build strategies visually, generate TradingView-compatible PineScript, and backtest locally with realistic execution. Every generated script works both in PineBack _and_ on TradingView — **one strategy, two platforms**.

> **Live demo**: [interview.4pass.io](https://interview.4pass.io)

---

## Why PineScript?

TradingView has the **largest global community** of retail algo-traders, all writing strategies in PineScript. By adopting PineScript v6 as the strategy language, PineBack can:

- **Serve the existing community** — any PineScript strategy can be backtested here with custom data and execution models
- **Export to TradingView** — strategies built in PineBack's visual builder generate valid PineScript that runs on TradingView directly
- **Leverage a familiar syntax** — no new language to learn for millions of TradingView users

## Metrics

Every backtest produces a comprehensive set of performance metrics:

- **Net Profit** — final value minus initial capital
- **CAGR / Annualized Return** — compound annual growth rate
- **Annualized Volatility** — standard deviation of returns, annualized
- **Max Drawdown** — largest peak-to-trough decline (% and duration)
- **Sharpe Ratio** — risk-adjusted return (excess return / volatility)
- **Sortino Ratio** — downside-risk-adjusted return
- **Profit Factor** — gross profit / gross loss
- **Expectancy** — average profit per trade
- **Total Trades, Win Rate, Best/Worst Trade, Avg Win/Loss, Avg Duration**

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

| Feature | Description |
|---------|-------------|
| No-code strategy builder | Visual condition builder with 40+ indicators, AND/OR logic, custom variables, math expressions |
| PineScript v6 compiler | Tokenizer → Parser → AST → Python codegen; generated scripts also run on TradingView |
| TradingView-compatible output | Every generated PineScript can be pasted into TradingView and executed directly |
| Magnifier mode | Iterates sub-bars for realistic intra-bar fill prices on higher timeframes |
| OHLCV chart + markers | Candlestick + volume (synced panes) with horizontal arrow markers at exact fill prices |
| Real-time progress | Background jobs with DB-persisted progress (0-100%), 2s frontend polling |
| 12 strategy templates | Pre-built classic strategies (MACD, RSI, BB, SuperTrend, etc.) with long+short signals |
| Configurable parameters | Order size, commission, slippage, timeframe, date range, magnifier toggle |
| Infrastructure as code | Fully parameterized Terraform for AWS EC2 + Route 53 |
| Interactive guided tutorial | Step-by-step walkthrough for first-time users (shepherd.js) |

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
5. Copy the generated PineScript and paste it into TradingView — it will run there too

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

- **PineScript v6 as the strategy language** — TradingView has the largest global algo-trading community; generated scripts are cross-platform (PineBack + TradingView)
- **SPY is the only symbol** — ~1.4M 1-minute bars from 2008-01-22 to 2021-05-06, sourced from [Kaggle](https://www.kaggle.com/datasets/rockinbrock/spy-1-minute-data)
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
| **Data** | [SPY 1-minute OHLCV from Kaggle](https://www.kaggle.com/datasets/rockinbrock/spy-1-minute-data), 2008-2021 (~1.4M candles, ~120MB CSV via Git LFS) |
