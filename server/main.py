"""
FastAPI application entry point.

Serves the REST API and the frontend SPA (static files).

Usage:
    uvicorn server.main:app --reload --port 8000
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes.backtests import router as backtests_router
from .routes.symbols import router as symbols_router

app = FastAPI(
    title="PineBack",
    description="PineScript v6 backtesting platform with visual strategy builder and vectorbt",
    version="1.0.0",
)

# CORS for frontend dev server (Vite on port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes (must be registered BEFORE static file mount)
app.include_router(backtests_router)
app.include_router(symbols_router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


# Serve frontend SPA (static files)
# Mount AFTER API routes so /api/* paths are handled first.
FRONTEND_DIST = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "frontend", "dist",
)

if os.path.isdir(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="spa")
