"""
Numba-compiled kernels for ``ta.py`` indicator hot-paths.

Three categories of optimization:

1. **Loop-based indicators** (SuperTrend, SAR): pure Python for-loops
   over numpy arrays → @njit gives 50-200x speedup.

2. **rolling.apply with lambdas** (WMA, ALMA, SWMA, CCI, COG,
   percentrank, linreg): pandas rolling().apply() has ~10µs per-call
   Python overhead → @njit sliding-window loops eliminate it entirely.

3. **Core EMA/RMA** used by RSI, ATR, MACD, DMI, etc.: pandas ewm()
   is already fast, but the @njit version avoids pandas Series creation
   overhead (significant when called on small windows in magnifier mode).

Every kernel operates on raw float64 numpy arrays and returns raw arrays.
The ``ta`` class wraps them back into ``pd.Series``.

All kernels use ``@njit(cache=True)`` so JIT cost is paid once.
"""

from __future__ import annotations

import math

import numba as nb
import numpy as np

# ──────────────────────────────────────────────────────────────────────────
#  Exponential moving averages
# ──────────────────────────────────────────────────────────────────────────


@nb.njit(cache=True)
def _ema(src: np.ndarray, span: int) -> np.ndarray:
    """EMA (span-based, adjust=False)."""
    n = len(src)
    out = np.empty(n, dtype=np.float64)
    alpha = 2.0 / (span + 1.0)
    out[0] = src[0]
    for i in range(1, n):
        if math.isnan(src[i]):
            out[i] = out[i - 1]
        elif math.isnan(out[i - 1]):
            out[i] = src[i]
        else:
            out[i] = alpha * src[i] + (1.0 - alpha) * out[i - 1]
    return out


@nb.njit(cache=True)
def _rma(src: np.ndarray, length: int) -> np.ndarray:
    """Wilder's smoothing (alpha = 1/length, adjust=False)."""
    n = len(src)
    out = np.empty(n, dtype=np.float64)
    alpha = 1.0 / length
    out[0] = src[0]
    for i in range(1, n):
        if math.isnan(src[i]):
            out[i] = out[i - 1]
        elif math.isnan(out[i - 1]):
            out[i] = src[i]
        else:
            out[i] = alpha * src[i] + (1.0 - alpha) * out[i - 1]
    return out


# ──────────────────────────────────────────────────────────────────────────
#  SMA
# ──────────────────────────────────────────────────────────────────────────


@nb.njit(cache=True)
def _sma(src: np.ndarray, length: int) -> np.ndarray:
    """Simple moving average — handles NaN-containing inputs correctly.

    Matches pandas ``rolling(length, min_periods=length).mean()``:
    a window produces a value only when all ``length`` elements are non-NaN.
    """
    n = len(src)
    out = np.full(n, np.nan, dtype=np.float64)
    if n < length:
        return out
    for i in range(length - 1, n):
        s = 0.0
        valid = True
        for j in range(i - length + 1, i + 1):
            if math.isnan(src[j]):
                valid = False
                break
            s += src[j]
        if valid:
            out[i] = s / length
    return out


# ──────────────────────────────────────────────────────────────────────────
#  Weighted moving averages
# ──────────────────────────────────────────────────────────────────────────


@nb.njit(cache=True)
def _wma(src: np.ndarray, length: int) -> np.ndarray:
    """Weighted moving average — replaces rolling().apply(lambda)."""
    n = len(src)
    out = np.full(n, np.nan, dtype=np.float64)
    # Precompute weights
    denom = length * (length + 1) / 2.0
    for i in range(length - 1, n):
        s = 0.0
        for j in range(length):
            s += src[i - length + 1 + j] * (j + 1)
        out[i] = s / denom
    return out


@nb.njit(cache=True)
def _alma(src: np.ndarray, length: int, offset: float,
          sigma: float) -> np.ndarray:
    """Arnaud Legoux moving average — replaces rolling().apply(lambda)."""
    n = len(src)
    out = np.full(n, np.nan, dtype=np.float64)
    m = offset * (length - 1)
    s = length / sigma
    # Precompute weights
    weights = np.empty(length, dtype=np.float64)
    w_sum = 0.0
    for k in range(length):
        w = math.exp(-((k - m) ** 2) / (2.0 * s * s))
        weights[k] = w
        w_sum += w
    for k in range(length):
        weights[k] /= w_sum

    for i in range(length - 1, n):
        v = 0.0
        for j in range(length):
            v += src[i - length + 1 + j] * weights[j]
        out[i] = v
    return out


