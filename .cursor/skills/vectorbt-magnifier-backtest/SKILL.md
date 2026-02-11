---
name: vectorbt-magnifier-backtest
description: Execute signal-based backtests with vectorbt Portfolio.from_signals(), including the magnifier technique for realistic intra-bar execution on higher timeframes. Use when running a trading strategy against historical data, extracting performance metrics, or improving backtest realism beyond bar-close fills.
---

# VectorBT Magnifier Backtest

Signal-based backtesting with vectorbt, plus the magnifier technique for
realistic intra-bar execution on higher timeframes.

For system-wide architecture context, see [architecture.md](../architecture.md).

## The Bar-Close Problem

Standard backtesting on higher timeframes fills at bar close:

```
4h bar: [Open $50K → High $52K → Low $48.5K → Close $51.2K]
                                                      ^
                                              Signal triggers, fill at $51.2K
```

But the MACD crossover may have occurred 2 hours in at $49.8K. The error
grows with timeframe: negligible on 1m, $1K+ on 4h, $5K+ on daily (BTC).

## Standard Mode

One vectorized call — fast but assumes bar-close fills:

```python
le, lx, se, sx = strategy.compute(df, params)
portfolio = vbt.Portfolio.from_signals(
    close=df["close"], entries=le, exits=lx,
    short_entries=se, short_exits=sx,
    init_cash=capital, fees=fees, slippage=slippage,
    freq=timeframe_freq,
)
```

Use for: 1m data, parameter sweeps, quick screening.

## Magnifier Mode

### Concept

For each chart bar, iterate sub-bars at finer resolution, progressively
building a "forming" OHLCV bar. Run the strategy at each tick. Record the
signal at the **exact sub-bar where it first triggers**, not at bar close.

```
Chart bar (4h):    [====================================]
Magnifier (15m):   [==|==|==|==|==|==|==|==|==|==|==|==|==|==|==|==]
                             ^
                             Signal triggers at tick 4 → fill at tick 4's close
```

### Dynamic Resolution

Target ~10 sub-bars per chart bar (max ~16):

```python
TF_MINUTES = {"1m":1, "3m":3, "5m":5, "15m":15, "30m":30, "1h":60, "4h":240, "1d":1440}
VALID_RESOLUTIONS = [1, 3, 5, 15, 30, 60, 240]

def pick_magnifier_resolution(chart_tf, target_ticks=10):
    chart_min = TF_MINUTES[chart_tf]
    if chart_min <= 1: return "1m"
    max_ticks = int(target_ticks * 1.6)
    best, best_dist = "1m", float("inf")
    for res in VALID_RESOLUTIONS:
        if res >= chart_min or chart_min % res != 0: continue
        ticks = chart_min // res
        if ticks > max_ticks: continue
        if abs(ticks - target_ticks) < best_dist:
            best_dist = abs(ticks - target_ticks)
            best = minutes_to_tf(res)
    return best
```

Result: 5m→1m(5), 1h→5m(12), 4h→15m(16), 1d→1h(24).

### Algorithm

