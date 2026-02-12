#!/usr/bin/env python3
"""
Benchmark: pandas-only ta.py vs Numba-accelerated ta.py

Runs each indicator on synthetic OHLCV data at three sizes:
  500 bars  (magnifier window — called 1000s of times)
  5 000 bars (typical chart)
  50 000 bars (large dataset)

Reports median time over multiple runs, comparing old vs new.
"""

from __future__ import annotations

import sys
import time

import numpy as np
import pandas as pd

# ── Synthetic OHLCV generator ──────────────────────────────────────────


def make_ohlcv(n: int, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100.0 + np.cumsum(rng.normal(0, 0.5, n))
    high = close + rng.uniform(0.1, 1.5, n)
    low = close - rng.uniform(0.1, 1.5, n)
    opn = close + rng.normal(0, 0.3, n)
    volume = rng.uniform(1e4, 1e6, n)
    idx = pd.date_range("2020-01-01", periods=n, freq="1min")
    return pd.DataFrame({
        "open": opn, "high": high, "low": low,
        "close": close, "volume": volume,
    }, index=idx)


# ── Old (pure pandas) implementations ─────────────────────────────────

class ta_old:
    """Copy of the original pure-pandas implementations for benchmarking."""

    @staticmethod
    def sma(source, length):
        return source.rolling(window=int(length), min_periods=int(length)).mean()

    @staticmethod
    def ema(source, length):
        return source.ewm(span=int(length), adjust=False).mean()

    @staticmethod
    def rma(source, length):
        return source.ewm(alpha=1.0 / int(length), adjust=False).mean()

    @staticmethod
    def wma(source, length):
        length = int(length)
        weights = np.arange(1, length + 1, dtype=float)
        return source.rolling(window=length).apply(
            lambda x: np.dot(x, weights) / weights.sum(), raw=True)

    @staticmethod
    def alma(source, length, offset=0.85, sigma=6.0):
        length = int(length)
        m = offset * (length - 1)
        s = length / sigma
        weights = np.array([np.exp(-((i - m) ** 2) / (2 * s * s))
                            for i in range(length)])
        weights /= weights.sum()
        return source.rolling(window=length).apply(
            lambda x: np.dot(x, weights), raw=True)

    @staticmethod
    def swma(source):
        weights = np.array([1, 2, 2, 1], dtype=float)
        weights /= weights.sum()
        return source.rolling(window=4).apply(
            lambda x: np.dot(x, weights), raw=True)

    @staticmethod
    def rsi(source, length=14):
        delta = source.diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        avg_gain = ta_old.rma(gain, length)
        avg_loss = ta_old.rma(loss, length)
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    @staticmethod
    def macd(source, fast=12, slow=26, signal=9):
        ef = ta_old.ema(source, fast)
        es = ta_old.ema(source, slow)
        ml = ef - es
        sl = ta_old.ema(ml, signal)
        return ml, sl, ml - sl

    @staticmethod
    def atr(high, low, close, length=14):
        tr = pd.concat([
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs(),
        ], axis=1).max(axis=1)
        return ta_old.rma(tr, length)

    @staticmethod
    def supertrend(high, low, close, factor=3.0, period=10):
        period = int(period)
        atr_val = ta_old.atr(high, low, close, period)
        hl2 = (high + low) / 2
        upper_band = hl2 + factor * atr_val
        lower_band = hl2 - factor * atr_val
        n = len(close)
        st = np.zeros(n); direction = np.ones(n)
        ub = upper_band.values.copy(); lb = lower_band.values.copy()
        cl = close.values
        for i in range(1, n):
            if np.isnan(ub[i]) or np.isnan(lb[i]):
                st[i] = np.nan; direction[i] = direction[i - 1]; continue
            if not (ub[i] < ub[i - 1] or cl[i - 1] > ub[i - 1]): ub[i] = ub[i - 1]
            if not (lb[i] > lb[i - 1] or cl[i - 1] < lb[i - 1]): lb[i] = lb[i - 1]
            if direction[i - 1] == -1:
                if cl[i] < lb[i]: direction[i] = 1; st[i] = ub[i]
                else: direction[i] = -1; st[i] = lb[i]
            else:
                if cl[i] > ub[i]: direction[i] = -1; st[i] = lb[i]
                else: direction[i] = 1; st[i] = ub[i]
        idx = close.index
        return pd.Series(st, index=idx), pd.Series(direction, index=idx)

    @staticmethod
    def sar(high, low, start=0.02, inc=0.02, max_val=0.2):
        n = len(high); h = high.values; lo = low.values
        psar = np.full(n, np.nan); af = start; trend = 1; ep = h[0]; psar[0] = lo[0]
        for i in range(1, n):
            if np.isnan(h[i]) or np.isnan(lo[i]): psar[i] = psar[i-1]; continue
            prev = psar[i-1]
            if trend == 1:
                psar[i] = prev + af * (ep - prev)
                psar[i] = min(psar[i], lo[i-1])
                if i >= 2: psar[i] = min(psar[i], lo[i-2])
                if lo[i] < psar[i]: trend = -1; psar[i] = ep; ep = lo[i]; af = start
                else:
                    if h[i] > ep: ep = h[i]; af = min(af + inc, max_val)
            else:
                psar[i] = prev + af * (ep - prev)
                psar[i] = max(psar[i], h[i-1])
                if i >= 2: psar[i] = max(psar[i], h[i-2])
                if h[i] > psar[i]: trend = 1; psar[i] = ep; ep = h[i]; af = start
                else:
                    if lo[i] < ep: ep = lo[i]; af = min(af + inc, max_val)
        return pd.Series(psar, index=high.index)

    @staticmethod
    def cci(source, length=20):
        length = int(length)
        mean = source.rolling(length).mean()
        mad = source.rolling(length).apply(
            lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
        return (source - mean) / (0.015 * mad)

    @staticmethod
    def cog(source, length=10):
        length = int(length)
        weights = np.arange(1, length + 1, dtype=float)
        num = source.rolling(length).apply(
            lambda x: -np.dot(x, weights), raw=True)
        denom = source.rolling(length).sum()
        return num / denom

    @staticmethod
    def percentrank(source, length=20):
        length = int(length)
        def _pctrank(window):
            return np.sum(window[-1] >= window[:-1]) / (len(window) - 1) * 100
        return source.rolling(length + 1).apply(_pctrank, raw=True)

    @staticmethod
    def linreg(source, length, offset=0):
        length = int(length)
        def _linreg(window):
            x = np.arange(len(window))
            coeffs = np.polyfit(x, window, 1)
            return np.polyval(coeffs, len(window) - 1 - offset)
        return source.rolling(length).apply(_linreg, raw=True)

    @staticmethod
    def dmi(high, low, close, di_length=14, adx_smoothing=14):
        di_length = int(di_length); adx_smoothing = int(adx_smoothing)
        up = high.diff(); down = -low.diff()
        plus_dm = ((up > down) & (up > 0)).astype(float) * up
        minus_dm = ((down > up) & (down > 0)).astype(float) * down
        atr_val = ta_old.atr(high, low, close, di_length)
        plus_di = 100 * ta_old.rma(plus_dm, di_length) / atr_val
        minus_di = 100 * ta_old.rma(minus_dm, di_length) / atr_val
        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
        adx = ta_old.rma(dx, adx_smoothing)
        return plus_di, minus_di, adx

    @staticmethod
    def stoch(close, high, low, length=14, smooth_k=1, smooth_d=3):
        length = int(length)
        smooth_k = int(smooth_k) if smooth_k else 1
        smooth_d = int(smooth_d) if smooth_d else 3
        ll = low.rolling(length).min()
        hh = high.rolling(length).max()
        raw_k = 100 * (close - ll) / (hh - ll)
        k = raw_k.rolling(smooth_k).mean() if smooth_k > 1 else raw_k
        d = k.rolling(smooth_d).mean()
        return k, d


# ── Import new Numba-accelerated ta ───────────────────────────────────

sys.path.insert(0, ".")
from server.ta import ta as ta_new  # noqa: E402


# ── Benchmark runner ──────────────────────────────────────────────────

def bench(fn, repeats=5):
    """Time a callable, return median seconds."""
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    times.sort()
    return times[len(times) // 2]


def main():
    sizes = [500, 5_000, 50_000]

    # Indicator benchmarks: (name, old_fn, new_fn)
    # We'll build these per-size since they reference the dataframe.

    print("=" * 90)
    print(f"{'Indicator':<18} {'N':>7}  {'Pandas (ms)':>12}  {'Numba (ms)':>12}  {'Speedup':>9}")
    print("=" * 90)

    for n in sizes:
        df = make_ohlcv(n)
        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]

        # Adjust repeats — more for small data, fewer for large
        reps = 20 if n <= 1000 else (10 if n <= 10_000 else 5)

        indicators = [
            ("SMA(20)",
             lambda: ta_old.sma(close, 20),
             lambda: ta_new.sma(close, 20)),
            ("EMA(20)",
             lambda: ta_old.ema(close, 20),
             lambda: ta_new.ema(close, 20)),
            ("RMA(14)",
             lambda: ta_old.rma(close, 14),
             lambda: ta_new.rma(close, 14)),
            ("WMA(20)",
             lambda: ta_old.wma(close, 20),
             lambda: ta_new.wma(close, 20)),
            ("ALMA(20)",
             lambda: ta_old.alma(close, 20),
             lambda: ta_new.alma(close, 20)),
            ("SWMA",
             lambda: ta_old.swma(close),
             lambda: ta_new.swma(close)),
            ("RSI(14)",
             lambda: ta_old.rsi(close, 14),
             lambda: ta_new.rsi(close, 14)),
            ("MACD",
             lambda: ta_old.macd(close),
             lambda: ta_new.macd(close)),
            ("ATR(14)",
             lambda: ta_old.atr(high, low, close, 14),
             lambda: ta_new.atr(high, low, close, 14)),
            ("SuperTrend",
             lambda: ta_old.supertrend(high, low, close),
             lambda: ta_new.supertrend(high, low, close)),
            ("SAR",
             lambda: ta_old.sar(high, low),
             lambda: ta_new.sar(high, low)),
            ("CCI(20)",
             lambda: ta_old.cci(close, 20),
             lambda: ta_new.cci(close, 20)),
            ("COG(10)",
             lambda: ta_old.cog(close, 10),
             lambda: ta_new.cog(close, 10)),
            ("PercentRank(20)",
             lambda: ta_old.percentrank(close, 20),
             lambda: ta_new.percentrank(close, 20)),
            ("LinReg(20)",
             lambda: ta_old.linreg(close, 20),
             lambda: ta_new.linreg(close, 20)),
            ("DMI(14,14)",
             lambda: ta_old.dmi(high, low, close),
             lambda: ta_new.dmi(high, low, close)),
            ("Stoch(14,1,3)",
             lambda: ta_old.stoch(close, high, low),
             lambda: ta_new.stoch(close, high, low)),
        ]

        for name, old_fn, new_fn in indicators:
            # Warmup for Numba JIT (first call compiles)
            new_fn()

            t_old = bench(old_fn, reps)
            t_new = bench(new_fn, reps)
            speedup = t_old / t_new if t_new > 0 else float("inf")

            print(f"{name:<18} {n:>7,}  {t_old*1000:>12.3f}  {t_new*1000:>12.3f}  {speedup:>8.1f}x")

        print("-" * 90)

    print("\nNote: Numba first-call JIT compilation time excluded (warmup call).")
    print("Speedup = Pandas_time / Numba_time (higher is better).\n")


if __name__ == "__main__":
    main()