@nb.njit(cache=True)
def _swma(src: np.ndarray) -> np.ndarray:
    """Symmetric weighted moving average (fixed 4-bar)."""
    n = len(src)
    out = np.full(n, np.nan, dtype=np.float64)
    # weights: 1/6, 2/6, 2/6, 1/6
    for i in range(3, n):
        out[i] = (src[i - 3] + 2.0 * src[i - 2] +
                  2.0 * src[i - 1] + src[i]) / 6.0
    return out


# ──────────────────────────────────────────────────────────────────────────
#  Center of Gravity
# ──────────────────────────────────────────────────────────────────────────


@nb.njit(cache=True)
def _cog(src: np.ndarray, length: int) -> np.ndarray:
    """Center of Gravity — replaces rolling().apply(lambda)."""
    n = len(src)
    out = np.full(n, np.nan, dtype=np.float64)
    for i in range(length - 1, n):
        num = 0.0
        denom = 0.0
        for j in range(length):
            v = src[i - length + 1 + j]
            num += -v * (j + 1)
            denom += v
        if denom != 0.0:
            out[i] = num / denom
    return out


# ──────────────────────────────────────────────────────────────────────────
#  CCI (mean absolute deviation is the slow part)
# ──────────────────────────────────────────────────────────────────────────


@nb.njit(cache=True)
def _cci(src: np.ndarray, length: int) -> np.ndarray:
    """Commodity Channel Index — full computation in one pass."""
    n = len(src)
    out = np.full(n, np.nan, dtype=np.float64)
    for i in range(length - 1, n):
        # Mean
        s = 0.0
        for j in range(length):
            s += src[i - length + 1 + j]
        mean = s / length
        # Mean absolute deviation
        mad = 0.0
        for j in range(length):
            mad += abs(src[i - length + 1 + j] - mean)
        mad /= length
        if mad != 0.0:
            out[i] = (src[i] - mean) / (0.015 * mad)
    return out


# ──────────────────────────────────────────────────────────────────────────
#  Percent Rank
# ──────────────────────────────────────────────────────────────────────────


@nb.njit(cache=True)
def _percentrank(src: np.ndarray, length: int) -> np.ndarray:
    """Percent rank — replaces rolling().apply(lambda)."""
    n = len(src)
    out = np.full(n, np.nan, dtype=np.float64)
    for i in range(length, n):
        count = 0
        for j in range(i - length, i):
            if src[i] >= src[j]:
                count += 1
        out[i] = count / length * 100.0
    return out


# ──────────────────────────────────────────────────────────────────────────
#  Linear Regression
# ──────────────────────────────────────────────────────────────────────────


@nb.njit(cache=True)
def _linreg(src: np.ndarray, length: int, offset: int) -> np.ndarray:
    """Linear regression value — replaces rolling().apply(polyfit)."""
    n = len(src)
    out = np.full(n, np.nan, dtype=np.float64)
    # Precompute x stats (same for every window)
    x_mean = (length - 1.0) / 2.0
    x_var = 0.0
    for k in range(length):
        x_var += (k - x_mean) ** 2

    for i in range(length - 1, n):
        y_mean = 0.0
        for j in range(length):
            y_mean += src[i - length + 1 + j]
        y_mean /= length

        cov = 0.0
        for j in range(length):
            cov += (j - x_mean) * (src[i - length + 1 + j] - y_mean)

        slope = cov / x_var if x_var != 0.0 else 0.0
        intercept = y_mean - slope * x_mean
        out[i] = intercept + slope * (length - 1 - offset)
    return out


# ──────────────────────────────────────────────────────────────────────────
#  ATR (True Range + RMA in one pass)
# ──────────────────────────────────────────────────────────────────────────


@nb.njit(cache=True)
def _atr(high: np.ndarray, low: np.ndarray, close: np.ndarray,
         length: int) -> np.ndarray:
    """ATR — fused true-range + RMA to avoid intermediate Series."""
    n = len(high)
    tr = np.empty(n, dtype=np.float64)
    tr[0] = high[0] - low[0]
    for i in range(1, n):
        hl = high[i] - low[i]
        hc = abs(high[i] - close[i - 1])
        lc = abs(low[i] - close[i - 1])
        tr[i] = max(hl, max(hc, lc))
    return _rma(tr, length)


