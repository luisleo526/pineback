"""
OHLCV data loading — DataSource protocol + TimescaleSource implementation.

The ``DataSource`` protocol defines the interface for OHLCV providers.
``TimescaleSource`` loads from TimescaleDB via psycopg2 (through PgBouncer).
"""

from __future__ import annotations

import os
from typing import Dict, Optional, Protocol

import pandas as pd


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Constants
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESAMPLE_MAP: Dict[str, str] = {
    "1m": "1min", "3m": "3min", "5m": "5min", "15m": "15min",
    "30m": "30min", "1h": "1h", "4h": "4h", "1d": "1D",
}

_TF_DELTA: Dict[str, pd.Timedelta] = {
    "1m": pd.Timedelta(minutes=1), "3m": pd.Timedelta(minutes=3),
    "5m": pd.Timedelta(minutes=5), "15m": pd.Timedelta(minutes=15),
    "30m": pd.Timedelta(minutes=30), "1h": pd.Timedelta(hours=1),
    "4h": pd.Timedelta(hours=4), "1d": pd.Timedelta(days=1),
}

# Minutes per timeframe (for magnifier resolution computation)
_TF_MINUTES: Dict[str, int] = {
    "1m": 1, "3m": 3, "5m": 5, "15m": 15,
    "30m": 30, "1h": 60, "4h": 240, "1d": 1440,
}

# Valid magnifier resolutions, ascending
_VALID_RESOLUTIONS = [1, 3, 5, 15, 30, 60, 240]  # minutes


def compute_magnifier_resolution(
    timeframe: str,
    target_ticks: int = 10,
) -> str:
    """
    Pick the best magnifier resolution for a given chart timeframe.

    The goal is to have roughly *target_ticks* sub-bars per chart bar.
    """
    chart_min = _TF_MINUTES.get(timeframe)
    if chart_min is None or chart_min <= 1:
        return "1m"

    max_ticks = int(target_ticks * 1.6)
    best_res = 1
    best_dist = float("inf")

    for res_min in _VALID_RESOLUTIONS:
        if res_min >= chart_min:
            continue
        if chart_min % res_min != 0:
            continue
        ticks = chart_min // res_min
        if ticks > max_ticks:
            continue
        dist = abs(ticks - target_ticks)
        if dist < best_dist:
            best_dist = dist
            best_res = res_min

    return _minutes_to_tf(best_res)


def _minutes_to_tf(minutes: int) -> str:
    for tf, m in _TF_MINUTES.items():
        if m == minutes:
            return tf
    return f"{minutes}m"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DataSource protocol
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class DataSource(Protocol):
    """Interface for OHLCV data providers."""

    def load_1m(
        self,
        symbol: str,
        exchange: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Load 1-minute OHLCV data.

        Returns a DataFrame with a UTC DatetimeIndex
        and columns: ``open``, ``high``, ``low``, ``close``, ``volume``.
        """
        ...


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TimescaleSource — loads from TimescaleDB via PgBouncer
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TimescaleSource:
    """
    Loads OHLCV from TimescaleDB via psycopg2.

    Uses the PgBouncer connection string (port 5434 locally).
    """

    def __init__(self, dsn: Optional[str] = None):
        self.dsn = dsn or os.getenv(
            "DATABASE_URL",
            "postgresql://backtest:backtest@localhost:5434/backtest",
        )

    def load_1m(
        self,
        symbol: str = "SPY",
        exchange: str = "NYSE",
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> pd.DataFrame:
        """Load 1m OHLCV from TimescaleDB."""
        from sqlalchemy import create_engine, text

        query = """
            SELECT ts, open, high, low, close, volume
            FROM ohlcv
            WHERE symbol = :symbol AND exchange = :exchange
        """
        bind_params = {"symbol": symbol, "exchange": exchange}

        if start:
            query += " AND ts >= :start"
            bind_params["start"] = start
        if end:
            query += " AND ts <= :end"
            bind_params["end"] = end

        query += " ORDER BY ts"

        engine = create_engine(self.dsn)
        with engine.connect() as conn:
            df = pd.read_sql_query(
                text(query), conn, params=bind_params,
                index_col="ts", parse_dates=["ts"],
            )

        if df.empty:
            raise ValueError(
                f"No data in [{start or 'earliest'} .. {end or 'latest'}] "
                f"for {symbol} on {exchange}"
            )

        # Ensure UTC timezone
        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC")
        else:
            df.index = df.index.tz_convert("UTC")

        df.index.name = "timestamp"
        return df


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Resampling
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def resample_ohlcv(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """Resample 1m OHLCV to a higher timeframe."""
    if timeframe == "1m":
        return df
    rule = RESAMPLE_MAP.get(timeframe)
    if rule is None:
        raise ValueError(
            f"Unknown timeframe '{timeframe}'.  Use: {', '.join(RESAMPLE_MAP)}"
        )
    return df.resample(rule).agg({
        "open": "first", "high": "max", "low": "min",
        "close": "last", "volume": "sum",
    }).dropna()
