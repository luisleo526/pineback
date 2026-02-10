"""
Backtest API endpoints.

POST /api/backtests      — Submit a new backtest (compile in handler, 400 on error)
GET  /api/backtests      — List all backtests (summary only, no result_json)
GET  /api/backtests/{id} — Poll status / get result (result_json only when completed)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import SessionLocal, get_db
from ..models import Backtest

router = APIRouter(prefix="/api/backtests", tags=["backtests"])


# ── Request / Response models ────────────────────────────────────

class BacktestRequest(BaseModel):
    pinescript: str
    timeframe: str = "1h"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    initial_capital: float = 10000
    params: Dict[str, Any] = {}
    mode: str = "magnifier"
    symbol: str = "SPY"
    exchange: str = "NYSE"


class BacktestSubmitResponse(BaseModel):
    id: str
    status: str


# ── Background job ───────────────────────────────────────────────

def execute_backtest_job(job_id: str):
    """Run backtest in background thread. Own session — request session is closed."""
    db = SessionLocal()
    try:
        job = db.query(Backtest).filter(Backtest.id == job_id).first()
        if not job:
            return

        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        job.progress = 0
        job.progress_message = "Starting"
        db.commit()

        def on_progress(pct: int, message: str):
            """Update progress in DB."""
            job.progress = pct
            job.progress_message = message
            db.commit()

        # Compile PineScript
        on_progress(5, "Compiling strategy")
        from ..pine import transform_pinescript
        strategy = transform_pinescript(job.pinescript)

        # Create data source and backtester
        from ..data import TimescaleSource
        from ..backtester import Backtester

        source = TimescaleSource()
        backtester = Backtester(data_source=source)

        # Merge user param overrides
        param_overrides = job.params or {}

        result = backtester.run(
            strategy=strategy,
            symbol=job.symbol,
            exchange=job.exchange,
            start=str(job.start_date) if job.start_date else None,
            end=str(job.end_date) if job.end_date else None,
            timeframe=job.timeframe,
            magnify=(job.mode == "magnifier"),
            initial_capital=float(job.initial_capital),
            on_progress=on_progress,
            **param_overrides,
        )

        # Write result
        job.status = "completed"
        job.progress = 100
        job.progress_message = "Done"
        job.completed_at = datetime.now(timezone.utc)

        # Denormalized summary stats
        job.total_return = result.total_return_pct
        job.sharpe_ratio = result.sharpe_ratio
        job.max_drawdown = result.max_drawdown_pct
        job.win_rate = result.win_rate_pct
        job.total_trades = result.total_trades
        job.profit_factor = result.profit_factor
        job.final_value = result.final_value
        job.strategy_name = strategy.name

        # Full result
        job.result_json = result.to_dict()
        db.commit()

    except Exception as e:
        import traceback
        traceback.print_exc()
        job.status = "failed"
        job.error_message = str(e)[:1000]
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()


# ── Endpoints ────────────────────────────────────────────────────

@router.post("", status_code=201, response_model=BacktestSubmitResponse)
async def submit_backtest(
    req: BacktestRequest,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Submit a new backtest. Compiles PineScript in-handler (400 on error)."""
    # Compile in handler — fail fast on syntax errors
    try:
        from ..pine import transform_pinescript
        strategy = transform_pinescript(req.pinescript)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PineScript compile error: {e}")

    # Create job row
    job = Backtest(
        strategy_name=strategy.name,
        pinescript=req.pinescript,
        symbol=req.symbol,
        exchange=req.exchange,
        timeframe=req.timeframe,
        start_date=req.start_date,
        end_date=req.end_date,
        initial_capital=req.initial_capital,
        params=req.params,
        mode=req.mode,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Dispatch background task
    bg.add_task(execute_backtest_job, str(job.id))

    return BacktestSubmitResponse(id=str(job.id), status="pending")


@router.get("/{backtest_id}")
async def get_backtest(backtest_id: str, db: Session = Depends(get_db)):
    """Poll backtest status or get result."""
    job = db.query(Backtest).filter(Backtest.id == backtest_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return job.to_detail_dict()


@router.get("")
async def list_backtests(db: Session = Depends(get_db)):
    """List all backtests (summary only, no result_json)."""
    jobs = (
        db.query(Backtest)
        .order_by(Backtest.submitted_at.desc())
        .limit(100)
        .all()
    )
    return [j.to_summary_dict() for j in jobs]
