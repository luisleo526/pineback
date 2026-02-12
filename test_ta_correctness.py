#!/usr/bin/env python3
"""
Correctness test: verify that Numba-accelerated ta.py produces
identical results to the original pure-pandas implementation.

Compares every indicator at multiple data sizes. Uses np.allclose
with a tight tolerance (1e-10) to account for floating-point ordering
differences between pandas ewm() and the Numba EMA loop.
"""

from __future__ import annotations

import sys
import numpy as np
import pandas as pd

# ── Synthetic OHLCV ────────────────────────────────────────────────────


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
# Copied verbatim from the original ta.py

class ta_old:

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
        def _lr(window):
            x = np.arange(len(window))
            coeffs = np.polyfit(x, window, 1)
            return np.polyval(coeffs, len(window) - 1 - offset)
        return source.rolling(length).apply(_lr, raw=True)

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

    @staticmethod
    def bb(source, length=20, mult=2.0):
        length = int(length)
        middle = ta_old.sma(source, length)
        std = source.rolling(window=length).std()
        return middle, middle + mult * std, middle - mult * std

    @staticmethod
    def hma(source, length):
        length = int(length)
        half = max(1, length // 2)
        sqrt_len = max(1, int(np.sqrt(length)))
        wma_half = ta_old.wma(source, half)
        wma_full = ta_old.wma(source, length)
        diff = 2 * wma_half - wma_full
        return ta_old.wma(diff, sqrt_len)


# ── Import new Numba ta ───────────────────────────────────────────────

sys.path.insert(0, ".")
from server.ta import ta as ta_new  # noqa: E402


# ── Comparison helpers ─────────────────────────────────────────────────

def compare_series(name: str, old: pd.Series, new: pd.Series,
                   atol: float = 1e-10, rtol: float = 1e-10) -> bool:
    """Compare two Series, ignoring NaN positions. Returns True if match."""
    a = old.values.astype(np.float64)
    b = new.values.astype(np.float64)

    if len(a) != len(b):
        print(f"  FAIL {name}: length mismatch {len(a)} vs {len(b)}")
        return False

    # Both NaN at same positions?
    nan_a = np.isnan(a)
    nan_b = np.isnan(b)
    nan_match = np.array_equal(nan_a, nan_b)

    # Compare non-NaN values
    mask = ~nan_a & ~nan_b
    if mask.sum() == 0:
        if nan_match:
            print(f"  OK   {name}: all NaN (matching)")
            return True
        else:
            print(f"  FAIL {name}: NaN pattern mismatch")
            return False

    vals_close = np.allclose(a[mask], b[mask], atol=atol, rtol=rtol)

    if vals_close and nan_match:
        max_diff = np.max(np.abs(a[mask] - b[mask]))
        print(f"  OK   {name}: max_diff={max_diff:.2e}, "
              f"{mask.sum()} values compared, {nan_a.sum()} NaNs")
        return True

    # Detailed failure report
    if not vals_close:
        diffs = np.abs(a[mask] - b[mask])
        max_diff = np.max(diffs)
        max_idx = np.argmax(diffs)
        real_idx = np.where(mask)[0][max_idx]
        print(f"  FAIL {name}: max_diff={max_diff:.2e} at index {real_idx} "
              f"(old={a[real_idx]:.10f}, new={b[real_idx]:.10f})")
    if not nan_match:
        diff_positions = np.where(nan_a != nan_b)[0]
        print(f"  FAIL {name}: NaN mismatch at {len(diff_positions)} positions, "
              f"first: {diff_positions[:5]}")
    return False


def compare_tuple(name: str, old_tuple, new_tuple,
                  labels: list, atol=1e-10, rtol=1e-10) -> bool:
    ok = True
    for label, old_s, new_s in zip(labels, old_tuple, new_tuple):
        if not compare_series(f"{name}.{label}", old_s, new_s, atol, rtol):
            ok = False
    return ok


# ── Main test ─────────────────────────────────────────────────────────

def main():
    passed = 0
    failed = 0
    sizes = [500, 5_000, 50_000]

    for n in sizes:
        print(f"\n{'='*70}")
        print(f"  Testing with N = {n:,}")
        print(f"{'='*70}")

        df = make_ohlcv(n)
        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]

        # For EMA/RMA the Numba kernel handles NaN seeding differently on
        # the very first element. pandas ewm starts from index 0 with the
        # raw value, and so does our kernel — but intermediate NaN handling
        # can cause tiny float divergence. We use a relaxed tolerance for
        # EMA-based indicators.
        ema_tol = dict(atol=1e-8, rtol=1e-8)
        strict = dict(atol=1e-10, rtol=1e-10)

        tests = [
            # (name, old_result, new_result, is_tuple, labels, tol)
            ("SMA(20)",
             ta_old.sma(close, 20), ta_new.sma(close, 20),
             False, None, strict),
            ("EMA(20)",
             ta_old.ema(close, 20), ta_new.ema(close, 20),
             False, None, ema_tol),
            ("RMA(14)",
             ta_old.rma(close, 14), ta_new.rma(close, 14),
             False, None, ema_tol),
            ("WMA(20)",
             ta_old.wma(close, 20), ta_new.wma(close, 20),
             False, None, strict),
            ("ALMA(20)",
             ta_old.alma(close, 20), ta_new.alma(close, 20),
             False, None, strict),
            ("SWMA",
             ta_old.swma(close), ta_new.swma(close),
             False, None, strict),
            ("HMA(20)",
             ta_old.hma(close, 20), ta_new.hma(close, 20),
             False, None, strict),
            ("RSI(14)",
             ta_old.rsi(close, 14), ta_new.rsi(close, 14),
             False, None, ema_tol),
            ("MACD",
             ta_old.macd(close), ta_new.macd(close),
             True, ["line", "signal", "hist"], ema_tol),
            ("ATR(14)",
             ta_old.atr(high, low, close, 14),
             ta_new.atr(high, low, close, 14),
             False, None, ema_tol),
            ("BB(20)",
             ta_old.bb(close, 20), ta_new.bb(close, 20),
             True, ["mid", "upper", "lower"], strict),
            ("SuperTrend",
             ta_old.supertrend(high, low, close),
             ta_new.supertrend(high, low, close),
             True, ["value", "direction"], ema_tol),
            ("SAR",
             ta_old.sar(high, low), ta_new.sar(high, low),
             False, None, strict),
            ("CCI(20)",
             ta_old.cci(close, 20), ta_new.cci(close, 20),
             False, None, strict),
            ("COG(10)",
             ta_old.cog(close, 10), ta_new.cog(close, 10),
             False, None, strict),
            ("PercentRank(20)",
             ta_old.percentrank(close, 20),
             ta_new.percentrank(close, 20),
             False, None, strict),
            ("LinReg(20)",
             ta_old.linreg(close, 20), ta_new.linreg(close, 20),
             False, None, dict(atol=1e-6, rtol=1e-6)),  # polyfit has some float variance
            ("DMI(14,14)",
             ta_old.dmi(high, low, close),
             ta_new.dmi(high, low, close),
             True, ["+DI", "-DI", "ADX"], ema_tol),
            ("Stoch(14,1,3)",
             ta_old.stoch(close, high, low),
             ta_new.stoch(close, high, low),
             True, ["K", "D"], strict),
        ]

        for name, old_res, new_res, is_tuple, labels, tol in tests:
            if is_tuple:
                ok = compare_tuple(name, old_res, new_res, labels, **tol)
            else:
                ok = compare_series(name, old_res, new_res, **tol)
            if ok:
                passed += 1
            else:
                failed += 1

    print(f"\n{'='*70}")
    print(f"  SUMMARY: {passed} passed, {failed} failed")
    print(f"{'='*70}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
