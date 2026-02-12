#!/usr/bin/env python3
"""
Correctness test: verify _compute_fast (numpy-only) produces
identical signals to _compute (pandas) for various strategies.
"""

import sys
import numpy as np
import pandas as pd

sys.path.insert(0, ".")

from server.ta import ta, ta_fast


def make_ohlcv_df(n=500, seed=42):
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


def test_strategy(name, pine_code, df, params=None):
    """Compile a strategy, run both compute and compute_fast, compare signals."""
    from server.pine.tokens import Tokenizer
    from server.pine.parser import Parser
    from server.pine.codegen import CodeGenerator

    tokens = Tokenizer(pine_code).tokenize()
    ast = Parser(tokens).parse()
    strategy = CodeGenerator(ast, source=pine_code).generate()

    p = params or {k: v.default for k, v in strategy.inputs.items()}

    # Run pandas-based compute
    le, lx, se, sx = strategy.compute(df, p)
    signals_pd = (
        le.values.astype(bool),
        lx.values.astype(bool),
        se.values.astype(bool),
        sx.values.astype(bool),
    )

    # Run numpy-based compute_fast
    assert strategy.compute_fast is not None, f"{name}: compute_fast is None!"

    o = np.ascontiguousarray(df["open"].values, dtype=np.float64)
    h = np.ascontiguousarray(df["high"].values, dtype=np.float64)
    l = np.ascontiguousarray(df["low"].values, dtype=np.float64)
    c = np.ascontiguousarray(df["close"].values, dtype=np.float64)
    v = np.ascontiguousarray(df["volume"].values, dtype=np.float64)

    # Check last-bar signal matches for each bar position
    mismatches = 0
    checked = 0
    warmup = strategy.warmup
    for i in range(warmup, len(df)):
        sl = slice(max(0, i - warmup * 3), i + 1)
        fast_le, fast_lx, fast_se, fast_sx = strategy.compute_fast(
            o[sl], h[sl], l[sl], c[sl], v[sl], p,
        )
        # Compare last-bar signal
        pd_le = bool(signals_pd[0][i])
        pd_lx = bool(signals_pd[1][i])
        pd_se = bool(signals_pd[2][i])
        pd_sx = bool(signals_pd[3][i])

        if (fast_le != pd_le or fast_lx != pd_lx or
                fast_se != pd_se or fast_sx != pd_sx):
            if mismatches < 3:
                print(f"    Mismatch at bar {i}: "
                      f"pd=({pd_le},{pd_lx},{pd_se},{pd_sx}) "
                      f"fast=({fast_le},{fast_lx},{fast_se},{fast_sx})")
            mismatches += 1
        checked += 1

    if mismatches == 0:
        print(f"  OK   {name}: {checked} bars checked, all match")
        return True
    else:
        print(f"  FAIL {name}: {mismatches}/{checked} mismatches")
        return False


def main():
    df = make_ohlcv_df(500)

    macd_pine = """
//@version=6
strategy("MACD Crossover", overlay=true)
fastPeriod = input.int(12, "Fast Period")
slowPeriod = input.int(26, "Slow Period")
signalPeriod = input.int(9, "Signal Period")
[macdLine, signalLine, _] = ta.macd(close, fastPeriod, slowPeriod, signalPeriod)
longEntryCondition = ta.crossover(macdLine, signalLine)
longExitCondition = ta.crossunder(macdLine, signalLine)
if longEntryCondition
    strategy.entry("Long", strategy.long)
if longExitCondition
    strategy.close("Long")
"""

    rsi_pine = """
//@version=6
strategy("RSI Strategy", overlay=true)
length = input.int(14, "RSI Length")
overbought = input.int(70, "Overbought")
oversold = input.int(30, "Oversold")
rsiVal = ta.rsi(close, length)
longEntryCondition = ta.crossover(rsiVal, oversold)
longExitCondition = ta.crossunder(rsiVal, overbought)
if longEntryCondition
    strategy.entry("Long", strategy.long)
if longExitCondition
    strategy.close("Long")
"""

    supertrend_pine = """
//@version=6
strategy("SuperTrend", overlay=true)
factor = input.float(3.0, "Factor")
period = input.int(10, "Period")
[stValue, stDir] = ta.supertrend(factor, period)
longEntryCondition = ta.crossunder(stDir, 0)
longExitCondition = ta.crossover(stDir, 0)
shortEntryCondition = ta.crossover(stDir, 0)
shortExitCondition = ta.crossunder(stDir, 0)
if longEntryCondition
    strategy.entry("Long", strategy.long)
if longExitCondition
    strategy.close("Long")
if shortEntryCondition
    strategy.entry("Short", strategy.short)
if shortExitCondition
    strategy.close("空單")
"""

    bb_pine = """
//@version=6
strategy("Bollinger Bands", overlay=true)
length = input.int(20, "Length")
mult = input.float(2.0, "Multiplier")
[middle, upper, lower] = ta.bb(close, length, mult)
longEntryCondition = ta.crossover(close, lower)
longExitCondition = ta.crossunder(close, upper)
if longEntryCondition
    strategy.entry("Long", strategy.long)
if longExitCondition
    strategy.close("Long")
"""

    passed = 0
    failed = 0

    print("=" * 60)
    print("  compute vs compute_fast correctness test")
    print("=" * 60)

    for name, pine in [
        ("MACD Crossover", macd_pine),
        ("RSI Strategy", rsi_pine),
        ("SuperTrend", supertrend_pine),
        ("Bollinger Bands", bb_pine),
    ]:
        try:
            if test_strategy(name, pine, df):
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ERROR {name}: {e}")
            import traceback; traceback.print_exc()
            failed += 1

    print("=" * 60)
    print(f"  SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
