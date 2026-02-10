# US Stock Backtesting System

A full-stack backtesting platform with a no-code visual strategy builder, PineScript v6 compiler, and TradingView-style results.

**Live demo**: [interview.4pass.io](https://interview.4pass.io)

---

## Architecture

```
Browser (Vue 3 SPA)
  │
  ├─ / .................. Landing Page (project documentation)
  └─ /app ............... Strategy Builder + Backtest Dashboard
        │
        │ POST /api/backtests ─── compile PineScript ─── BackgroundTask
        │ GET  /api/backtests/{id} ─── poll progress / get result
        │
  nginx (SSL) ──► FastAPI (uvicorn)
                    │
                    ├── PineScript Compiler (tokenizer → parser → AST → codegen)
                    ├── vectorbt Portfolio.from_signals() (standard + magnifier)
                    └── PostgreSQL 16 + TimescaleDB
                          ├── ohlcv (hypertable, 1m bars)
                          └── backtests (jobs + results)
                          via PgBouncer (connection pooling)
```

## Features

| Feature | Description | Use Case |
|---------|-------------|----------|
| No-code strategy builder | Visual condition builder with 40+ indicators, AND/OR logic, custom variables, math expressions | Non-programmers can build and test trading strategies |
| PineScript v6 compiler | Tokenizer → Parser → AST → Python codegen, compiles to vectorized functions | Execute TradingView-compatible strategies programmatically |
| Magnifier mode | Iterates sub-bars for realistic intra-bar fill prices on higher timeframes | Avoid unrealistic bar-close fills on 1h/4h/1d backtests |
| OHLCV chart + markers | Candlestick + volume (synced panes) with trade entry/exit markers | Visually verify timing and price accuracy of trades |
| Real-time progress | Background jobs with DB-persisted progress (0-100%), 2s frontend polling | Know when long backtests will finish |
| 12 strategy templates | Pre-built classic strategies (MACD, RSI, BB, SuperTrend, etc.) | Quick-start with proven strategies, then customize |
| Interactive tutorial | 12-step guided tour with forced actions (shepherd.js) | Reviewers can experience the full workflow in 3 minutes |
| Infrastructure as code | Fully parameterized Terraform for AWS EC2 + Route 53 | One-command cloud deployment to any AWS account |

## Metrics

CAGR (annualized return), annualized volatility, Sharpe ratio, Sortino ratio, Calmar ratio, max drawdown (% and duration), profit factor, win rate, expectancy, total trades, best/worst trade, avg winning/losing trade, total fees paid.

## Quick Start (Local Development)

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### 1. Start the database

```bash
cd server/docker
docker compose up -d
```

This starts TimescaleDB (port 5433) and PgBouncer (port 5434).

### 2. Install Python dependencies

```bash
pip install -r server/requirements.txt
```

### 3. Ingest SPY data

```bash
python -m server.ingest
```

Loads ~2M 1-minute bars (SPY, 2008-2021) into TimescaleDB. Takes about 1 minute.

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

Open http://localhost:5173 — the landing page is at `/`, the app is at `/app`.

## Docker Deployment (Local)

```bash
docker compose -f docker-compose.prod.yml up -d --build

# Wait for DB to be ready (~20s), then ingest data:
docker compose -f docker-compose.prod.yml exec app python -m server.ingest

# Open http://localhost
```

## Cloud Deployment (AWS via Terraform)

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
# Edit: key_pair_name, repo_url, domain_name, hosted_zone_name, admin_email

terraform init
terraform plan
terraform apply

# Output: https://your-domain.example.com
# Tear down: terraform destroy
```

Requirements: AWS account with a Route 53 hosted zone and an EC2 key pair.

## Key Assumptions

- **SPY is the only symbol.** ~2M 1-minute bars from 2008-01-22 to 2021, stored in TimescaleDB.
- **Strategies are stateless.** No persistent bar-to-bar variables (no `var`/`varip`). All 12 templates follow this pattern.
- **Configurable fills.** Commission (default 0.1%), slippage (default 0.05%) are user-adjustable per backtest.
- **Magnifier mode** gives realistic intra-bar fills on higher timeframes. Standard mode fills at bar close (fast but less realistic).
- **No authentication.** This is a single-user tool, not a SaaS platform.

## AI / Agent Workflow

- Built using **Cursor IDE** with **Claude** (agent mode)
- Used **Cursor Skills** for domain knowledge:
  - PineScript v6 language reference
  - vectorbt magnifier technique
  - TimescaleDB OHLCV schema design
  - FastAPI backtest server patterns
  - Frontend charting with lightweight-charts
- Strategy builder migrated from an existing Vue 3 project using agent-guided refactoring
- **24 incremental commits** reflecting the AI-driven development process

## Tech Stack

**Backend:** Python 3.11, FastAPI, SQLAlchemy, psycopg2, vectorbt, TimescaleDB, PgBouncer

**Frontend:** Vue 3, Vite, Tailwind CSS, lightweight-charts, shepherd.js, Font Awesome

**Infrastructure:** Docker, Terraform, AWS EC2, Route 53, nginx, Let's Encrypt

**Data:** SPY 1-minute OHLCV bars, 2008-2021 (~2M candles, ~120MB CSV)
