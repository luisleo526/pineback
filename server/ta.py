"""
Vectorized PineScript v6 ``ta.*`` indicators — Numba-accelerated.

Every method is a ``@staticmethod`` on the ``ta`` class.  Inputs and outputs
are ``pd.Series`` (or tuples of Series for multi-output indicators).

Indicators that PineScript accesses implicitly (e.g. ``ta.atr(14)`` uses
high/low/close internally) receive those columns as **explicit** arguments
here.  The code generator injects ``_high, _low, _close, _volume`` at
call sites.

Hot-path computations delegate to ``@njit`` kernels in
``_numba_kernels.py``.  The pandas wrappers here handle Series ↔ ndarray
conversion and index preservation.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np
import pandas as pd

from . import _numba_kernels as _nb


def _to_arr(s: pd.Series) -> np.ndarray:
    """Extract float64 numpy array from a Series."""
    return np.ascontiguousarray(s.values, dtype=np.float64)


def _wrap(arr: np.ndarray, index: pd.Index) -> pd.Series:
    """Wrap a numpy array back into a pandas Series."""
    return pd.Series(arr, index=index, dtype=np.float64)


class ta:
    """PineScript v6 ``ta.*`` indicator functions — Numba-accelerated."""

    # ──────────────────────────────────────────────────────────────────────
    #  Trend / Moving Averages
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def sma(source: pd.Series, length: int) -> pd.Series:
        return _wrap(_nb._sma(_to_arr(source), int(length)), source.index)

    @staticmethod
    def ema(source: pd.Series, length: int) -> pd.Series:
        return _wrap(_nb._ema(_to_arr(source), int(length)), source.index)

    @staticmethod
    def rma(source: pd.Series, length: int) -> pd.Series:
        """Wilder's smoothing (used internally by RSI / ATR)."""
        return _wrap(_nb._rma(_to_arr(source), int(length)), source.index)

    @staticmethod
    def wma(source: pd.Series, length: int) -> pd.Series:
        """Weighted moving average."""
        return _wrap(_nb._wma(_to_arr(source), int(length)), source.index)

    @staticmethod
    def vwma(source: pd.Series, volume: pd.Series, length: int) -> pd.Series:
        """Volume-weighted moving average."""
        length = int(length)
        return (source * volume).rolling(length).sum() / volume.rolling(length).sum()

    @staticmethod
    def hma(source: pd.Series, length: int) -> pd.Series:
        """Hull moving average: WMA(2*WMA(n/2) - WMA(n), sqrt(n))."""
        length = int(length)
        half = max(1, length // 2)
        sqrt_len = max(1, int(np.sqrt(length)))
        wma_half = ta.wma(source, half)
        wma_full = ta.wma(source, length)
        diff = 2 * wma_half - wma_full
        return ta.wma(diff, sqrt_len)

    @staticmethod
    def alma(source: pd.Series, length: int, offset: float = 0.85,
             sigma: float = 6.0) -> pd.Series:
        """Arnaud Legoux moving average."""
        return _wrap(
            _nb._alma(_to_arr(source), int(length), offset, sigma),
            source.index,
        )

    @staticmethod
    def swma(source: pd.Series) -> pd.Series:
        """Symmetric weighted moving average (fixed 4-bar)."""
        return _wrap(_nb._swma(_to_arr(source)), source.index)

    @staticmethod
    def supertrend(high: pd.Series, low: pd.Series, close: pd.Series,
                   factor: float = 3.0, period: int = 10,
                   ) -> Tuple[pd.Series, pd.Series]:
        """SuperTrend indicator.  Returns (value, direction).
        direction: -1 = uptrend (bullish), 1 = downtrend (bearish)."""
        st, direction = _nb._supertrend(
            _to_arr(high), _to_arr(low), _to_arr(close),
            float(factor), int(period),
        )
        idx = close.index
        return _wrap(st, idx), _wrap(direction, idx)

    # ──────────────────────────────────────────────────────────────────────
    #  Momentum
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def rsi(source: pd.Series, length: int = 14) -> pd.Series:
        return _wrap(_nb._rsi(_to_arr(source), int(length)), source.index)

    @staticmethod
    def macd(source: pd.Series, fast_length: int = 12,
             slow_length: int = 26, signal_length: int = 9,
             ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Returns (macd_line, signal_line, histogram)."""
        ml, sl, hist = _nb._macd(
            _to_arr(source), int(fast_length),
            int(slow_length), int(signal_length),
        )
        idx = source.index
        return _wrap(ml, idx), _wrap(sl, idx), _wrap(hist, idx)

    @staticmethod
    def stoch(close: pd.Series, high: pd.Series, low: pd.Series,
              length: int = 14, smooth_k: int = 1, smooth_d: int = 3):
        """Stochastic oscillator. Returns (K, D) tuple for multi-output support."""
        k, d = _nb._stoch(
            _to_arr(close), _to_arr(high), _to_arr(low),
            int(length), int(smooth_k) if smooth_k else 1,
            int(smooth_d) if smooth_d else 3,
        )
        idx = close.index
        return _wrap(k, idx), _wrap(d, idx)

    @staticmethod
    def cci(source: pd.Series, length: int = 20) -> pd.Series:
        """Commodity Channel Index."""
        return _wrap(_nb._cci(_to_arr(source), int(length)), source.index)

    @staticmethod
    def mfi(source: pd.Series, high: pd.Series, low: pd.Series,
            close: pd.Series, volume: pd.Series,
            length: int = 14) -> pd.Series:
        """Money Flow Index."""
        length = int(length)
        typical = (high + low + close) / 3
        raw_mf = typical * volume
        delta = typical.diff()
        pos_mf = (raw_mf * (delta > 0)).rolling(length).sum()
        neg_mf = (raw_mf * (delta <= 0)).rolling(length).sum()
        ratio = pos_mf / neg_mf.replace(0, np.nan)
        return 100.0 - (100.0 / (1.0 + ratio))

    @staticmethod
    def cmo(source: pd.Series, length: int = 14) -> pd.Series:
        """Chande Momentum Oscillator."""
        length = int(length)
        delta = source.diff()
        gain = delta.clip(lower=0).rolling(length).sum()
        loss = (-delta).clip(lower=0).rolling(length).sum()
        return 100.0 * (gain - loss) / (gain + loss)

    @staticmethod
    def roc(source: pd.Series, length: int = 14) -> pd.Series:
        """Rate of Change (%)."""
        length = int(length)
        prev = source.shift(length)
        return 100.0 * (source - prev) / prev

    @staticmethod
    def tsi(source: pd.Series, short_length: int = 13,
            long_length: int = 25) -> pd.Series:
        """True Strength Index."""
        delta = source.diff()
        double_smooth = ta.ema(ta.ema(delta, long_length), short_length)
        double_smooth_abs = ta.ema(ta.ema(delta.abs(), long_length), short_length)
        return 100.0 * double_smooth / double_smooth_abs

    @staticmethod
    def mom(source: pd.Series, length: int = 10) -> pd.Series:
        """Momentum (price difference)."""
        return source.diff(int(length))

    @staticmethod
    def wpr(high: pd.Series, low: pd.Series, close: pd.Series,
            length: int = 14) -> pd.Series:
        """Williams %R."""
        length = int(length)
        hh = high.rolling(length).max()
        ll = low.rolling(length).min()
        return -100 * (hh - close) / (hh - ll)

    @staticmethod
    def percentrank(source: pd.Series, length: int = 20) -> pd.Series:
        """Percent Rank."""
        return _wrap(
            _nb._percentrank(_to_arr(source), int(length)), source.index,
        )

    # ──────────────────────────────────────────────────────────────────────
    #  Volatility
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series,
            length: int = 14) -> pd.Series:
        """Average True Range."""
        return _wrap(
            _nb._atr(_to_arr(high), _to_arr(low), _to_arr(close), int(length)),
            close.index,
        )

    @staticmethod
    def bb(source: pd.Series, length: int = 20,
           mult: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Bollinger Bands.  Returns (middle, upper, lower)."""
        length = int(length)
        middle = ta.sma(source, length)
        std = source.rolling(window=length).std()
        return middle, middle + mult * std, middle - mult * std

    @staticmethod
    def bbw(source: pd.Series, length: int = 20,
            mult: float = 2.0) -> pd.Series:
        """Bollinger Band Width."""
        middle, upper, lower = ta.bb(source, length, mult)
        return (upper - lower) / middle

    @staticmethod
    def kc(source: pd.Series, high: pd.Series, low: pd.Series,
           close: pd.Series, length: int = 20,
           mult: float = 1.5) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Keltner Channel.  Returns (middle, upper, lower)."""
        length = int(length)
        middle = ta.ema(source, length)
        atr_val = ta.atr(high, low, close, length)
        return middle, middle + mult * atr_val, middle - mult * atr_val

    @staticmethod
    def kcw(source: pd.Series, high: pd.Series, low: pd.Series,
            close: pd.Series, length: int = 20,
            mult: float = 1.5) -> pd.Series:
        """Keltner Channel Width."""
        middle, upper, lower = ta.kc(source, high, low, close, length, mult)
        return (upper - lower) / middle

    @staticmethod
    def dmi(high: pd.Series, low: pd.Series, close: pd.Series,
            di_length: int = 14, adx_smoothing: int = 14,
            ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Directional Movement Index.  Returns (+DI, -DI, ADX)."""
        plus_di, minus_di, adx = _nb._dmi(
            _to_arr(high), _to_arr(low), _to_arr(close),
            int(di_length), int(adx_smoothing),
        )
        idx = close.index
        return _wrap(plus_di, idx), _wrap(minus_di, idx), _wrap(adx, idx)

    @staticmethod
    def stdev(source: pd.Series, length: int = 20,
              biased: bool = True) -> pd.Series:
        """Standard deviation."""
        length = int(length)
        ddof = 0 if biased else 1
        return source.rolling(window=length).std(ddof=ddof)

    @staticmethod
    def sar(high: pd.Series, low: pd.Series,
            start: float = 0.02, inc: float = 0.02,
            max_val: float = 0.2) -> pd.Series:
        """Parabolic SAR."""
        return _wrap(
            _nb._sar(_to_arr(high), _to_arr(low), start, inc, max_val),
            high.index,
        )

    @staticmethod
    def cog(source: pd.Series, length: int = 10) -> pd.Series:
        """Center of Gravity."""
        return _wrap(_nb._cog(_to_arr(source), int(length)), source.index)

    # ──────────────────────────────────────────────────────────────────────
    #  Volume
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """On-Balance Volume."""
        direction = np.sign(close.diff()).fillna(0)
        return (volume * direction).cumsum()

    @staticmethod
    def accdist(high: pd.Series, low: pd.Series, close: pd.Series,
                volume: pd.Series) -> pd.Series:
        """Accumulation/Distribution."""
        mfm = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
        return (mfm * volume).cumsum()

    @staticmethod
    def pvt(close: pd.Series, volume: pd.Series) -> pd.Series:
        """Price Volume Trend."""
        return (volume * close.pct_change()).fillna(0).cumsum()

    @staticmethod
    def wad(high: pd.Series, low: pd.Series,
            close: pd.Series) -> pd.Series:
        """Williams Accumulation/Distribution."""
        prev_close = close.shift(1)
        ad = np.where(
            close > prev_close,
            close - np.minimum(low, prev_close),
            np.where(
                close < prev_close,
                close - np.maximum(high, prev_close),
                0.0,
            ),
        )
        return pd.Series(ad, index=close.index).cumsum()

    @staticmethod
    def vwap(high: pd.Series, low: pd.Series, close: pd.Series,
             volume: pd.Series) -> pd.Series:
        """Volume-Weighted Average Price (cumulative, session-based approximation)."""
        typical = (high + low + close) / 3
        return (typical * volume).cumsum() / volume.cumsum()

    # ──────────────────────────────────────────────────────────────────────
    #  Utility / Lookback
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def highest(source: pd.Series, length: int) -> pd.Series:
        return source.rolling(window=int(length)).max()

    @staticmethod
    def lowest(source: pd.Series, length: int) -> pd.Series:
        return source.rolling(window=int(length)).min()

    @staticmethod
    def change(source: pd.Series, length: int = 1) -> pd.Series:
        return source.diff(int(length))

    @staticmethod
    def median(source: pd.Series, length: int) -> pd.Series:
        return source.rolling(window=int(length)).median()

    @staticmethod
    def range_indicator(source: pd.Series, length: int) -> pd.Series:
        """Range (highest - lowest over period).
        Named range_indicator to avoid shadowing Python builtin."""
        length = int(length)
        return source.rolling(length).max() - source.rolling(length).min()

    @staticmethod
    def linreg(source: pd.Series, length: int,
               offset: int = 0) -> pd.Series:
        """Linear regression value."""
        return _wrap(
            _nb._linreg(_to_arr(source), int(length), int(offset)),
            source.index,
        )

    @staticmethod
    def rising(source: pd.Series, length: int) -> pd.Series:
        """True if source has risen for ``length`` consecutive bars."""
        length = int(length)
        diff = (source.diff() > 0).astype(float)
        return diff.rolling(length).sum() >= length

    @staticmethod
    def falling(source: pd.Series, length: int) -> pd.Series:
        """True if source has fallen for ``length`` consecutive bars."""
        length = int(length)
        diff = (source.diff() < 0).astype(float)
        return diff.rolling(length).sum() >= length

    @staticmethod
    def cum(source: pd.Series) -> pd.Series:
        """Cumulative sum."""
        return source.cumsum()

    # ──────────────────────────────────────────────────────────────────────
    #  Cross detection
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def crossover(a: pd.Series, b) -> pd.Series:
        """True on bars where *a* crosses **above** *b*."""
        if isinstance(b, (int, float)):
            b = pd.Series(b, index=a.index)
        return (a > b) & (a.shift(1) <= b.shift(1))

    @staticmethod
    def crossunder(a: pd.Series, b) -> pd.Series:
        """True on bars where *a* crosses **below** *b*."""
        if isinstance(b, (int, float)):
            b = pd.Series(b, index=a.index)
        return (a < b) & (a.shift(1) >= b.shift(1))

    @staticmethod
    def cross(a: pd.Series, b) -> pd.Series:
        """True on bars where *a* crosses *b* in either direction."""
        return ta.crossover(a, b) | ta.crossunder(a, b)

    # ──────────────────────────────────────────────────────────────────────
    #  Built-in helpers
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def nz(source: pd.Series, replacement: float = 0.0) -> pd.Series:
        """Replace NaN with *replacement* (PineScript ``nz()``)."""
        return source.fillna(replacement)


# ══════════════════════════════════════════════════════════════════════════
#  ta_fast — numpy-only API for the magnifier inner loop
# ══════════════════════════════════════════════════════════════════════════

class ta_fast:
    """Numpy-only indicator API — zero pandas overhead.

    Every method mirrors ``ta`` but takes/returns raw ``np.ndarray``
    instead of ``pd.Series``.  Used by ``_compute_fast`` in the magnifier
    inner loop where the per-call pandas wrapping cost dominates.
    """

    # ── Trend / Moving Averages ───────────────────────────────

    @staticmethod
    def sma(source: np.ndarray, length: int) -> np.ndarray:
        return _nb._sma(source, int(length))

    @staticmethod
    def ema(source: np.ndarray, length: int) -> np.ndarray:
        return _nb._ema(source, int(length))

    @staticmethod
    def rma(source: np.ndarray, length: int) -> np.ndarray:
        return _nb._rma(source, int(length))

    @staticmethod
    def wma(source: np.ndarray, length: int) -> np.ndarray:
        return _nb._wma(source, int(length))

    @staticmethod
    def vwma(source: np.ndarray, volume: np.ndarray, length: int) -> np.ndarray:
        length = int(length)
        sv = source * volume
        sv_sum = _nb._sma(sv, length) * length  # rolling sum via SMA * length
        v_sum = _nb._sma(volume, length) * length
        n = len(source)
        out = np.full(n, np.nan, dtype=np.float64)
        for i in range(length - 1, n):
            if v_sum[i] != 0.0:
                out[i] = sv_sum[i] / v_sum[i]
        return out

    @staticmethod
    def hma(source: np.ndarray, length: int) -> np.ndarray:
        length = int(length)
        half = max(1, length // 2)
        sqrt_len = max(1, int(np.sqrt(length)))
        wma_half = _nb._wma(source, half)
        wma_full = _nb._wma(source, length)
        diff = 2.0 * wma_half - wma_full
        return _nb._wma(diff, sqrt_len)

    @staticmethod
    def alma(source: np.ndarray, length: int, offset: float = 0.85,
             sigma: float = 6.0) -> np.ndarray:
        return _nb._alma(source, int(length), offset, sigma)

    @staticmethod
    def swma(source: np.ndarray) -> np.ndarray:
        return _nb._swma(source)

    @staticmethod
    def supertrend(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                   factor: float = 3.0, period: int = 10):
        return _nb._supertrend(high, low, close, float(factor), int(period))

    # ── Momentum ──────────────────────────────────────────────

    @staticmethod
    def rsi(source: np.ndarray, length: int = 14) -> np.ndarray:
        return _nb._rsi(source, int(length))

    @staticmethod
    def macd(source: np.ndarray, fast_length: int = 12,
             slow_length: int = 26, signal_length: int = 9):
        return _nb._macd(source, int(fast_length),
                         int(slow_length), int(signal_length))

    @staticmethod
    def stoch(close: np.ndarray, high: np.ndarray, low: np.ndarray,
              length: int = 14, smooth_k: int = 1, smooth_d: int = 3):
        return _nb._stoch(close, high, low, int(length),
                          int(smooth_k) if smooth_k else 1,
                          int(smooth_d) if smooth_d else 3)

    @staticmethod
    def cci(source: np.ndarray, length: int = 20) -> np.ndarray:
        return _nb._cci(source, int(length))

    @staticmethod
    def mfi(source: np.ndarray, high: np.ndarray, low: np.ndarray,
            close: np.ndarray, volume: np.ndarray,
            length: int = 14) -> np.ndarray:
        length = int(length)
        typical = (high + low + close) / 3.0
        raw_mf = typical * volume
        n = len(source)
        delta = np.empty(n, dtype=np.float64)
        delta[0] = np.nan
        for i in range(1, n):
            delta[i] = typical[i] - typical[i - 1]
        pos_mf = np.where(delta > 0, raw_mf, 0.0)
        neg_mf = np.where(delta <= 0, raw_mf, 0.0)
        pos_sum = _nb._sma(pos_mf, length) * length
        neg_sum = _nb._sma(neg_mf, length) * length
        out = np.full(n, np.nan, dtype=np.float64)
        for i in range(n):
            if not np.isnan(pos_sum[i]) and neg_sum[i] != 0.0:
                ratio = pos_sum[i] / neg_sum[i]
                out[i] = 100.0 - (100.0 / (1.0 + ratio))
        return out

    @staticmethod
    def cmo(source: np.ndarray, length: int = 14) -> np.ndarray:
        length = int(length)
        n = len(source)
        delta = np.empty(n, dtype=np.float64)
        delta[0] = np.nan
        for i in range(1, n):
            delta[i] = source[i] - source[i - 1]
        gain = np.where(delta > 0, delta, 0.0)
        loss = np.where(delta < 0, -delta, 0.0)
        gain[0] = np.nan
        loss[0] = np.nan
        gain_sum = _nb._sma(gain, length) * length
        loss_sum = _nb._sma(loss, length) * length
        out = np.full(n, np.nan, dtype=np.float64)
        for i in range(n):
            s = gain_sum[i] + loss_sum[i]
            if not np.isnan(s) and s != 0.0:
                out[i] = 100.0 * (gain_sum[i] - loss_sum[i]) / s
        return out

    @staticmethod
    def roc(source: np.ndarray, length: int = 14) -> np.ndarray:
        length = int(length)
        n = len(source)
        out = np.full(n, np.nan, dtype=np.float64)
        for i in range(length, n):
            if source[i - length] != 0.0:
                out[i] = 100.0 * (source[i] - source[i - length]) / source[i - length]
        return out

    @staticmethod
    def tsi(source: np.ndarray, short_length: int = 13,
            long_length: int = 25) -> np.ndarray:
        n = len(source)
        delta = np.empty(n, dtype=np.float64)
        delta[0] = np.nan
        for i in range(1, n):
            delta[i] = source[i] - source[i - 1]
        abs_delta = np.abs(delta)
        ds = _nb._ema(_nb._ema(delta, long_length), short_length)
        dsa = _nb._ema(_nb._ema(abs_delta, long_length), short_length)
        out = np.full(n, np.nan, dtype=np.float64)
        for i in range(n):
            if dsa[i] != 0.0 and not np.isnan(dsa[i]):
                out[i] = 100.0 * ds[i] / dsa[i]
        return out

    @staticmethod
    def mom(source: np.ndarray, length: int = 10) -> np.ndarray:
        length = int(length)
        n = len(source)
        out = np.full(n, np.nan, dtype=np.float64)
        for i in range(length, n):
            out[i] = source[i] - source[i - length]
        return out

    @staticmethod
    def wpr(high: np.ndarray, low: np.ndarray, close: np.ndarray,
            length: int = 14) -> np.ndarray:
        length = int(length)
        n = len(close)
        out = np.full(n, np.nan, dtype=np.float64)
        for i in range(length - 1, n):
            hh = high[i]
            ll = low[i]
            for j in range(i - length + 1, i):
                if high[j] > hh:
                    hh = high[j]
                if low[j] < ll:
                    ll = low[j]
            rng = hh - ll
            if rng != 0.0:
                out[i] = -100.0 * (hh - close[i]) / rng
        return out

    @staticmethod
    def percentrank(source: np.ndarray, length: int = 20) -> np.ndarray:
        return _nb._percentrank(source, int(length))

    # ── Volatility ────────────────────────────────────────────

    @staticmethod
    def atr(high: np.ndarray, low: np.ndarray, close: np.ndarray,
            length: int = 14) -> np.ndarray:
        return _nb._atr(high, low, close, int(length))

    @staticmethod
    def bb(source: np.ndarray, length: int = 20, mult: float = 2.0):
        length = int(length)
        middle = _nb._sma(source, length)
        n = len(source)
        upper = np.full(n, np.nan, dtype=np.float64)
        lower = np.full(n, np.nan, dtype=np.float64)
        for i in range(length - 1, n):
            s = 0.0
            for j in range(i - length + 1, i + 1):
                s += (source[j] - middle[i]) ** 2
            std = (s / (length - 1)) ** 0.5
            upper[i] = middle[i] + mult * std
            lower[i] = middle[i] - mult * std
        return middle, upper, lower

    @staticmethod
    def bbw(source: np.ndarray, length: int = 20,
            mult: float = 2.0) -> np.ndarray:
        middle, upper, lower = ta_fast.bb(source, length, mult)
        n = len(source)
        out = np.full(n, np.nan, dtype=np.float64)
        for i in range(n):
            if middle[i] != 0.0 and not np.isnan(middle[i]):
                out[i] = (upper[i] - lower[i]) / middle[i]
        return out

    @staticmethod
    def kc(source: np.ndarray, high: np.ndarray, low: np.ndarray,
           close: np.ndarray, length: int = 20, mult: float = 1.5):
        length = int(length)
        middle = _nb._ema(source, length)
        atr_val = _nb._atr(high, low, close, length)
        return middle, middle + mult * atr_val, middle - mult * atr_val

    @staticmethod
    def kcw(source: np.ndarray, high: np.ndarray, low: np.ndarray,
            close: np.ndarray, length: int = 20,
            mult: float = 1.5) -> np.ndarray:
        middle, upper, lower = ta_fast.kc(source, high, low, close, length, mult)
        n = len(source)
        out = np.full(n, np.nan, dtype=np.float64)
        for i in range(n):
            if middle[i] != 0.0 and not np.isnan(middle[i]):
                out[i] = (upper[i] - lower[i]) / middle[i]
        return out

    @staticmethod
    def dmi(high: np.ndarray, low: np.ndarray, close: np.ndarray,
            di_length: int = 14, adx_smoothing: int = 14):
        return _nb._dmi(high, low, close, int(di_length), int(adx_smoothing))

    @staticmethod
    def stdev(source: np.ndarray, length: int = 20,
              biased: bool = True) -> np.ndarray:
        length = int(length)
        n = len(source)
        out = np.full(n, np.nan, dtype=np.float64)
        ddof = 0 if biased else 1
        for i in range(length - 1, n):
            s = 0.0
            for j in range(i - length + 1, i + 1):
                s += source[j]
            mean = s / length
            ss = 0.0
            for j in range(i - length + 1, i + 1):
                ss += (source[j] - mean) ** 2
            out[i] = (ss / (length - ddof)) ** 0.5
        return out

    @staticmethod
    def sar(high: np.ndarray, low: np.ndarray,
            start: float = 0.02, inc: float = 0.02,
            max_val: float = 0.2) -> np.ndarray:
        return _nb._sar(high, low, start, inc, max_val)

    @staticmethod
    def cog(source: np.ndarray, length: int = 10) -> np.ndarray:
        return _nb._cog(source, int(length))

    # ── Volume ────────────────────────────────────────────────

    @staticmethod
    def obv(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        n = len(close)
        out = np.empty(n, dtype=np.float64)
        out[0] = 0.0
        for i in range(1, n):
            d = close[i] - close[i - 1]
            if d > 0:
                out[i] = out[i - 1] + volume[i]
            elif d < 0:
                out[i] = out[i - 1] - volume[i]
            else:
                out[i] = out[i - 1]
        return out

    @staticmethod
    def accdist(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                volume: np.ndarray) -> np.ndarray:
        n = len(close)
        out = np.empty(n, dtype=np.float64)
        s = 0.0
        for i in range(n):
            rng = high[i] - low[i]
            if rng != 0.0:
                mfm = ((close[i] - low[i]) - (high[i] - close[i])) / rng
                s += mfm * volume[i]
            out[i] = s
        return out

    @staticmethod
    def pvt(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        n = len(close)
        out = np.empty(n, dtype=np.float64)
        out[0] = 0.0
        for i in range(1, n):
            if close[i - 1] != 0.0:
                out[i] = out[i - 1] + volume[i] * (close[i] - close[i - 1]) / close[i - 1]
            else:
                out[i] = out[i - 1]
        return out

    @staticmethod
    def wad(high: np.ndarray, low: np.ndarray,
            close: np.ndarray) -> np.ndarray:
        n = len(close)
        out = np.empty(n, dtype=np.float64)
        out[0] = 0.0
        for i in range(1, n):
            if close[i] > close[i - 1]:
                ad = close[i] - min(low[i], close[i - 1])
            elif close[i] < close[i - 1]:
                ad = close[i] - max(high[i], close[i - 1])
            else:
                ad = 0.0
            out[i] = out[i - 1] + ad
        return out

    @staticmethod
    def vwap(high: np.ndarray, low: np.ndarray, close: np.ndarray,
             volume: np.ndarray) -> np.ndarray:
        typical = (high + low + close) / 3.0
        tv_cum = np.cumsum(typical * volume)
        v_cum = np.cumsum(volume)
        return tv_cum / v_cum

    # ── Utility / Lookback ────────────────────────────────────

    @staticmethod
    def highest(source: np.ndarray, length: int) -> np.ndarray:
        length = int(length)
        n = len(source)
        out = np.full(n, np.nan, dtype=np.float64)
        for i in range(length - 1, n):
            mx = source[i]
            for j in range(i - length + 1, i):
                if source[j] > mx:
                    mx = source[j]
            out[i] = mx
        return out

    @staticmethod
    def lowest(source: np.ndarray, length: int) -> np.ndarray:
        length = int(length)
        n = len(source)
        out = np.full(n, np.nan, dtype=np.float64)
        for i in range(length - 1, n):
            mn = source[i]
            for j in range(i - length + 1, i):
                if source[j] < mn:
                    mn = source[j]
            out[i] = mn
        return out

    @staticmethod
    def change(source: np.ndarray, length: int = 1) -> np.ndarray:
        length = int(length)
        n = len(source)
        out = np.full(n, np.nan, dtype=np.float64)
        for i in range(length, n):
            out[i] = source[i] - source[i - length]
        return out

    @staticmethod
    def median(source: np.ndarray, length: int) -> np.ndarray:
        length = int(length)
        n = len(source)
        out = np.full(n, np.nan, dtype=np.float64)
        for i in range(length - 1, n):
            window = np.sort(source[i - length + 1:i + 1])
            out[i] = window[length // 2] if length % 2 == 1 else (window[length // 2 - 1] + window[length // 2]) / 2.0
        return out

    @staticmethod
    def range_indicator(source: np.ndarray, length: int) -> np.ndarray:
        return ta_fast.highest(source, length) - ta_fast.lowest(source, length)

    @staticmethod
    def linreg(source: np.ndarray, length: int,
               offset: int = 0) -> np.ndarray:
        return _nb._linreg(source, int(length), int(offset))

    @staticmethod
    def rising(source: np.ndarray, length: int) -> np.ndarray:
        length = int(length)
        n = len(source)
        out = np.full(n, np.nan, dtype=np.float64)
        for i in range(length, n):
            count = 0
            for j in range(i - length + 1, i + 1):
                if source[j] > source[j - 1]:
                    count += 1
            out[i] = 1.0 if count >= length else 0.0
        return out

    @staticmethod
    def falling(source: np.ndarray, length: int) -> np.ndarray:
        length = int(length)
        n = len(source)
        out = np.full(n, np.nan, dtype=np.float64)
        for i in range(length, n):
            count = 0
            for j in range(i - length + 1, i + 1):
                if source[j] < source[j - 1]:
                    count += 1
            out[i] = 1.0 if count >= length else 0.0
        return out

    @staticmethod
    def cum(source: np.ndarray) -> np.ndarray:
        return np.cumsum(source)

    # ── Cross detection (returns np.ndarray of bool-like floats) ──

    @staticmethod
    def crossover(a: np.ndarray, b) -> np.ndarray:
        if isinstance(b, (int, float)):
            b_arr = np.full(len(a), b, dtype=np.float64)
        else:
            b_arr = b
        n = len(a)
        out = np.zeros(n, dtype=np.float64)
        for i in range(1, n):
            if a[i] > b_arr[i] and a[i - 1] <= b_arr[i - 1]:
                out[i] = 1.0
        return out

    @staticmethod
    def crossunder(a: np.ndarray, b) -> np.ndarray:
        if isinstance(b, (int, float)):
            b_arr = np.full(len(a), b, dtype=np.float64)
        else:
            b_arr = b
        n = len(a)
        out = np.zeros(n, dtype=np.float64)
        for i in range(1, n):
            if a[i] < b_arr[i] and a[i - 1] >= b_arr[i - 1]:
                out[i] = 1.0
        return out

    @staticmethod
    def cross(a: np.ndarray, b) -> np.ndarray:
        return ta_fast.crossover(a, b) + ta_fast.crossunder(a, b)

    # ── Built-in helpers ──────────────────────────────────────

    @staticmethod
    def nz(source: np.ndarray, replacement: float = 0.0) -> np.ndarray:
        out = source.copy()
        out[np.isnan(out)] = replacement
        return out
