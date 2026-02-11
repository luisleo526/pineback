---
name: pinescript-compiler
description: Compile PineScript v6 strategies into vectorized Python functions via a tokenizer-parser-AST-codegen pipeline. Implements the 4-signal model and a TA indicator library. Use when building or modifying the PineScript compiler, adding technical indicators, or designing the signal interface between strategy logic and the backtest engine.
---

# PineScript Compiler

PineScript v6 → vectorized Python transpiler, with TA indicator library.

For system-wide architecture context, see [architecture.md](../architecture.md).

## The 4-Signal Model

Every compiled strategy produces exactly **4 boolean pd.Series**:

```python
def compute(df: pd.DataFrame, params: dict) -> tuple[
    pd.Series,  # long_entry
    pd.Series,  # long_exit
    pd.Series,  # short_entry
    pd.Series,  # short_exit
]: ...
```

This is the universal contract. The execution engine only understands these
four signals — it never sees strategy logic. Any definition method (PineScript,
visual builder, raw Python) must produce this 4-tuple.

Mapping from PineScript:

| PineScript | Signal |
|-----------|--------|
| `strategy.entry("Long", strategy.long)` in if-block | `long_entry` = the if-condition |
| `strategy.close("Long")` in if-block | `long_exit` = the if-condition |
| `strategy.entry("Short", strategy.short)` in if-block | `short_entry` = the if-condition |
| `strategy.close("Short")` in if-block | `short_exit` = the if-condition |

## Compiler Pipeline

```
PineScript → [Tokenizer] → [Parser] → [CodeGen] → exec() → compute function
```

### Tokenizer

PineScript-specific behaviors to handle:

- **Comment stripping:** `//` line comments (preserve `//` inside strings)
- **Continuation joining:** Lines with unbalanced parens join into one logical line:
  ```pine
  [a, b, c] = ta.macd(close,
      12, 26, 9)
  ```
- **Indent tracking:** PineScript uses indentation for if-blocks. Emit
  INDENT/DEDENT tokens like Python.

### Parser

Recursive descent. The AST needs to capture:

- `strategy()` declaration → name + settings (initial_capital, commission, slippage)
- `input.int/float/bool/string()` → parameter definitions (name, default, bounds)
- Assignments including tuple destructuring: `[a, b, c] = ta.macd(...)`
- `if` blocks containing `strategy.entry/close/exit` calls

### Code Generation: The Hard Part

The codegen translates PineScript to vectorized pandas Python. Key translations:

**Price builtins → DataFrame columns (prefix to avoid Python shadowing):**

| PineScript | Python |
|-----------|--------|
| `close` | `_df['close']` (aliased to `_close`) |
| `open` | `_df['open']` (aliased to `_open` — `open` is Python builtin) |
| `hlc3` | `(_high + _low + _close) / 3` |

**Implicit argument injection** — the most important translation:

PineScript's `ta.atr(14)` implicitly uses high/low/close. The generated
Python needs these explicit:

```python
IMPLICIT_ARGS = {
    "atr":        ("_high", "_low", "_close"),
    "supertrend": ("_high", "_low", "_close"),
    "sar":        ("_high", "_low"),
    "dmi":        ("_high", "_low", "_close"),
    "obv":        ("_close", "_volume"),
    "mfi":        ("_high", "_low", "_close", "_volume"),
    "vwap":       ("_high", "_low", "_close", "_volume"),
    # rsi, macd, sma, ema, etc.: source is explicit in PineScript
}
# ta.atr(14)  →  ta.atr(_high, _low, _close, 14)
# ta.rsi(close, 14)  →  ta.rsi(_close, 14)  (just price builtin substitution)
```

**Boolean operators:**

| PineScript | Python | Why |
|-----------|--------|-----|
| `a and b` | `(a) & (b)` | Series bitwise ops; parens for precedence |
| `a or b` | `(a) \| (b)` | `\|` not `or` for pandas |
| `not a` | `~(a)` | Bitwise NOT |

**Other translations:**

| PineScript | Python |
|-----------|--------|
| `math.abs(x)` | `np.abs(x)` |
| `nz(x)` | `x.fillna(0)` |
| `na(x)` | `x.isna()` |
| `[a, b, c] = f()` | `(a, b, c) = f()` |

**Signal return:** Wrap every condition with `.fillna(False)` — indicators
return NaN during warmup, and NaN must not become a True signal.

### exec() and Security

```python
namespace = {"ta": ta, "pd": pd, "np": np}
exec(generated_source, namespace)
compute_fn = namespace["_compute"]
```

The namespace deliberately excludes `os`, `sys`, `subprocess`. If accepting
PineScript from untrusted users, add sandboxing (RestrictedPython, subprocess
isolation, or WASM).

## Compiled Strategy Object

```python
@dataclass
class TransformedStrategy:
    name: str                       # From strategy("name", ...)
    inputs: dict[str, InputParam]   # {varName: IntInput(...), ...}
    compute: Callable               # (df, params) -> 4-tuple
    warmup: int                     # max(all_indicator_periods) * 2
    source_code: str                # Original PineScript
    generated_code: str             # Generated Python (debug)
    settings: dict                  # initial_capital, commission, slippage
```

**Warmup:** Scan all indicator periods and set `warmup = max(periods) * 2`.
Conservative — EMA technically needs infinite history but `2x` is practical.

## TA Indicator Library

All indicators should be static methods on a `ta` class, accept/return
`pd.Series`, and use vectorized ops (no Python loops). They must match
PineScript's output — verify against TradingView.

Categories to implement:

- **Trend:** sma, ema, wma, vwma, hma, rma, alma, swma
- **Momentum:** rsi, macd (returns 3-tuple), stoch, cci, mfi, roc, mom, wpr
- **Volatility:** atr, bb (returns 3-tuple), kc, supertrend, dmi
- **Volume:** obv, vwap
- **Utility:** crossover, crossunder, highest, lowest, change, rising, falling

Key implementations:

```python
class ta:
    @staticmethod
    def rsi(source, length):
        delta = source.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1.0/length, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0/length, adjust=False).mean()
        return 100.0 - (100.0 / (1.0 + avg_gain / avg_loss))

    @staticmethod
    def crossover(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))
```

**When adding a new indicator:** implement in `ta` class, add to
IMPLICIT_ARGS if PineScript calls it without explicit price args, then
verify output against TradingView.

## Supported PineScript Subset

**In scope:** `strategy()`, `input.*()`, variable assignments, tuple
destructuring, `ta.*` calls, boolean expressions, `if` blocks with
`strategy.entry/close/exit`, `math.*`, `nz()`, `na()`.

**Out of scope:** `for`/`while` (hard to vectorize), `var`/`varip`
(persistent state), `request.security()` (multi-TF), `plot()` (visual only),
user-defined functions, `array.*`/`matrix.*`.

## Pitfalls

| Pitfall | Prevention |
|---------|-----------|
| `and`/`or` on Series | Translate to `&`/`\|` with parens |
| NaN signals during warmup | `.fillna(False)` on all conditions |
| `open` shadows Python builtin | Prefix: `_open`, `_close`, etc. |
| Missing implicit args | Maintain IMPLICIT_ARGS table per indicator |
| Operator precedence `a & b \| c` | Always parenthesize each operand |
| `exec()` without sandboxing | Restrict namespace; sandbox for untrusted input |
