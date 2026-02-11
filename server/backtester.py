"""
Backtester — runs a ``TransformedStrategy`` against OHLCV data.

Two execution modes:

  **Standard**
    Signals computed on bar-close of the target timeframe.

  **Windowed-recompute magnifier**
    For each higher-TF bar, iterate sub-bars at dynamic resolution,
    progressively build a forming bar, run ``compute()`` on a sliding
    window, and record signals at the exact sub-bar timestamp.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

import numpy as np
import pandas as pd

from .data import (
    DataSource, RESAMPLE_MAP, _TF_DELTA,
    compute_magnifier_resolution, resample_ohlcv,
)
from .strategy import (
    BacktestResult, DrawdownRecord, OrderRecord, TradeRecord,
    TransformedStrategy,
)

# Type alias for progress callback
ProgressCallback = Optional[Callable[[int, str], None]]

# Maximum OHLCV bars to include in result (for frontend charting)
MAX_CHART_BARS = 5000


def _safe_float(val: Any) -> Optional[float]:
    """Safely convert a stats value to float, returning None on failure."""
    if val is None:
        return None
    try:
        f = float(val)
        if np.isnan(f) or np.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


def _noop_progress(pct: int, msg: str) -> None:
    """Default no-op progress callback."""
    pass


class Backtester:
    """
    Run a ``TransformedStrategy`` against OHLCV data from any DataSource.

    Parameters
    ----------
    data_source : DataSource
        Must implement the ``load_1m()`` method.
    """

    def __init__(self, data_source: DataSource):
        self.data_source: DataSource = data_source

    # ── public API ────────────────────────────────────────────

    def run(
        self,
        strategy: TransformedStrategy,
        symbol: str = "SPY",
        exchange: str = "NYSE",
        start: Optional[str] = None,
        end: Optional[str] = None,
        timeframe: str = "1h",
        magnify: bool = True,
        initial_capital: Optional[float] = None,
        fees: Optional[float] = None,
        slippage: Optional[float] = None,
        order_size: float = 100,
        order_type: str = "percent",
        on_progress: ProgressCallback = None,
        **param_overrides: Any,
    ) -> BacktestResult:
        """
        Run the backtest end-to-end.

        Parameters
        ----------
        order_size : float
            Position size per trade. Meaning depends on order_type.
        order_type : str
            'percent' = % of equity (100 = all-in), 'fixed' = fixed quantity.
        on_progress : callable, optional
            ``(pct: int, message: str) -> None`` called at each phase.
        """
        progress = on_progress or _noop_progress

        # Resolve parameters
        params = self._resolve_params(strategy, param_overrides)
        capital = initial_capital or strategy.settings.get("initial_capital", 10_000)
        _fees = fees if fees is not None else strategy.settings.get("commission_value", 0.001)
        _slippage = slippage if slippage is not None else strategy.settings.get("slippage", 0.0005)

        # Order sizing for vectorbt
        # Note: SizeType.Percent does not support position reversal (long->short).
        # Use np.inf with "amount" for all-in sizing, which is equivalent but
        # compatible with strategies that have both long and short signals.
        if order_type == "percent" and order_size >= 100:
            _size = np.inf        # all available cash
            _size_type = "amount"
        elif order_type == "percent":
            _size = order_size / 100.0
            _size_type = "percent"
        else:
            _size = order_size
            _size_type = "amount"

        mode = "magnifier" if (magnify and timeframe != "1m") else "standard"

        # Load data
        progress(10, "Loading 1m OHLCV data")
        df_1m = self.data_source.load_1m(symbol, exchange, start, end)

        # Resample to chart timeframe
        progress(15, f"Resampling to {timeframe}")
        df_tf = resample_ohlcv(df_1m, timeframe)

        if mode == "magnifier":
            progress(18, "Preparing magnifier resolution")
            pf = self._run_magnified(
                df_1m, df_tf, timeframe, strategy, params,
                capital, _fees, _slippage, _size, _size_type, progress,
            )
        else:
            progress(20, "Computing signals")
            pf = self._run_standard(
                df_tf, timeframe, strategy, params,
                capital, _fees, _slippage, _size, _size_type, progress,
            )

        # Extract result
        progress(90, "Building portfolio")
        progress(95, "Extracting results")
        result = self._extract_result(
            pf, df_tf, strategy, symbol, exchange, timeframe,
            start or str(df_1m.index[0].date()),
            end or str(df_1m.index[-1].date()),
            mode, params, capital,
        )
        progress(100, "Done")
        return result

    # ── parameter resolution ─────────────────────────────────

    @staticmethod
    def _resolve_params(strategy: TransformedStrategy,
                        overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user overrides with strategy defaults, validate bounds."""
        params: Dict[str, Any] = {}
        for key, inp in strategy.inputs.items():
            val = overrides.get(key, inp.default)
            from .strategy import IntInput, FloatInput
            if isinstance(inp, (IntInput, FloatInput)):
                if inp.minval is not None and val < inp.minval:
                    raise ValueError(f"{key}={val} below minval={inp.minval}")
                if inp.maxval is not None and val > inp.maxval:
                    raise ValueError(f"{key}={val} above maxval={inp.maxval}")
            params[key] = val
        return params

    # ── standard mode ────────────────────────────────────────

    def _run_standard(self, df_tf, timeframe, strategy, params,
                      capital, fees, slippage, size, size_type, progress):
        long_e, long_x, short_e, short_x = strategy.compute(df_tf, params)
        progress(40, "Signals computed")

        import vectorbt as vbt
        progress(50, "Building portfolio")
        return vbt.Portfolio.from_signals(
            close=df_tf["close"],
            entries=long_e,
            exits=long_x,
            short_entries=short_e,
            short_exits=short_x,
            init_cash=capital,
            size=size,
            size_type=size_type,
            fees=fees,
            slippage=slippage,
            freq=RESAMPLE_MAP.get(timeframe, timeframe),
        )

    # ── magnifier mode (windowed recompute) ──────────────────

    def _run_magnified(self, df_1m, df_tf, timeframe, strategy, params,
                       capital, fees, slippage, size, size_type, progress):
        """Magnifier with dynamic resolution and progress reporting.

        Optimized: pre-allocates a window buffer DataFrame and updates the
        last row in-place instead of creating+concatenating DataFrames per
        sub-bar.  This eliminates ~15 allocations per HT bar.
        """
        mag_tf = compute_magnifier_resolution(timeframe)
        df_mag = resample_ohlcv(df_1m, mag_tf) if mag_tf != "1m" else df_1m

        warmup = strategy.warmup
        window_size = warmup * 3
        td = _TF_DELTA[timeframe]

        tf_index = df_tf.index
        mag_index = df_mag.index
        mag_open = df_mag["open"].values
        mag_high = df_mag["high"].values
        mag_low = df_mag["low"].values
        mag_close = df_mag["close"].values
        mag_volume = df_mag["volume"].values

        n_mag = len(df_mag)
        long_entries_mag = np.zeros(n_mag, dtype=bool)
        long_exits_mag = np.zeros(n_mag, dtype=bool)
        short_entries_mag = np.zeros(n_mag, dtype=bool)
        short_exits_mag = np.zeros(n_mag, dtype=bool)

        in_long = False
        in_short = False

        total_bars = len(tf_index) - warmup
        report_interval = max(1, total_bars // 50)

        # Pre-extract numpy arrays from the HT DataFrame for fast slicing
        tf_open = df_tf["open"].values
        tf_high = df_tf["high"].values
        tf_low = df_tf["low"].values
        tf_close = df_tf["close"].values
        tf_volume = df_tf["volume"].values
        tf_cols = ["open", "high", "low", "close", "volume"]

        for bar_idx in range(warmup, len(tf_index)):
            # Report progress every ~2% of bars
            bars_done = bar_idx - warmup
            if bars_done % report_interval == 0:
                loop_pct = bars_done / max(1, total_bars)
                overall_pct = 20 + int(loop_pct * 68)  # 20%-88%
                progress(overall_pct, f"Magnifier: bar {bars_done}/{total_bars}")

            bar_start = tf_index[bar_idx]
            bar_end = bar_start + td

            pos_start = mag_index.searchsorted(bar_start, side="left")
            pos_end = mag_index.searchsorted(bar_end, side="left")
            if pos_start >= pos_end:
                continue

            # Build the window buffer once per HT bar: completed rows + 1 forming row.
            # Use numpy to construct the data block, then wrap in a DataFrame once.
            win_start = max(0, bar_idx - window_size)
            n_completed = bar_idx - win_start

            # Stack completed window data from pre-extracted arrays
            buf = np.empty((n_completed + 1, 5), dtype=np.float64)
            buf[:n_completed, 0] = tf_open[win_start:bar_idx]
            buf[:n_completed, 1] = tf_high[win_start:bar_idx]
            buf[:n_completed, 2] = tf_low[win_start:bar_idx]
            buf[:n_completed, 3] = tf_close[win_start:bar_idx]
            buf[:n_completed, 4] = tf_volume[win_start:bar_idx]

            # Pre-fill the forming row placeholder (will be updated in inner loop)
            forming_open = float(mag_open[pos_start])
            forming_high = -np.inf
            forming_low = np.inf
            forming_vol = 0.0

            # Build index once; we'll update the last entry in-place
            win_idx = list(tf_index[win_start:bar_idx]) + [mag_index[pos_start]]
            window = pd.DataFrame(buf, index=win_idx, columns=tf_cols)

            for pos in range(pos_start, pos_end):
                forming_high = max(forming_high, float(mag_high[pos]))
                forming_low = min(forming_low, float(mag_low[pos]))
                forming_close = float(mag_close[pos])
                forming_vol += float(mag_volume[pos])

                # Update the last row in-place (no allocation)
                window.iloc[-1, 0] = forming_open
                window.iloc[-1, 1] = forming_high
                window.iloc[-1, 2] = forming_low
                window.iloc[-1, 3] = forming_close
                window.iloc[-1, 4] = forming_vol
                window.index = win_idx[:-1] + [mag_index[pos]]

                try:
                    le, lx, se, sx = strategy.compute(window, params)
                except Exception:
                    continue

                last_le = bool(le.iloc[-1]) if not pd.isna(le.iloc[-1]) else False
                last_lx = bool(lx.iloc[-1]) if not pd.isna(lx.iloc[-1]) else False
                last_se = bool(se.iloc[-1]) if not pd.isna(se.iloc[-1]) else False
                last_sx = bool(sx.iloc[-1]) if not pd.isna(sx.iloc[-1]) else False

                if not in_long and last_le:
                    long_entries_mag[pos] = True
                    in_long = True
                    break
                if in_long and last_lx:
                    long_exits_mag[pos] = True
                    in_long = False
                    break
                if not in_short and last_se:
                    short_entries_mag[pos] = True
                    in_short = True
                    break
                if in_short and last_sx:
                    short_exits_mag[pos] = True
                    in_short = False
                    break

        progress(88, "Magnifier loop complete")

        mag_freq = RESAMPLE_MAP.get(mag_tf, mag_tf)
        import vectorbt as vbt
        return vbt.Portfolio.from_signals(
            close=df_mag["close"],
            entries=pd.Series(long_entries_mag, index=df_mag.index),
            exits=pd.Series(long_exits_mag, index=df_mag.index),
            short_entries=pd.Series(short_entries_mag, index=df_mag.index),
            short_exits=pd.Series(short_exits_mag, index=df_mag.index),
            init_cash=capital,
            size=size,
            size_type=size_type,
            fees=fees,
            slippage=slippage,
            freq=mag_freq,
        )

    # ── result extraction ────────────────────────────────────

    @staticmethod
    def _extract_result(pf, df_tf, strategy, symbol, exchange, timeframe,
                        start_date, end_date, mode, params, capital,
                        ) -> BacktestResult:
        """Extract maximum-detail BacktestResult from vbt.Portfolio."""
        stats = pf.stats()

        # ── Compute annualized metrics (not in vbt.stats()) ──────
        try:
            returns = pf.returns()
            total_return = float(stats.get("Total Return [%]", 0)) / 100
            n_days = (returns.index[-1] - returns.index[0]).days
            if n_days > 0:
                annualized_return = ((1 + total_return) ** (365.25 / n_days) - 1) * 100
                annualized_vol = float(returns.std() * (252 ** 0.5) * 100)
            else:
                annualized_return = None
                annualized_vol = None
        except Exception:
            annualized_return = None
            annualized_vol = None

        # ── Equity curve (sample to ~1000 points max) ────────
        equity = pf.value()
        total_points = len(equity)
        step = max(1, total_points // 1000)
        sampled_eq = equity.iloc[::step]
        equity_curve = [
            {"timestamp": ts.isoformat(), "value": round(float(v), 2)}
            for ts, v in sampled_eq.items()
        ]

        # ── Returns series (same sampling) ───────────────────
        returns_series = pf.returns()
        sampled_ret = returns_series.iloc[::step]
        returns_data = [
            {"timestamp": ts.isoformat(), "return": round(float(v), 6)}
            for ts, v in sampled_ret.items()
        ]

        # ── Drawdown underwater curve ────────────────────────
        try:
            dd_series = pf.drawdown()
            sampled_dd = dd_series.iloc[::step]
            drawdown_curve = [
                {"timestamp": ts.isoformat(),
                 "drawdown_pct": round(float(v) * 100, 4)}
                for ts, v in sampled_dd.items()
            ]
        except Exception:
            drawdown_curve = []

        # ── OHLCV bars for candlestick chart ─────────────────
        ohlcv_step = max(1, len(df_tf) // MAX_CHART_BARS)
        sampled_ohlcv = df_tf.iloc[::ohlcv_step]
        ohlcv_bars = [
            {
                "timestamp": ts.isoformat(),
                "open": round(float(row["open"]), 4),
                "high": round(float(row["high"]), 4),
                "low": round(float(row["low"]), 4),
                "close": round(float(row["close"]), 4),
                "volume": round(float(row["volume"]), 2),
            }
            for ts, row in sampled_ohlcv.iterrows()
        ]

        # ── Trade records (full detail) ──────────────────────
        trade_records: List[TradeRecord] = []
        try:
            readable = pf.trades.records_readable
            if len(readable) > 0:
                for idx, row in readable.iterrows():
                    tid = int(row.get("Exit Trade Id",
                              row.get("Trade Id", idx)))
                    is_closed = row.get("Status") == "Closed"
                    trade_records.append(TradeRecord(
                        trade_id=tid,
                        position_id=int(row.get("Position Id", tid)),
                        direction=str(row.get("Direction", "Long")),
                        status=str(row.get("Status", "Open")),
                        entry_time=str(row.get("Entry Timestamp", "")),
                        exit_time=str(row["Exit Timestamp"]) if is_closed else None,
                        entry_price=round(float(row.get("Avg Entry Price", 0)), 8),
                        exit_price=(round(float(row["Avg Exit Price"]), 8)
                                    if is_closed else None),
                        size=float(row.get("Size", 0)),
                        entry_fees=round(float(row.get("Entry Fees", 0)), 4),
                        exit_fees=round(float(row.get("Exit Fees", 0)), 4),
                        pnl=round(float(row.get("PnL", 0)), 2),
                        return_pct=round(float(row.get("Return", 0)) * 100, 4),
                        duration=str(row.get("Duration", "")),
                    ))
        except Exception:
            pass

        # ── Order records ────────────────────────────────────
        order_records: List[OrderRecord] = []
        try:
            orders_readable = pf.orders.records_readable
            if len(orders_readable) > 0:
                for _, row in orders_readable.iterrows():
                    order_records.append(OrderRecord(
                        order_id=int(row.get("Order Id", 0)),
                        timestamp=str(row.get("Timestamp", "")),
                        side=str(row.get("Side", "")),
                        price=round(float(row.get("Price", 0)), 8),
                        size=float(row.get("Size", 0)),
                        fees=round(float(row.get("Fees", 0)), 4),
                    ))
        except Exception:
            pass

        # ── Drawdown records ─────────────────────────────────
        dd_records: List[DrawdownRecord] = []
        try:
            dd_readable = pf.drawdowns.records_readable
            if len(dd_readable) > 0:
                for _, row in dd_readable.iterrows():
                    peak_val = float(row.get("Peak Value", 0))
                    valley_val = float(row.get("Valley Value", 0))
                    dd_pct = ((valley_val / peak_val) - 1) * 100 if peak_val else 0
                    is_recovered = row.get("Status") == "Recovered"
                    dd_records.append(DrawdownRecord(
                        drawdown_id=int(row.get("Drawdown Id", 0)),
                        peak_time=str(row.get("Peak Timestamp", "")),
                        start_time=str(row.get("Start Timestamp", "")),
                        valley_time=str(row.get("Valley Timestamp", "")),
                        end_time=(str(row["End Timestamp"])
                                  if is_recovered else None),
                        peak_value=round(peak_val, 2),
                        valley_value=round(valley_val, 2),
                        end_value=(round(float(row["End Value"]), 2)
                                   if is_recovered else None),
                        drawdown_pct=round(dd_pct, 4),
                        duration=str(row.get("Duration", "")),
                        status=str(row.get("Status", "Active")),
                    ))
        except Exception:
            pass

        # ── Trade markers for chart overlay ──────────────────
        trade_markers = Backtester._build_trade_markers(
            order_records, trade_records, df_tf.index,
        )

        return BacktestResult(
            strategy_name=strategy.name,
            symbol=symbol,
            exchange=exchange,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            period=str(stats.get("Period", "")),
            mode=mode,
            params=params,
            # Performance
            initial_capital=capital,
            final_value=_safe_float(stats.get("End Value")) or capital,
            total_return_pct=_safe_float(stats.get("Total Return [%]")) or 0.0,
            annualized_return_pct=_safe_float(annualized_return),
            annualized_volatility_pct=_safe_float(annualized_vol),
            benchmark_return_pct=_safe_float(stats.get("Benchmark Return [%]")) or 0.0,
            total_fees_paid=_safe_float(stats.get("Total Fees Paid")) or 0.0,
            max_gross_exposure_pct=_safe_float(stats.get("Max Gross Exposure [%]")) or 0.0,
            # Risk-adjusted
            sharpe_ratio=_safe_float(stats.get("Sharpe Ratio")),
            calmar_ratio=_safe_float(stats.get("Calmar Ratio")),
            sortino_ratio=_safe_float(stats.get("Sortino Ratio")),
            omega_ratio=_safe_float(stats.get("Omega Ratio")),
            # Drawdown
            max_drawdown_pct=_safe_float(stats.get("Max Drawdown [%]")) or 0.0,
            max_drawdown_duration=str(stats.get("Max Drawdown Duration", "")),
            # Trade summary
            total_trades=int(stats.get("Total Trades", 0)),
            total_closed_trades=int(stats.get("Total Closed Trades", 0)),
            total_open_trades=int(stats.get("Total Open Trades", 0)),
            open_trade_pnl=_safe_float(stats.get("Open Trade PnL")) or 0.0,
            win_rate_pct=_safe_float(stats.get("Win Rate [%]")) or 0.0,
            best_trade_pct=_safe_float(stats.get("Best Trade [%]")) or 0.0,
            worst_trade_pct=_safe_float(stats.get("Worst Trade [%]")) or 0.0,
            avg_winning_trade_pct=_safe_float(stats.get("Avg Winning Trade [%]")) or 0.0,
            avg_losing_trade_pct=_safe_float(stats.get("Avg Losing Trade [%]")) or 0.0,
            avg_winning_duration=str(stats.get("Avg Winning Trade Duration", "")),
            avg_losing_duration=str(stats.get("Avg Losing Trade Duration", "")),
            profit_factor=_safe_float(stats.get("Profit Factor")),
            expectancy=_safe_float(stats.get("Expectancy")) or 0.0,
            # Time series
            equity_curve=equity_curve,
            returns=returns_data,
            drawdown_curve=drawdown_curve,
            # OHLCV bars for candlestick chart
            ohlcv_bars=ohlcv_bars,
            # Trade markers
            trade_markers=trade_markers,
            # Detail records
            trades=trade_records,
            orders=order_records,
            drawdowns=dd_records,
            # Raw
            portfolio=pf,
        )

    # ── trade markers ────────────────────────────────────────

    @staticmethod
    def _build_trade_markers(
        orders: List[OrderRecord],
        trades: List[TradeRecord],
        tf_index: pd.DatetimeIndex,
    ) -> List[Dict[str, Any]]:
        """Build chart markers from trade records (not orders).

        Each trade produces exactly one entry marker and one exit marker
        (if the trade is closed). This avoids the issue where a single
        order serves as both a long exit and short entry simultaneously.
        """
        if not trades or len(tf_index) == 0:
            return []

        markers: List[Dict[str, Any]] = []

        def snap_ts(ts_str: str) -> str:
            """Snap a timestamp to the nearest chart-TF candle."""
            ts = pd.Timestamp(ts_str)
            idx = tf_index.searchsorted(ts, side="right") - 1
            idx = max(0, min(idx, len(tf_index) - 1))
            return tf_index[idx].isoformat()

        for t in trades:
            is_long = t.direction == "Long"

            # Entry marker
            if t.entry_time and t.entry_price:
                markers.append({
                    "timestamp": snap_ts(t.entry_time),
                    "price": round(t.entry_price, 4),
                    "side": "Buy" if is_long else "Sell",
                    "direction": t.direction,
                    "is_entry": True,
                    "trade_id": t.trade_id,
                    "label": "",
                    "pnl": None,
                })

            # Exit marker (only for closed trades)
            if t.exit_time and t.exit_price:
                markers.append({
                    "timestamp": snap_ts(t.exit_time),
                    "price": round(t.exit_price, 4),
                    "side": "Sell" if is_long else "Buy",
                    "direction": t.direction,
                    "is_entry": False,
                    "trade_id": t.trade_id,
                    "label": "",
                    "pnl": round(t.pnl, 2) if t.pnl else None,
                })

        return markers
