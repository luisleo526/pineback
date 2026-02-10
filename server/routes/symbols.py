"""
Symbols, strategies, and compile endpoints.

GET  /api/symbols    — Available symbols with date ranges
GET  /api/strategies — Pre-built strategy templates (condition builder JSON)
POST /api/compile    — Compile PineScript, return inputs for parameter discovery
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from ..db import SessionLocal

router = APIRouter(prefix="/api", tags=["symbols"])

# Path to strategy template JSON files
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


# ── Request / Response models ────────────────────────────────────

class CompileRequest(BaseModel):
    pinescript: str


class InputInfo(BaseModel):
    type: str
    default: Any
    title: str
    minval: Any = None
    maxval: Any = None


class CompileResponse(BaseModel):
    name: str
    inputs: Dict[str, InputInfo]
    python_source: str = ""


class SymbolInfo(BaseModel):
    symbol: str
    exchange: str
    market_type: str
    min_ts: str
    max_ts: str
    count: int


class StrategyTemplate(BaseModel):
    filename: str
    name: str
    strategy_data: Dict[str, Any]


# ── Endpoints ────────────────────────────────────────────────────

@router.get("/symbols", response_model=List[SymbolInfo])
async def get_symbols():
    """Return available symbols with date ranges from the ohlcv table."""
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT symbol, exchange, market_type,
                   MIN(ts)::text AS min_ts,
                   MAX(ts)::text AS max_ts,
                   COUNT(*) AS count
            FROM ohlcv
            GROUP BY symbol, exchange, market_type
            ORDER BY symbol
        """))
        rows = result.fetchall()
        return [
            SymbolInfo(
                symbol=r[0], exchange=r[1], market_type=r[2],
                min_ts=r[3], max_ts=r[4], count=r[5],
            )
            for r in rows
        ]
    finally:
        db.close()


@router.get("/strategies", response_model=List[StrategyTemplate])
async def get_strategies():
    """Return pre-built strategy templates as condition builder JSON."""
    templates: List[StrategyTemplate] = []

    if not os.path.isdir(TEMPLATES_DIR):
        return templates

    for filename in sorted(os.listdir(TEMPLATES_DIR)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(TEMPLATES_DIR, filename)
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            templates.append(StrategyTemplate(
                filename=filename,
                name=data.get("name", filename.replace(".json", "")),
                strategy_data=data,
            ))
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: failed to load template {filename}: {e}")

    return templates


@router.post("/compile", response_model=CompileResponse)
async def compile_pinescript(req: CompileRequest):
    """Compile PineScript and return discovered input parameters."""
    try:
        from ..pine import transform_pinescript
        from ..strategy import IntInput, FloatInput, BoolInput, StringInput

        strategy = transform_pinescript(req.pinescript)

        inputs: Dict[str, InputInfo] = {}
        for key, inp in strategy.inputs.items():
            if isinstance(inp, IntInput):
                inputs[key] = InputInfo(
                    type="int", default=inp.default, title=inp.title,
                    minval=inp.minval, maxval=inp.maxval,
                )
            elif isinstance(inp, FloatInput):
                inputs[key] = InputInfo(
                    type="float", default=inp.default, title=inp.title,
                    minval=inp.minval, maxval=inp.maxval,
                )
            elif isinstance(inp, BoolInput):
                inputs[key] = InputInfo(
                    type="bool", default=inp.default, title=inp.title,
                )
            elif isinstance(inp, StringInput):
                inputs[key] = InputInfo(
                    type="string", default=inp.default, title=inp.title,
                )

        return CompileResponse(
            name=strategy.name,
            inputs=inputs,
            python_source=strategy.python_source,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Compile error: {e}")