```python
def run_magnified(df_1m, chart_tf, strategy, params, capital, fees, slippage):
    df_chart = resample_ohlcv(df_1m, chart_tf)
    mag_tf = pick_magnifier_resolution(chart_tf)
    df_mag = resample_ohlcv(df_1m, mag_tf)

    # Signal arrays at magnifier resolution
    n = len(df_mag)
    long_entries  = np.zeros(n, dtype=bool)
    long_exits    = np.zeros(n, dtype=bool)
    short_entries = np.zeros(n, dtype=bool)
    short_exits   = np.zeros(n, dtype=bool)

    in_long, in_short = False, False
    warmup = strategy.warmup
    td = TF_TIMEDELTA[chart_tf]

    for bar_idx in range(warmup, len(df_chart)):
        bar_start = df_chart.index[bar_idx]
        bar_end = bar_start + td

        # Magnifier ticks within this chart bar
        mag_start = df_mag.index.searchsorted(bar_start, side="left")
        mag_end   = df_mag.index.searchsorted(bar_end,   side="left")
        if mag_start >= mag_end: continue

        # Completed chart-TF bars as indicator context
        completed = df_chart.iloc[max(0, bar_idx - warmup*3):bar_idx]

        # Progressive forming bar
        forming_open = df_mag["open"].iloc[mag_start]
        forming_high, forming_low, forming_vol = -np.inf, np.inf, 0.0

        for pos in range(mag_start, mag_end):
            forming_high  = max(forming_high, df_mag["high"].iloc[pos])
            forming_low   = min(forming_low,  df_mag["low"].iloc[pos])
            forming_close = df_mag["close"].iloc[pos]
            forming_vol  += df_mag["volume"].iloc[pos]

            # Window = completed bars + forming bar
            forming = pd.DataFrame({
                "open": [forming_open], "high": [forming_high],
                "low": [forming_low], "close": [forming_close],
                "volume": [forming_vol],
            }, index=[df_mag.index[pos]])
            window = pd.concat([completed, forming])

            le, lx, se, sx = strategy.compute(window, params)

            # Record signal at exact sub-bar, then break
            if not in_long and bool(le.iloc[-1]):
                long_entries[pos] = True; in_long = True; break
            if in_long and bool(lx.iloc[-1]):
                long_exits[pos] = True; in_long = False; break
            if not in_short and bool(se.iloc[-1]):
                short_entries[pos] = True; in_short = True; break
            if in_short and bool(sx.iloc[-1]):
                short_exits[pos] = True; in_short = False; break

    # KEY: portfolio uses magnifier-resolution close prices, not chart-TF
    return vbt.Portfolio.from_signals(
        close=df_mag["close"],
        entries=pd.Series(long_entries, index=df_mag.index),
        exits=pd.Series(long_exits, index=df_mag.index),
        short_entries=pd.Series(short_entries, index=df_mag.index),
        short_exits=pd.Series(short_exits, index=df_mag.index),
        init_cash=capital, fees=fees, slippage=slippage,
        freq=timeframe_to_freq(mag_tf),  # mag_tf, NOT chart_tf
    )
```

**Requirement:** 1m base data must be available. If not, fall back to
standard mode.

## Result Extraction

Extract from `vbt.Portfolio` into a JSON-serializable structure:

```python
def extract_result(pf):
    stats = pf.stats()

    # Equity curve — sample to ~1000 points
    equity = pf.value()
    step = max(1, len(equity) // 1000)
    equity_curve = [{"timestamp": ts.isoformat(), "value": round(float(v), 2)}
                    for ts, v in equity.iloc[::step].items()]

    # Trades
    trades = [{"direction": r["Direction"], "entry_time": str(r["Entry Timestamp"]),
               "exit_time": str(r["Exit Timestamp"]), "pnl": round(float(r["PnL"]), 2),
               "return_pct": round(float(r["Return"]) * 100, 4)}
              for _, r in pf.trades.records_readable.iterrows()]

    return {
        "total_return_pct": safe_float(stats.get("Total Return [%]")),
        "sharpe_ratio": safe_float(stats.get("Sharpe Ratio")),
        "max_drawdown_pct": safe_float(stats.get("Max Drawdown [%]")),
        "total_trades": int(stats.get("Total Trades", 0)),
        "win_rate_pct": safe_float(stats.get("Win Rate [%]")),
        "profit_factor": safe_float(stats.get("Profit Factor")),
        "equity_curve": equity_curve,
        "trades": trades,
    }

def safe_float(val):
    if val is None: return None
    f = float(val)
    return None if (np.isnan(f) or np.isinf(f)) else f
```

**NaN → None:** Many stats return NaN when undefined (Sharpe with zero
variance, Profit Factor with no losing trades). Always `safe_float()` before
JSON serialization.

## Performance

| Config | Speed | Fill Realism |
|--------|-------|-------------|
| Standard 1m | Fast | Excellent |
| Standard 4h | Very fast | Poor |
| Magnifier 4h | Moderate (~10K compute calls for 1000 bars) | Good (15m fills) |
| Magnifier 1d | Moderate | Good (1h fills) |

Skip magnifier for: 1m data, param sweeps, initial screening.

## Pitfalls

| Pitfall | Prevention |
|---------|-----------|
| No warmup skip | Skip first `warmup` bars in magnifier loop |
| No position state tracking | Track `in_long`/`in_short`; avoid duplicate entries |
| Portfolio uses chart-TF close | Use `df_mag["close"]` — that's the whole point |
| Wrong `freq` param | Use mag_tf freq in magnifier mode (affects Sharpe annualization) |
| No `break` after signal | One signal per chart bar; break after recording |
| NaN in signals | `.fillna(False)` before passing to vectorbt |
| Huge equity curve | Sample to ~1000 points before storing |
