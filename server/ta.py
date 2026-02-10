"""
Vectorized PineScript v6 ``ta.*`` indicators — pandas implementation.

Every method is a ``@staticmethod`` on the ``ta`` class.  Inputs and outputs
are ``pd.Series`` (or tuples of Series for multi-output indicators).

Indicators that PineScript accesses implicitly (e.g. ``ta.atr(14)`` uses
high/low/close internally) receive those columns as **explicit** arguments
here.  The code generator injects ``_high, _low, _close, _volume`` at
call sites.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np
import pandas as pd


class ta:
    """PineScript v6 ``ta.*`` indicator functions in pandas."""

    # ──────────────────────────────────────────────────────────────────────
    #  Trend / Moving Averages
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def sma(source: pd.Series, length: int) -> pd.Series:
        return source.rolling(window=int(length), min_periods=int(length)).mean()

    @staticmethod
    def ema(source: pd.Series, length: int) -> pd.Series:
        return source.ewm(span=int(length), adjust=False).mean()

    @staticmethod
    def rma(source: pd.Series, length: int) -> pd.Series:
        """Wilder's smoothing (used internally by RSI / ATR)."""
        return source.ewm(alpha=1.0 / int(length), adjust=False).mean()

    @staticmethod
    def wma(source: pd.Series, length: int) -> pd.Series:
        """Weighted moving average."""
        length = int(length)
        weights = np.arange(1, length + 1, dtype=float)
        return source.rolling(window=length).apply(
            lambda x: np.dot(x, weights) / weights.sum(), raw=True,
        )

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
        length = int(length)
        m = offset * (length - 1)
        s = length / sigma
        weights = np.array([np.exp(-((i - m) ** 2) / (2 * s * s))
                            for i in range(length)])
        weights /= weights.sum()
        return source.rolling(window=length).apply(
            lambda x: np.dot(x, weights), raw=True,
        )

    @staticmethod
    def swma(source: pd.Series) -> pd.Series:
        """Symmetric weighted moving average (fixed 4-bar)."""
        weights = np.array([1, 2, 2, 1], dtype=float)
        weights /= weights.sum()
        return source.rolling(window=4).apply(
            lambda x: np.dot(x, weights), raw=True,
        )

    @staticmethod
    def supertrend(high: pd.Series, low: pd.Series, close: pd.Series,
                   factor: float = 3.0, period: int = 10,
                   ) -> Tuple[pd.Series, pd.Series]:
        """SuperTrend indicator.  Returns (value, direction).
        direction: -1 = uptrend (bullish), 1 = downtrend (bearish)."""
        period = int(period)
        atr_val = ta.atr(high, low, close, period)
        hl2 = (high + low) / 2
        upper_band = hl2 + factor * atr_val
        lower_band = hl2 - factor * atr_val

        n = len(close)
        st = np.zeros(n)
        direction = np.ones(n)  # 1 = down, -1 = up

        ub = upper_band.values.copy()
        lb = lower_band.values.copy()
        cl = close.values

        for i in range(1, n):
            if np.isnan(ub[i]) or np.isnan(lb[i]):
                st[i] = np.nan
                direction[i] = direction[i - 1]
                continue
            # Adjust bands
            if ub[i] < ub[i - 1] or cl[i - 1] > ub[i - 1]:
                pass  # keep ub[i]
            else:
                ub[i] = ub[i - 1]
            if lb[i] > lb[i - 1] or cl[i - 1] < lb[i - 1]:
                pass  # keep lb[i]
            else:
                lb[i] = lb[i - 1]

            if direction[i - 1] == -1:  # was uptrend
                if cl[i] < lb[i]:
                    direction[i] = 1
                    st[i] = ub[i]
                else:
                    direction[i] = -1
                    st[i] = lb[i]
            else:  # was downtrend
                if cl[i] > ub[i]:
                    direction[i] = -1
                    st[i] = lb[i]
                else:
                    direction[i] = 1
                    st[i] = ub[i]

        idx = close.index
        return pd.Series(st, index=idx), pd.Series(direction, index=idx)

    # ──────────────────────────────────────────────────────────────────────
    #  Momentum
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def rsi(source: pd.Series, length: int = 14) -> pd.Series:
        delta = source.diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        avg_gain = ta.rma(gain, length)
        avg_loss = ta.rma(loss, length)
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    @staticmethod
    def macd(source: pd.Series, fast_length: int = 12,
             slow_length: int = 26, signal_length: int = 9,
             ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Returns (macd_line, signal_line, histogram)."""
        ema_fast = ta.ema(source, fast_length)
        ema_slow = ta.ema(source, slow_length)
        macd_line = ema_fast - ema_slow
        signal_line = ta.ema(macd_line, signal_length)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def stoch(close: pd.Series, high: pd.Series, low: pd.Series,
              length: int = 14) -> pd.Series:
        """Raw Stochastic %K (unsmoothed)."""
        length = int(length)
        lowest_low = low.rolling(length).min()
        highest_high = high.rolling(length).max()
        return 100 * (close - lowest_low) / (highest_high - lowest_low)

    @staticmethod
    def cci(source: pd.Series, length: int = 20) -> pd.Series:
        """Commodity Channel Index."""
        length = int(length)
        mean = source.rolling(length).mean()
        mad = source.rolling(length).apply(
            lambda x: np.mean(np.abs(x - np.mean(x))), raw=True,
        )
        return (source - mean) / (0.015 * mad)

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
        length = int(length)
        def _pctrank(window):
            return np.sum(window[-1] >= window[:-1]) / (len(window) - 1) * 100
        return source.rolling(length + 1).apply(_pctrank, raw=True)

    # ──────────────────────────────────────────────────────────────────────
    #  Volatility
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series,
            length: int = 14) -> pd.Series:
        """Average True Range."""
        tr = pd.concat([
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs(),
        ], axis=1).max(axis=1)
        return ta.rma(tr, length)

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
        di_length = int(di_length)
        adx_smoothing = int(adx_smoothing)

        up = high.diff()
        down = -low.diff()
        plus_dm = ((up > down) & (up > 0)).astype(float) * up
        minus_dm = ((down > up) & (down > 0)).astype(float) * down

        atr_val = ta.atr(high, low, close, di_length)
        plus_di = 100 * ta.rma(plus_dm, di_length) / atr_val
        minus_di = 100 * ta.rma(minus_dm, di_length) / atr_val

        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
        adx = ta.rma(dx, adx_smoothing)

        return plus_di, minus_di, adx

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
        n = len(high)
        h = high.values
        lo = low.values

        psar = np.full(n, np.nan)
        af = start
        trend = 1  # 1 = up, -1 = down
        ep = h[0]
        psar[0] = lo[0]

        for i in range(1, n):
            if np.isnan(h[i]) or np.isnan(lo[i]):
                psar[i] = psar[i - 1]
                continue

            prev_psar = psar[i - 1]
            if trend == 1:  # uptrend
                psar[i] = prev_psar + af * (ep - prev_psar)
                psar[i] = min(psar[i], lo[i - 1])
                if i >= 2:
                    psar[i] = min(psar[i], lo[i - 2])
                if lo[i] < psar[i]:  # reversal
                    trend = -1
                    psar[i] = ep
                    ep = lo[i]
                    af = start
                else:
                    if h[i] > ep:
                        ep = h[i]
                        af = min(af + inc, max_val)
            else:  # downtrend
                psar[i] = prev_psar + af * (ep - prev_psar)
                psar[i] = max(psar[i], h[i - 1])
                if i >= 2:
                    psar[i] = max(psar[i], h[i - 2])
                if h[i] > psar[i]:  # reversal
                    trend = 1
                    psar[i] = ep
                    ep = h[i]
                    af = start
                else:
                    if lo[i] < ep:
                        ep = lo[i]
                        af = min(af + inc, max_val)

        return pd.Series(psar, index=high.index)

    @staticmethod
    def cog(source: pd.Series, length: int = 10) -> pd.Series:
        """Center of Gravity."""
        length = int(length)
        weights = np.arange(1, length + 1, dtype=float)
        num = source.rolling(length).apply(
            lambda x: -np.dot(x, weights), raw=True,
        )
        denom = source.rolling(length).sum()
        return num / denom

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
        length = int(length)
        def _linreg(window):
            x = np.arange(len(window))
            coeffs = np.polyfit(x, window, 1)
            return np.polyval(coeffs, len(window) - 1 - offset)
        return source.rolling(length).apply(_linreg, raw=True)

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
