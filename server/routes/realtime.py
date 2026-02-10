"""
Realtime API session proxy.

Proxies the WebRTC SDP handshake to OpenAI so the API key stays server-side.
After session creation, all communication (voice audio + function calls) flows
directly between the browser and OpenAI over WebRTC.
"""

import json
import os
import httpx

from fastapi import APIRouter, HTTPException, Request, Response

from ..secrets import get_secret

router = APIRouter(prefix="/api/realtime", tags=["realtime"])

OPENAI_REALTIME_URL = "https://api.openai.com/v1/realtime/calls"

# Resolved lazily on first request so the module can import before
# Secrets Manager credentials or env vars are fully available.
_openai_api_key: str | None = None


def _get_openai_key() -> str:
    global _openai_api_key
    if _openai_api_key is None:
        _openai_api_key = get_secret("OPENAI_API_KEY")
    return _openai_api_key

# ── Tool definitions for the voice agent ──────────────────────
# These are sent in the session config so the AI model knows what
# functions it can call. The browser resolves them from local data.

TOOLS = [
    {
        "type": "function",
        "name": "get_performance_summary",
        "description": (
            "Get the backtest performance summary including key metrics: "
            "total return, annualized return, Sharpe ratio, Sortino ratio, "
            "max drawdown, win rate, profit factor, total trades, "
            "initial capital, final value, and fees paid."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "type": "function",
        "name": "get_trade_list",
        "description": (
            "Get the list of individual trades from the backtest. "
            "Each trade includes direction, entry/exit times, entry/exit prices, "
            "PnL, return percentage, and duration. "
            "Use limit and offset for pagination."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of trades to return. Default 20.",
                },
                "offset": {
                    "type": "integer",
                    "description": "Number of trades to skip. Default 0.",
                },
            },
            "required": [],
        },
    },
    {
        "type": "function",
        "name": "get_strategy_info",
        "description": (
            "Get strategy metadata: strategy name, symbol, exchange, timeframe, "
            "backtest mode, date range, and strategy parameter values."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]

SESSION_CONFIG = {
    "type": "realtime",
    "model": "gpt-4o-mini-realtime-preview",
    "audio": {
        "input": {
            "transcription": {"model": "gpt-4o-mini-transcribe"},
        },
        "output": {
            "voice": "ash",
        },
    },
    "instructions": (
        "You are a helpful trading strategy analyst. The user is viewing a "
        "backtest report and wants to discuss the results. Use the available "
        "tools to fetch performance metrics, trade details, and strategy info "
        "as needed. Be concise and insightful. Highlight key strengths and "
        "weaknesses of the strategy. When discussing numbers, round to 2 "
        "decimal places. Speak naturally as if you're a knowledgeable trading "
        "mentor having a conversation."
    ),
    "tools": TOOLS,
}


@router.post("/session")
async def create_realtime_session(request: Request):
    """
    Proxy the WebRTC SDP offer to OpenAI and return the SDP answer.

    The browser sends its SDP offer as the request body with
    Content-Type: application/sdp. We combine it with our session
    config and forward to OpenAI's /v1/realtime/calls endpoint.
    """
    api_key = _get_openai_key()
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not configured (check Secrets Manager or env var)",
        )

    # Read the raw SDP offer from the browser
    sdp_offer = (await request.body()).decode("utf-8")
    if not sdp_offer.strip():
        raise HTTPException(status_code=400, detail="Empty SDP offer")

    # Build the multipart form: sdp + session config
    # Must use files= (not data=) so httpx sends multipart/form-data
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                OPENAI_REALTIME_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                },
                files={
                    "sdp": (None, sdp_offer, "application/sdp"),
                    "session": (None, json.dumps(SESSION_CONFIG), "application/json"),
                },
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Timeout connecting to OpenAI Realtime API",
            )

    if resp.status_code != 200 and resp.status_code != 201:
        detail = resp.text[:500] if resp.text else f"HTTP {resp.status_code}"
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"OpenAI Realtime API error: {detail}",
        )

    # Return the SDP answer to the browser
    return Response(
        content=resp.text,
        media_type="application/sdp",
    )