# ──────────────────────────────────────────────────────────────────────────
#  RSI (fused delta → RMA → ratio in one pass)
# ──────────────────────────────────────────────────────────────────────────


@nb.njit(cache=True)
def _rsi(src: np.ndarray, length: int) -> np.ndarray:
    """RSI — fused computation avoids 5 intermediate Series.

    Matches pandas: ``delta = source.diff()`` (NaN at index 0),
    ``gain = delta.clip(lower=0)`` (NaN stays NaN),
    then ``rma(gain, length)`` seeds from NaN at index 0.
    """
    n = len(src)
    out = np.full(n, np.nan, dtype=np.float64)

    gain = np.empty(n, dtype=np.float64)
    loss = np.empty(n, dtype=np.float64)
    # diff() at index 0 is NaN → clip preserves NaN
    gain[0] = np.nan
    loss[0] = np.nan
    for i in range(1, n):
        d = src[i] - src[i - 1]
        gain[i] = d if d > 0 else 0.0
        loss[i] = -d if d < 0 else 0.0

    avg_gain = _rma(gain, length)
    avg_loss = _rma(loss, length)

    for i in range(n):
        if math.isnan(avg_gain[i]) or math.isnan(avg_loss[i]):
            out[i] = np.nan
        elif avg_loss[i] == 0.0:
            out[i] = 100.0 if avg_gain[i] > 0 else np.nan
        else:
            rs = avg_gain[i] / avg_loss[i]
            out[i] = 100.0 - (100.0 / (1.0 + rs))
    return out


# ──────────────────────────────────────────────────────────────────────────
#  SuperTrend
# ──────────────────────────────────────────────────────────────────────────


@nb.njit(cache=True)
def _supertrend(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                factor: float, period: int):
    """SuperTrend — the biggest win: Python loop → native loop."""
    n = len(close)
    atr_val = _atr(high, low, close, period)
    hl2 = np.empty(n, dtype=np.float64)
    for i in range(n):
        hl2[i] = (high[i] + low[i]) / 2.0

    ub = np.empty(n, dtype=np.float64)
    lb = np.empty(n, dtype=np.float64)
    for i in range(n):
        ub[i] = hl2[i] + factor * atr_val[i]
        lb[i] = hl2[i] - factor * atr_val[i]

    st = np.zeros(n, dtype=np.float64)
    direction = np.ones(n, dtype=np.float64)

    for i in range(1, n):
        if math.isnan(ub[i]) or math.isnan(lb[i]):
            st[i] = np.nan
            direction[i] = direction[i - 1]
            continue

        # Adjust bands
        if not (ub[i] < ub[i - 1] or close[i - 1] > ub[i - 1]):
            ub[i] = ub[i - 1]
        if not (lb[i] > lb[i - 1] or close[i - 1] < lb[i - 1]):
            lb[i] = lb[i - 1]

        if direction[i - 1] == -1.0:  # was uptrend
            if close[i] < lb[i]:
                direction[i] = 1.0
                st[i] = ub[i]
            else:
                direction[i] = -1.0
                st[i] = lb[i]
        else:  # was downtrend
            if close[i] > ub[i]:
                direction[i] = -1.0
                st[i] = lb[i]
            else:
                direction[i] = 1.0
                st[i] = ub[i]

    return st, direction


# ──────────────────────────────────────────────────────────────────────────
#  Parabolic SAR
# ──────────────────────────────────────────────────────────────────────────


@nb.njit(cache=True)
def _sar(high: np.ndarray, low: np.ndarray,
         start: float, inc: float, max_val: float) -> np.ndarray:
    """Parabolic SAR — Python loop → native loop."""
    n = len(high)
    psar = np.full(n, np.nan, dtype=np.float64)
    af = start
    trend = 1  # 1 = up, -1 = down
    ep = high[0]
    psar[0] = low[0]

    for i in range(1, n):
        if math.isnan(high[i]) or math.isnan(low[i]):
            psar[i] = psar[i - 1]
            continue

        prev_psar = psar[i - 1]
        if trend == 1:  # uptrend
            psar[i] = prev_psar + af * (ep - prev_psar)
            psar[i] = min(psar[i], low[i - 1])
            if i >= 2:
                psar[i] = min(psar[i], low[i - 2])
            if low[i] < psar[i]:
                trend = -1
                psar[i] = ep
                ep = low[i]
                af = start
            else:
                if high[i] > ep:
                    ep = high[i]
                    af = min(af + inc, max_val)
        else:  # downtrend
            psar[i] = prev_psar + af * (ep - prev_psar)
            psar[i] = max(psar[i], high[i - 1])
            if i >= 2:
                psar[i] = max(psar[i], high[i - 2])
            if high[i] > psar[i]:
                trend = 1
                psar[i] = ep
                ep = high[i]
                af = start
            else:
                if low[i] < ep:
                    ep = low[i]
                    af = min(af + inc, max_val)

    return psar


