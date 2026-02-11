# PineScript v6 — Technical Analysis Functions Reference

All functions in the `ta.*` namespace. Signatures show the most common overload.

## Moving Averages

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `ta.sma` | `(source, length)` | `float` | Simple Moving Average |
| `ta.ema` | `(source, length)` | `float` | Exponential MA (alpha = 2/(length+1)) |
| `ta.wma` | `(source, length)` | `float` | Weighted MA (linear weights) |
| `ta.rma` | `(source, length)` | `float` | Wilder's smoothing (alpha = 1/length), used in RSI |
| `ta.hma` | `(source, length)` | `float` | Hull MA |
| `ta.alma` | `(source, length, offset, sigma)` | `float` | Arnaud Legoux MA |
| `ta.swma` | `(source)` | `float` | Symmetrically Weighted MA, fixed length 4 |
| `ta.vwma` | `(source, length)` | `float` | Volume-Weighted MA |
| `ta.linreg` | `(source, length, offset)` | `float` | Linear regression curve |

## Oscillators

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `ta.rsi` | `(source, length)` | `float` | Relative Strength Index (0–100) |
| `ta.stoch` | `(source, high, low, length)` | `float` | Stochastic (0–100) |
| `ta.cci` | `(source, length)` | `float` | Commodity Channel Index |
| `ta.mfi` | `(series, length)` | `float` | Money Flow Index (0–100) |
| `ta.mom` | `(source, length)` | `float` | Momentum: `source - source[length]` |
| `ta.roc` | `(source, length)` | `float` | Rate of Change (%) |
| `ta.cmo` | `(source, length)` | `float` | Chande Momentum Oscillator |
| `ta.tsi` | `(source, short_length, long_length)` | `float` | True Strength Index (−1 to 1) |
| `ta.wpr` | `(length)` | `float` | Williams %R |
| `ta.cog` | `(source, length)` | `float` | Center of Gravity |
| `ta.rci` | `(source, length)` | `float` | Rank Correlation Index (−100 to 100) |

## MACD

```pine
[macdLine, signalLine, histLine] = ta.macd(source, fastlen, slowlen, siglen)
```

- `macdLine`: EMA(fast) - EMA(slow)
- `signalLine`: EMA of macdLine
- `histLine`: macdLine - signalLine

## Bollinger Bands / Keltner Channels

```pine
[middle, upper, lower] = ta.bb(source, length, mult)
[middle, upper, lower] = ta.kc(source, length, mult)  // uses ATR
```

| Function | Returns |
|----------|---------|
| `ta.bbw(source, length, mult)` | BB Width (%) |
| `ta.kcw(source, length, mult)` | KC Width (%) |

## Volatility & Range

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `ta.atr` | `(length)` | `float` | Average True Range |
| `ta.tr` | (variable) | `float` | True Range: `max(high-low, abs(high-close[1]), abs(low-close[1]))` |
| `ta.tr` | `(handle_na)` | `float` | TR with na handling option |
| `ta.stdev` | `(source, length)` | `float` | Standard deviation |
| `ta.variance` | `(source, length)` | `float` | Variance |
| `ta.dev` | `(source, length)` | `float` | Mean absolute deviation |
| `ta.range` | `(source, length)` | `float` | Max − min over period |

## Trend Indicators

```pine
[supertrend, direction] = ta.supertrend(factor, atrPeriod)
// direction: -1 = up trend, 1 = down trend
```

```pine
[diplus, diminus, adx] = ta.dmi(diLength, adxSmoothing)
```

```pine
ta.sar(start, increment, maximum)  // Parabolic SAR
```

## Crossover & State Detection

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `ta.crossover` | `(source1, source2)` | `bool` | `true` when src1 crosses above src2 |
| `ta.crossunder` | `(source1, source2)` | `bool` | `true` when src1 crosses below src2 |
| `ta.cross` | `(source1, source2)` | `bool` | `true` on any cross |
| `ta.rising` | `(source, length)` | `bool` | Source rising for length bars |
| `ta.falling` | `(source, length)` | `bool` | Source falling for length bars |
| `ta.change` | `(source, length)` | varies | Difference from length bars ago (bool source returns direction change) |

## Extremes & Lookback

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `ta.highest` | `(source, length)` | `float` | Highest value in lookback |
| `ta.lowest` | `(source, length)` | `float` | Lowest value in lookback |
| `ta.highestbars` | `(source, length)` | `int` | Offset to highest bar (negative) |
| `ta.lowestbars` | `(source, length)` | `int` | Offset to lowest bar (negative) |
| `ta.max` | `(source)` | `float` | All-time high of source |
| `ta.min` | `(source)` | `float` | All-time low of source |
| `ta.median` | `(source, length)` | `float` | Median value |
| `ta.mode` | `(source, length)` | `float` | Most frequent value |
| `ta.percentrank` | `(source, length)` | `float` | Percent rank |
| `ta.percentile_nearest_rank` | `(source, length, percentage)` | `float` | Percentile (nearest rank) |
| `ta.percentile_linear_interpolation` | `(source, length, percentage)` | `float` | Percentile (interpolated) |

## Pivots

```pine
ta.pivothigh(source, leftbars, rightbars)   // returns price or na
ta.pivotlow(source, leftbars, rightbars)    // returns price or na
ta.pivot_point_levels(type, anchor)         // returns array<float> [P, R1, S1, R2, S2, ...]
```

Types for `ta.pivot_point_levels`: `"Traditional"`, `"Fibonacci"`, `"Woodie"`, `"Classic"`, `"DM"`, `"Camarilla"`

## Cumulative & Historical

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `ta.cum` | `(source)` | `float` | Cumulative sum since chart start |
| `ta.barssince` | `(condition)` | `int` | Bars since condition was last true |
| `ta.valuewhen` | `(condition, source, occurrence)` | varies | Source value when condition was true (nth occurrence) |
| `ta.correlation` | `(source1, source2, length)` | `float` | Correlation coefficient |

## VWAP

```pine
ta.vwap                                         // variable: VWAP using hlc3
ta.vwap(source)                                 // function: VWAP of custom source
[vwap, upper, lower] = ta.vwap(source, anchor, stdevMult)  // with bands
```

## Volume Indicators (Variables)

| Variable | Description |
|----------|-------------|
| `ta.accdist` | Accumulation/Distribution |
| `ta.obv` | On Balance Volume |
| `ta.pvt` | Price-Volume Trend |
| `ta.vwap` | Volume Weighted Average Price |
| `ta.wad` | Williams Accumulation/Distribution |
| `ta.wvad` | Williams Variable A/D |
| `ta.nvi` | Negative Volume Index |
| `ta.pvi` | Positive Volume Index |
| `ta.iii` | Intraday Intensity Index |
| `ta.tr` | True Range |

## Important Notes

1. **`length` must be `simple int`** — you cannot pass a `series int` (runtime-computed) as the length parameter to most `ta.*` functions. Use `input.int()` or literal values.
2. **Call in global scope** — `ta.*` functions maintain internal state. They must execute on every bar to produce correct results. Calling inside an `if` block that doesn't execute on every bar produces incorrect series.
3. **`na` handling** — most functions ignore `na` values in the source series and calculate on non-na values. Exceptions: `ta.change`, `ta.linreg`, `ta.swma` include `na` in calculations.
4. **Repainting** — `ta.barssince`, `ta.valuewhen`, and `ta.pivothigh`/`ta.pivotlow` can cause repainting when used with realtime data.
