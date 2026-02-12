"""
Strategy data model — TransformedStrategy, BacktestResult, InputParam types.

This module defines:
  - Input parameter types (mirrors PineScript input.int/float/bool/string)
  - TransformedStrategy: what the compiler outputs and the backtester consumes
  - TradeRecord / BacktestResult: structured output from a backtest run
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Input Parameter Types  (mirrors PineScript input.*)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class IntInput:
    """``input.int(defval, title, minval, maxval, step)``"""
    default: int
    title: str
    minval: Optional[int] = None
    maxval: Optional[int] = None
    step: int = 1


@dataclass
class FloatInput:
    """``input.float(defval, title, minval, maxval, step)``"""
    default: float
    title: str
    minval: Optional[float] = None
    maxval: Optional[float] = None
    step: float = 0.1


@dataclass
class BoolInput:
    """``input.bool(defval, title)``"""
    default: bool
    title: str


@dataclass
class StringInput:
    """``input.string(defval, title, options)``"""
    default: str
    title: str
    options: Optional[List[str]] = None


InputParam = Union[IntInput, FloatInput, BoolInput, StringInput]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TransformedStrategy — compiler output / backtester input
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class TransformedStrategy:
    """
    The compiled form of a PineScript strategy.

    Attributes:
        name:           Strategy display name (from ``strategy("name", ...)``)
        inputs:         Parameter definitions extracted from ``input.*`` declarations
        compute:        Vectorized compute function:
                        ``(df: DataFrame, params: dict) -> (long_entries, long_exits,
                         short_entries, short_exits)`` — four boolean pd.Series
        warmup:         Minimum bars before indicators stabilize
        pinescript:     Original PineScript source
        python_source:  Generated Python source (for debug)
        settings:       Strategy settings from ``strategy()`` declaration
                        (initial_capital, fees, slippage, etc.)
    """
    name: str
    inputs: Dict[str, InputParam]
    compute: Callable[
        [pd.DataFrame, Dict[str, Any]],
        Tuple[pd.Series, pd.Series, pd.Series, pd.Series],
    ]
    compute_fast: Optional[Callable[
        [np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]],
        Tuple[bool, bool, bool, bool],
    ]] = None
    warmup: int = 50
    pinescript: str = ""
    python_source: str = ""
    python_fast_source: str = ""
    settings: Dict[str, Any] = field(default_factory=dict)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BacktestResult — structured output
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class TradeRecord:
    """Single trade from a backtest — full detail."""
    trade_id: int
    position_id: int
    direction: str                # "Long" or "Short"
    status: str                   # "Closed" or "Open"
    entry_time: str               # ISO timestamp
    exit_time: Optional[str]      # None if still open
    entry_price: float
    exit_price: Optional[float]   # None if still open
    size: float
    entry_fees: float
    exit_fees: float
    pnl: float
    return_pct: float
    duration: str                 # human-readable duration


@dataclass
class OrderRecord:
    """Single order (buy or sell)."""
    order_id: int
    timestamp: str
    side: str                     # "Buy" or "Sell"
    price: float
    size: float
    fees: float


@dataclass
class DrawdownRecord:
    """Single drawdown period."""
    drawdown_id: int
    peak_time: str
    start_time: str
    valley_time: str
    end_time: Optional[str]       # None if still in drawdown
    peak_value: float
    valley_value: float
    end_value: Optional[float]
    drawdown_pct: float           # valley/peak - 1
    duration: str
    status: str                   # "Recovered" or "Active"


@dataclass
class BacktestResult:
    """Complete backtest output — maximum detail for frontend consumption."""

    # ── Metadata ──────────────────────────────────────────────
    strategy_name: str
    symbol: str
    exchange: str
    timeframe: str
    start_date: str
    end_date: str
    period: str                   # human-readable period (e.g. "60 days")
    mode: str                     # "standard" or "magnifier"
    params: Dict[str, Any]        # resolved strategy parameters

    # ── Performance ──────────────────────────────────────────
    initial_capital: float
    final_value: float
    total_return_pct: float       # Total Return [%]
    annualized_return_pct: Optional[float]  # CAGR (Annualized Return [%])
    annualized_volatility_pct: Optional[float]  # Annualized Volatility [%]
    benchmark_return_pct: float   # Buy & hold return [%]
    total_fees_paid: float
    max_gross_exposure_pct: float

    # ── Risk-adjusted ratios ─────────────────────────────────
    sharpe_ratio: Optional[float]
    calmar_ratio: Optional[float]
    sortino_ratio: Optional[float]
    omega_ratio: Optional[float]

    # ── Drawdown ─────────────────────────────────────────────
    max_drawdown_pct: float       # Max Drawdown [%]
    max_drawdown_duration: str    # human-readable

    # ── Trade summary ────────────────────────────────────────
    total_trades: int
    total_closed_trades: int
    total_open_trades: int
    open_trade_pnl: float
    win_rate_pct: float           # Win Rate [%]
    best_trade_pct: float
    worst_trade_pct: float
    avg_winning_trade_pct: float
    avg_losing_trade_pct: float
    avg_winning_duration: str
    avg_losing_duration: str
    profit_factor: Optional[float]  # None when gross loss is zero (= ∞)
    expectancy: float

    # ── Time series (for charting) ───────────────────────────
    equity_curve: List[Dict[str, Any]]    # [{timestamp, value}, ...]
    returns: List[Dict[str, Any]]         # [{timestamp, return}, ...] per-bar returns
    drawdown_curve: List[Dict[str, Any]]  # [{timestamp, drawdown_pct}, ...] underwater curve

    # ── OHLCV bars for candlestick chart (chart timeframe) ───
    ohlcv_bars: List[Dict[str, Any]]      # [{timestamp, open, high, low, close, volume}, ...]

    # ── Trade markers for chart overlay ──────────────────────
    trade_markers: List[Dict[str, Any]]   # [{timestamp, price, side, direction, trade_id, label, pnl}, ...]

    # ── Detail records ───────────────────────────────────────
    trades: List[TradeRecord]
    orders: List[OrderRecord]
    drawdowns: List[DrawdownRecord]

    # ── Raw portfolio (not serialized) ───────────────────────
    portfolio: Any = field(default=None, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict (excludes non-serializable portfolio)."""
        d = asdict(self)
        d.pop("portfolio", None)
        return d
