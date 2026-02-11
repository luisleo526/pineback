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

Every backtest produces 16 performance metrics (4×4 grid):

| Row | Metrics |
|-----|---------|
| 1 | Net Profit, CAGR, Annualized Volatility, Max Drawdown |
| 2 | Sharpe Ratio, Sortino Ratio, Profit Factor, Expectancy |
| 3 | Total Trades, Win Rate, Best Trade, Worst Trade |
| 4 | Avg Winning Trade, Avg Losing Trade, Avg Win Duration, Avg Loss Duration |

## Architecture

```
Browser (Vue 3 SPA)
  ├─ /           Landing page (project documentation)
  ├─ /app        Strategy Builder + Backtest Dashboard
  ├─ /result/:id Full-page backtest results + Voice AI Agent
  │
  │ POST /api/backtests ── compile PineScript ── BackgroundTask
  │ GET  /api/backtests/{id} ── poll progress (0-100%) / get result
  │ POST /api/voice/session ── SDP proxy for OpenAI Realtime WebRTC
  │
FastAPI (uvicorn)
  ├── PineScript v6 Compiler (tokenizer → parser → AST → codegen)
  ├── 37 Technical Indicators (ta.py)
  ├── vectorbt Portfolio.from_signals() (standard + magnifier mode)
  ├── Voice session endpoint (proxies SDP to OpenAI, keeps API key server-side)
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
| Voice AI Agent | Discuss backtest results with an AI analyst via voice (OpenAI Realtime API over WebRTC). Function calls resolved in-browser from local report data — backend is not in the hot path. |
| Interactive guided tutorial | Step-by-step walkthrough for first-time users (shepherd.js) |
| Infrastructure as code | Fully parameterized Terraform for AWS EC2 + Route 53 |

## Quick Start (Local Development)

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- **`OPENAI_API_KEY`** (optional) — required only for the Voice AI Agent feature. Set it as an environment variable before starting the backend:
  ```bash
  export OPENAI_API_KEY="sk-..."
  ```

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
# Without Voice AI:
uvicorn server.main:app --reload --port 8000

# With Voice AI:
OPENAI_API_KEY="sk-..." uvicorn server.main:app --reload --port 8000
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
6. Click the microphone icon on the result page to talk to the AI analyst about your results (requires `OPENAI_API_KEY`)

## Docker Deployment

```bash
docker compose -f docker-compose.prod.yml up -d --build
# Wait for DB (~20s), then ingest:
docker compose -f docker-compose.prod.yml exec app python -m server.ingest
# Open http://localhost
```

To enable Voice AI in Docker, set `OPENAI_API_KEY` in the environment or `.env` file.

## Cloud Deployment (AWS via Terraform)

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars:
#   key_pair_name  = "my-key-pair"
#   repo_url       = "https://github.com/you/pineback.git"
#   domain_name    = "backtest.example.com"
#   hosted_zone_name = "example.com"
#   admin_email    = "you@example.com"
#   openai_api_key = "sk-..."          # for Voice AI agent
terraform init && terraform apply
```

**What happens automatically:**

1. Provisions EC2 (t3.large), Elastic IP, Route 53 DNS, Security Group
2. Creates a Secrets Manager secret with the OpenAI API key
3. Creates an IAM role + instance profile so the app can read secrets
4. Bootstrap script (`user_data.sh.tpl`) runs on first boot:
   - Installs Docker, Docker Compose, git-lfs
   - Clones the repo and pulls LFS data (SPY CSV)
   - Builds all containers (`docker compose -f docker-compose.prod.yml up --build`)
   - Polls DB readiness, then ingests ~1.4M SPY bars
   - Obtains an SSL certificate via Let's Encrypt (certbot)
   - Writes the SSL nginx config and restarts nginx
5. App is live at `https://your-domain.example.com` within ~5 minutes

**Requirements:** AWS account with a Route 53 hosted zone and an EC2 key pair. All resources are parameterized — see `terraform.tfvars.example`.

**Voice AI agent:** Requires the `openai_api_key` variable. The key is stored in AWS Secrets Manager and loaded at runtime via the EC2 instance profile — no secrets in env vars or Docker images.

## Key Assumptions

- **PineScript v6 as the strategy language** — TradingView has the largest global algo-trading community; generated scripts are cross-platform (PineBack + TradingView)
- **SPY is the only symbol** — ~1.4M 1-minute bars from 2008-01-22 to 2021-05-06, sourced from [Kaggle](https://www.kaggle.com/datasets/rockinbrock/spy-1-minute-data)
- **Strategies are stateless** — no persistent bar-to-bar variables (`var`/`varip`)
- **Configurable execution costs** — commission (default 0.1%), slippage (default 0.05%), order size (default 100% equity)
- **Magnifier mode** gives realistic intra-bar fills; standard mode fills at bar close
- **Voice AI requires `OPENAI_API_KEY`** — the Voice AI Agent on the result page uses OpenAI's Realtime API (gpt-4o-mini-realtime-preview). Without the key, all other features work normally.
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
- **110+ incremental commits** reflecting the AI-driven development process
- Systematic verification: all 12 templates tested end-to-end (compiler → signals → trades)

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy, psycopg2, vectorbt, TimescaleDB, PgBouncer |
| **Frontend** | Vue 3, Vite, Tailwind CSS, lightweight-charts (Series Primitives), shepherd.js |
| **Voice AI** | OpenAI Realtime API (gpt-4o-mini-realtime-preview), WebRTC, in-browser function calling |
| **Infrastructure** | Docker, Terraform, AWS EC2, Route 53, nginx, Let's Encrypt, Secrets Manager |
| **Data** | [SPY 1-minute OHLCV from Kaggle](https://www.kaggle.com/datasets/rockinbrock/spy-1-minute-data), 2008-2021 (~1.4M candles, ~120MB CSV via Git LFS) |

## Bonus Features

| Feature | Description | Use Case |
|---------|-------------|----------|
| Visual Strategy Builder | Drag-and-drop interface with 40+ indicators | Non-technical users can create strategies |
| PineScript v6 Compiler | Full 4-stage compiler: tokenize → parse → AST → codegen | Import/export TradingView strategies |
| Magnifier Mode | Resample HT signals to 1-min bars for intra-bar execution | Realistic fill simulation for limit/stop orders |
| OHLCV Candlestick Chart | Interactive chart with horizontal arrow markers at exact fill prices | Visual trade inspection with market context |
| 12 Strategy Templates | Pre-built strategies covering major TA categories | Instant backtesting without building from scratch |
| Drawdown Analysis | Underwater chart with duration tracking | Risk assessment and worst-case analysis |
| Job Progress Tracking | Real-time status polling (0-100%) | Monitor long-running backtests |
| Voice AI Agent | Voice conversation via OpenAI Realtime WebRTC; function calls resolved in-browser | Hands-free strategy analysis and performance Q&A |
| IaC Deployment | Terraform + Docker Compose, fully parameterized | One-command deployment to any AWS account |
| Interactive Tutorial | Guided tour with forced-action steps (shepherd.js) | Reviewer can experience the full workflow in 3 minutes |
