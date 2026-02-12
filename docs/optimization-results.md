# Performance Optimization Results

Summary of all optimizations applied to the PineBack backtesting engine.

## 1. Numba JIT Indicator Acceleration

Replaced all pure-pandas `ta.py` indicator implementations with `@njit`-compiled kernels in `_numba_kernels.py`. The pandas wrappers now delegate to native-compiled numpy loops.

### Benchmark: Pandas vs Numba (median of multiple runs, JIT warmup excluded)

#### N=500 (magnifier window size — called thousands of times per backtest)

| Indicator | Pandas (ms) | Numba (ms) | Speedup |
|-----------|-------------|------------|---------|
| SMA(20) | 0.040 | 0.019 | 2.1x |
| EMA(20) | 0.032 | 0.015 | 2.2x |
| RMA(14) | 0.030 | 0.014 | 2.0x |
| WMA(20) | 0.819 | 0.018 | 45.4x |
| ALMA(20) | 0.357 | 0.017 | 20.6x |
| SWMA | 0.357 | 0.015 | 23.5x |
| RSI(14) | 0.500 | 0.017 | 29.9x |
| MACD | 0.130 | 0.044 | 3.0x |
| ATR(14) | 0.425 | 0.018 | 24.0x |
| SuperTrend | 1.748 | 0.033 | 53.7x |
| SAR | 1.093 | 0.018 | 61.0x |
| CCI(20) | 3.365 | 0.023 | 145.8x |
| COG(10) | 0.429 | 0.016 | 26.5x |
| PercentRank(20) | 1.495 | 0.022 | 69.1x |
| LinReg(20) | 13.568 | 0.024 | 555.7x |
| DMI(14,14) | 0.965 | 0.046 | 20.8x |
| Stoch(14,1,3) | 0.187 | 0.032 | 5.9x |

#### N=5,000 (typical chart)

| Indicator | Pandas (ms) | Numba (ms) | Speedup |
|-----------|-------------|------------|---------|
| WMA(20) | 8.215 | 0.060 | 136.3x |
| SWMA | 3.348 | 0.021 | 160.1x |
| SuperTrend | 12.055 | 0.069 | 174.3x |
| SAR | 10.455 | 0.026 | 397.0x |
| CCI(20) | 34.557 | 0.109 | 317.3x |
| LinReg(20) | 137.916 | 0.107 | 1,286.4x |

#### N=50,000 (large dataset)

| Indicator | Pandas (ms) | Numba (ms) | Speedup |
|-----------|-------------|------------|---------|
| SWMA | 32.719 | 0.073 | 449.0x |
| SuperTrend | 118.447 | 0.404 | 292.9x |
| SAR | 106.067 | 0.188 | 563.7x |
| CCI(20) | 326.083 | 0.991 | 329.1x |
| PercentRank(20) | 161.760 | 0.425 | 380.8x |
| LinReg(20) | 1,390.853 | 0.967 | 1,437.6x |

### Why the speedups vary

- **100-1,400x**: Indicators that used `rolling().apply(lambda)` or Python for-loops (LinReg, CCI, SAR, SuperTrend, PercentRank, WMA, SWMA, ALMA). Per-element Python interpreter overhead eliminated entirely.
- **5-30x**: Already-vectorized pandas indicators that benefit from fused computation (RSI, ATR, DMI, COG) — no intermediate Series allocation.
- **2-7x**: Indicators where pandas already uses optimized C code internally (SMA, EMA, RMA, MACD, Stoch). Win comes from avoiding Series construction overhead.

### Correctness

All 17 indicators verified identical to the original pandas implementation across 500, 5,000, and 50,000 bars. Maximum observed difference: 3.29e-11 (CCI at 50K bars) — well within IEEE 754 floating-point precision.

---

## 2. compute_fast: Zero-Pandas Magnifier Loop

Added a second code path (`_compute_fast`) that operates entirely on numpy arrays, eliminating all pandas DataFrame/Series overhead from the magnifier inner loop.

### Architecture

- `ta_fast` class in `ta.py` — mirrors every `ta` method but takes/returns raw `np.ndarray`
- Codegen emits `_compute_fast(open, high, low, close, volume, params) -> (bool, bool, bool, bool)` alongside `_compute`
- Magnifier loop auto-selects the fast path when available

### Benchmark: compute vs compute_fast

MACD Crossover on 300-bar window, 1,000 iterations:

| Path | Per-call | Speedup |
|------|----------|---------|
| `compute` (pandas DataFrame) | 0.616 ms | baseline |
| `compute_fast` (numpy arrays) | 0.143 ms | **4.3x** |

### Magnifier impact estimate

For a 2-month 15m backtest with magnifier (~23,400 sub-bar calls):

- Before: ~14.4 seconds (0.616ms x 23,400)
- After: ~3.3 seconds (0.143ms x 23,400)

### Correctness

Verified identical signals between `compute` and `compute_fast` for MACD Crossover, RSI Strategy, SuperTrend, and Bollinger Bands across 290-450 bars each.

---

## 3. Template Strategy Signal Validation

All 12 template strategies tested on real SPY data (1h bars, 2021-03-01 to 2021-05-01, 308 bars).

### Results (after parameter tuning)

| Strategy | Trades | Return % | Status |
|----------|:------:|:--------:|--------|
| ATR Trailing Stop | 9 | +1.89% | OK |
| Bollinger Band Breakout | 10 | -3.00% | OK |
| DMI ADX | 11 | -8.19% | OK |
| EMA SMA Cross | 10 | +3.52% | OK |
| KC BB Squeeze | 13 | -3.82% | OK |
| MA Ribbon | 13 | +1.25% | OK |
| MACD Crossover | 28 | -8.74% | OK |
| Multi Momentum | 7 | +2.57% | OK |
| OBV Volume | 19 | +1.25% | OK |
| RSI Mean Reversion | 6 | +9.54% | OK |
| Stochastic RSI Combo | 63 | -22.53% | OK |
| SuperTrend | 8 | +2.96% | OK |

### Fixes Applied

| Template | Problem | Fix |
|----------|---------|-----|
| `rsi_mean_reversion.json` | RSI 30/70 thresholds too extreme for 1h trending data (1 entry in 2 months) | Changed defaults to 35/65 |
| `kc_squeeze.json` | "Squeeze AND breakout" condition nearly impossible on short windows (0 entries) | Changed to "BB expanded outside KC AND price above/below KC band" |
| `dmi_adx.json` | ADX threshold 25 too high for DI crossover combo (2 entries) | Lowered to 20 |