# ──────────────────────────────────────────────────────────────────────────
#  DMI (+DI, -DI, ADX) — fused
# ──────────────────────────────────────────────────────────────────────────


@nb.njit(cache=True)
def _dmi(high: np.ndarray, low: np.ndarray, close: np.ndarray,
         di_length: int, adx_smoothing: int):
    """DMI — fused computation avoids many intermediate Series.

    Matches pandas: ``high.diff()`` and ``-low.diff()`` are NaN at
    index 0, and ``0.0 * NaN = NaN`` in pandas, so plus_dm[0] and
    minus_dm[0] must be NaN to seed the RMA identically.
    """
    n = len(high)

    # Directional movement — NaN at index 0 (matches diff())
    plus_dm = np.empty(n, dtype=np.float64)
    minus_dm = np.empty(n, dtype=np.float64)
    plus_dm[0] = np.nan
    minus_dm[0] = np.nan
    for i in range(1, n):
        up = high[i] - high[i - 1]
        down = low[i - 1] - low[i]
        if up > down and up > 0:
            plus_dm[i] = up
        else:
            plus_dm[i] = 0.0
        if down > up and down > 0:
            minus_dm[i] = down
        else:
            minus_dm[i] = 0.0

    atr_val = _atr(high, low, close, di_length)
    sm_plus = _rma(plus_dm, di_length)
    sm_minus = _rma(minus_dm, di_length)

    plus_di = np.full(n, np.nan, dtype=np.float64)
    minus_di = np.full(n, np.nan, dtype=np.float64)
    dx = np.full(n, np.nan, dtype=np.float64)

    for i in range(n):
        if atr_val[i] != 0.0 and not math.isnan(atr_val[i]):
            if not math.isnan(sm_plus[i]):
                plus_di[i] = 100.0 * sm_plus[i] / atr_val[i]
            if not math.isnan(sm_minus[i]):
                minus_di[i] = 100.0 * sm_minus[i] / atr_val[i]
            if not math.isnan(plus_di[i]) and not math.isnan(minus_di[i]):
                s = plus_di[i] + minus_di[i]
                if s != 0.0:
                    dx[i] = 100.0 * abs(plus_di[i] - minus_di[i]) / s

    adx = _rma(dx, adx_smoothing)
    return plus_di, minus_di, adx


# ──────────────────────────────────────────────────────────────────────────
#  MACD (fused: 2 EMAs + signal EMA)
# ──────────────────────────────────────────────────────────────────────────


@nb.njit(cache=True)
def _macd(src: np.ndarray, fast_length: int, slow_length: int,
          signal_length: int):
    """MACD — three EMA calls fused, avoids intermediate Series."""
    ema_fast = _ema(src, fast_length)
    ema_slow = _ema(src, slow_length)
    n = len(src)
    macd_line = np.empty(n, dtype=np.float64)
    for i in range(n):
        macd_line[i] = ema_fast[i] - ema_slow[i]
    signal_line = _ema(macd_line, signal_length)
    histogram = np.empty(n, dtype=np.float64)
    for i in range(n):
        histogram[i] = macd_line[i] - signal_line[i]
    return macd_line, signal_line, histogram


# ──────────────────────────────────────────────────────────────────────────
#  Stochastic
# ──────────────────────────────────────────────────────────────────────────


@nb.njit(cache=True)
def _stoch(close: np.ndarray, high: np.ndarray, low: np.ndarray,
           length: int, smooth_k: int, smooth_d: int):
    """Stochastic oscillator — rolling min/max + SMA smoothing."""
    n = len(close)
    raw_k = np.full(n, np.nan, dtype=np.float64)

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
            raw_k[i] = 100.0 * (close[i] - ll) / rng

    k = _sma(raw_k, smooth_k) if smooth_k > 1 else raw_k
    d = _sma(k, smooth_d)
    return k, d
