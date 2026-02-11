---
name: fastapi-backtest-server
description: REST API design for a backtest server using FastAPI — async job execution, PostgreSQL/TimescaleDB schema, static SPA serving, and scaling patterns. Use when building or modifying the HTTP layer that submits strategies, runs backtests asynchronously, and returns results to a frontend.
---

# FastAPI Backtest Server

Fullstack server: REST API for backtests + serves the frontend SPA.

For system-wide architecture context, see [architecture.md](../architecture.md).

## Architecture

```
Browser (SPA)  →  FastAPI  →  Background Worker  →  PostgreSQL + TimescaleDB
                    |                                   ├── ohlcv (hypertable)
                    |                                   └── backtests (jobs + results)
                    └── Static files (frontend/dist)
```

One process, one database, no message queue. Not SaaS — no multi-tenancy,
no billing.

## Backtests Table

```sql
CREATE TABLE backtests (
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
    status          TEXT            NOT NULL DEFAULT 'pending',
    error_message   TEXT,
    submitted_at    TIMESTAMPTZ     NOT NULL DEFAULT now(),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    -- Denormalized for fast listing (avoid parsing JSONB)
    total_return    NUMERIC(12,4),
    sharpe_ratio    NUMERIC(8,4),
    max_drawdown    NUMERIC(8,4),
    win_rate        NUMERIC(8,4),
    total_trades    INTEGER,
    profit_factor   NUMERIC(8,4),
    final_value     NUMERIC(20,2),
    -- Full result
    result_json     JSONB,
    CONSTRAINT valid_status CHECK (status IN ('pending','running','completed','failed')),
    CONSTRAINT valid_mode CHECK (mode IN ('standard','magnifier'))
);
CREATE INDEX idx_backtests_submitted ON backtests (submitted_at DESC);
CREATE INDEX idx_backtests_pending ON backtests (status) WHERE status IN ('pending','running');
```

UUID primary key (safe to expose in URLs). Summary stats denormalized so
list queries don't need to parse JSONB. Full result in `result_json` for
the detail view.

## Endpoints

### POST /api/backtests — Submit

```python
@router.post("/api/backtests", status_code=201)
async def submit(req: BacktestRequest, bg: BackgroundTasks, db=Depends(get_db)):
    # CRITICAL: compile in the handler, not the background task
    try:
        strategy = compile_pinescript(req.pinescript)
    except CompileError as e:
        raise HTTPException(400, detail=str(e))

    job = Backtest(strategy_name=strategy.name, pinescript=req.pinescript, ...)
    db.add(job); db.commit(); db.refresh(job)
    bg.add_task(execute_backtest_job, str(job.id))
    return {"id": str(job.id), "status": "pending"}
```

**Compile at submission, not in background.** If PineScript is invalid,
return 400 immediately — don't create a job that will fail.

### GET /api/backtests/{id} — Poll Status / Get Result

Return summary fields always. Return `result_json` only when
`status == "completed"`.

### GET /api/backtests — List

Return summary columns only. **Never include `result_json` in list
responses** — it's several MB per backtest.

### GET /api/symbols — Available Data

Query `SELECT symbol, exchange, min(ts), max(ts), count(*) FROM ohlcv GROUP BY ...`
so the frontend knows what data exists and what date ranges are valid.

## Background Job

```python
def execute_backtest_job(job_id: str):
    db = SessionLocal()  # Own session — request session is already closed
    try:
        job = db.query(Backtest).get(job_id)
        job.status = "running"; job.started_at = utcnow(); db.commit()

        strategy = compile_pinescript(job.pinescript)
        result = run_backtest(strategy, job.symbol, job.exchange, ...)

        job.status = "completed"
        job.total_return = result["total_return_pct"]
        job.sharpe_ratio = result["sharpe_ratio"]
        # ... other summary stats ...
        job.result_json = result
        job.completed_at = utcnow(); db.commit()
    except Exception as e:
        job.status = "failed"; job.error_message = str(e)[:1000]
        job.completed_at = utcnow(); db.commit()
    finally:
        db.close()
```

**Own session:** Background tasks outlive the HTTP request. Create a fresh
`SessionLocal()` — the request-scoped `Depends(get_db)` session is closed.

## Static File Serving

```python
app = FastAPI()
app.include_router(backtests_router)   # API routes FIRST
app.include_router(data_router)
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="spa")  # LAST
```

**Mount order matters.** `StaticFiles` at `/` is a catch-all. If mounted
before API routes, it intercepts `/api/*`. `html=True` returns `index.html`
for SPA client-side routing.

CORS middleware for frontend dev server:
```python
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], ...)
```

## Scaling Progression

**Single user / local:** `BackgroundTasks` (in-process thread pool) — simplest.

**Moderate:** Redis queue — `lpush` in API, `brpop` in a separate worker
process. Adds concurrency control and job persistence across restarts.

**Heavy:** Celery + Redis/RabbitMQ — horizontal worker scaling, retries,
rate limiting.

**Real-time progress (optional):** SSE instead of polling:
```python
@router.get("/api/backtests/{id}/events")
async def events(id: str):
    async def gen():
        while True:
            job = get_status(id)
            yield f"data: {json.dumps({'status': job.status})}\n\n"
            if job.status in ("completed","failed"): break
            await asyncio.sleep(1)
    return StreamingResponse(gen(), media_type="text/event-stream")
```

## Pitfalls

| Pitfall | Prevention |
|---------|-----------|
| Compile in background task | Compile in POST handler; 400 on failure |
| Static mount before API routes | Mount `StaticFiles` after `include_router` |
| Shared request session in background | Create `SessionLocal()` in the task |
| `result_json` in list endpoint | Only return denormalized summary columns |
| Sync backtest in request handler | Always `BackgroundTasks` or task queue |
| No concurrent backtest limit | Use task queue with worker pool limit |
