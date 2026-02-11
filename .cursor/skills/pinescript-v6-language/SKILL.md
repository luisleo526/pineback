---
name: pinescript-v6-language
description: Comprehensive PineScript v6 language reference for writing TradingView indicators and strategies. Covers syntax, execution model, type system, technical analysis functions, strategy commands, and best practices. Use when writing, reviewing, debugging, or explaining PineScript code, or when the user mentions PineScript, Pine Script, TradingView strategies, or .pine files.
---

# PineScript v6 Language Reference

## Execution Model

PineScript executes **bar-by-bar**, left to right. The script re-runs from top to bottom on every bar. Key implications:

- Variables are **re-declared** each bar unless prefixed with `var` (persists across bars) or `varip` (persists across ticks).
- Use `[]` history-referencing operator to access previous bar values: `close[1]` = previous bar's close.
- `ta.*` functions internally reference history; they must be called in the **global scope** on every bar to produce correct series.

### Historical vs Realtime

- **Historical bars**: script executes once per bar, values are final.
- **Realtime bar**: script executes on every tick; values may change until bar closes.
- `barstate.ishistory`, `barstate.isrealtime`, `barstate.islast`, `barstate.isconfirmed` detect execution context.

## Script Structure

Every script requires `//@version=6` and a declaration statement:

```pine
//@version=6
strategy("My Strategy", overlay=true, initial_capital=10000,
  default_qty_type=strategy.percent_of_equity, default_qty_value=100)
```

or for indicators:

```pine
//@version=6
indicator("My Indicator", overlay=true)
```

### Recommended Order

1. `//@version=6`
2. `indicator()` / `strategy()` / `library()` declaration
3. `import` statements
4. Constants (`SNAKE_CASE`)
5. `input.*()` declarations (suffix with `Input`)
6. Function declarations
7. Calculations
8. Strategy calls
9. Visuals (`plot`, `plotshape`, `bgcolor`, etc.)
10. Alerts

## Type System

### Primitive Types

| Type | Example | Notes |
|------|---------|-------|
| `int` | `14`, `0` | Integer values |
| `float` | `3.14`, `0.0` | Floating point |
| `bool` | `true`, `false` | Boolean |
| `string` | `"hello"` | String literals |
| `color` | `#FF0000`, `color.red` | `color.new(color.red, 50)` for transparency (0=opaque, 100=invisible) |

### Type Qualifiers (weakest to strongest)

`const` < `input` < `simple` < `series`

- `const`: compile-time literal (e.g., `"EMA"`)
- `input`: set once via `input.*()`, never changes
- `simple`: set on first bar, never changes (e.g., `syminfo.ticker`)
- `series`: can change every bar (e.g., `close`, `ta.rsi(close, 14)`)

A function expecting a weaker qualifier rejects a stronger one. E.g., `ta.sma(close, length)` requires `length` to be `simple int` — you cannot pass a `series int`.

### Special Value: `na`

- Represents "not available". Test with `na(x)` function, **never** `x == na`.
- Use `nz(x)` to replace `na` with 0, or `nz(x, replacement)`.

### Collections

- `array<type>`: dynamic array. Create with `array.new<float>()` or `array.from(1, 2, 3)`.
- `matrix<type>`: 2D matrix.
- `map<keyType, valueType>`: key-value store.

### User-Defined Types (UDT)

```pine
type bar
    float o = open
    float h = high
    float l = low
    float c = close
```

## Keywords and Control Flow

### Variables

```pine
x = close                    // re-declared each bar
var float x = 0.0            // persists across bars (initialized once)
varip int ticks = 0          // persists across ticks (realtime)
x := newValue                // reassignment (use := not =)
```

### Conditionals

```pine
// if/else
result = if close > open
    close
else
    open

// Ternary
result = close > open ? color.green : color.red

// switch (with expression)
ma = switch maType
    "EMA" => ta.ema(close, len)
    "SMA" => ta.sma(close, len)
    => ta.wma(close, len)    // default

// switch (without expression)
switch
    longCond  => strategy.entry("Long", strategy.long)
    shortCond => strategy.entry("Short", strategy.short)
```

### Loops

```pine
for i = 0 to 9
    sum += array.get(a, i)

for i = 0 to 9 by 2    // step

for [index, value] in myArray
    if value > 0
        count += 1

while counter > 0
    counter -= 1
```

### Functions

```pine
// User-defined function
myFunc(src, len) =>
    ta.sma(src, len)

// Multi-line (last expression is return value)
getSignal(fast, slow) =>
    bull = ta.crossover(fast, slow)
    bear = ta.crossunder(fast, slow)
    [bull, bear]    // tuple return

// Method syntax
method maintainArray(array<float> id, int maxSize, float value) =>
    id.push(value)
    if id.size() > maxSize
        id.shift()
```

### Logical Operators

`and`, `or`, `not` (not `&&`, `||`, `!`)

## Input Functions

```pine
length    = input.int(14, "Length", minval=1, maxval=200)
threshold = input.float(0.5, "Threshold", step=0.1)
useFilter = input.bool(true, "Use Filter")
maType    = input.string("EMA", "MA Type", options=["EMA", "SMA", "WMA"])
src       = input.source(close, "Source")
tf        = input.timeframe("D", "Timeframe")
```

## Built-in Variables (Most Used)

| Variable | Type | Description |
|----------|------|-------------|
| `open`, `high`, `low`, `close` | `series float` | OHLC prices |
| `volume` | `series float` | Bar volume |
| `time`, `time_close` | `series int` | Bar open/close time (UNIX ms) |
| `bar_index` | `series int` | Zero-based bar number |
| `hl2`, `hlc3`, `ohlc4` | `series float` | Price shortcuts |
| `syminfo.ticker` | `simple string` | Symbol name |
| `syminfo.tickerid` | `simple string` | Full ticker with exchange prefix |
| `timeframe.period` | `simple string` | Current timeframe |
| `strategy.position_size` | `series float` | Current position (>0 long, <0 short) |
| `strategy.equity` | `series float` | Current equity |

## Technical Analysis Functions

For the full TA function reference, see [reference/ta-functions.md](reference/ta-functions.md).

### Moving Averages

```pine
ta.sma(source, length)     // Simple MA
ta.ema(source, length)     // Exponential MA
ta.wma(source, length)     // Weighted MA
ta.rma(source, length)     // Wilder's smoothing (used in RSI)
ta.hma(source, length)     // Hull MA
ta.alma(source, length, offset, sigma)  // Arnaud Legoux MA
ta.vwma(source, length)    // Volume-weighted MA
```

### Oscillators

```pine
ta.rsi(source, length)                             // RSI (0-100)
ta.stoch(close, high, low, length)                  // Stochastic (0-100)
[macdLine, signal, hist] = ta.macd(src, fast, slow, signal)
ta.cci(source, length)                              // CCI
ta.mfi(hlc3, length)                                // Money Flow Index
ta.mom(source, length)                              // Momentum
ta.roc(source, length)                              // Rate of Change
ta.cmo(source, length)                              // Chande Momentum
ta.tsi(source, shortLen, longLen)                    // True Strength Index
ta.wpr(length)                                       // Williams %R
```

### Volatility / Trend

```pine
ta.atr(length)                                       // Average True Range
ta.tr                                                 // True Range (variable)
[middle, upper, lower] = ta.bb(src, length, mult)    // Bollinger Bands
[middle, upper, lower] = ta.kc(src, length, mult)    // Keltner Channels
[supertrend, direction] = ta.supertrend(factor, atrPeriod)
[diplus, diminus, adx] = ta.dmi(diLen, adxSmoothing)
ta.sar(start, inc, max)                               // Parabolic SAR
```

### Crossover / Comparison

```pine
ta.crossover(source1, source2)    // true when src1 crosses above src2
ta.crossunder(source1, source2)   // true when src1 crosses below src2
ta.cross(source1, source2)        // true on any cross
ta.highest(source, length)        // Highest value in lookback
ta.lowest(source, length)         // Lowest value in lookback
ta.change(source, length)         // Difference from length bars ago
ta.rising(source, length)         // True if rising for length bars
ta.falling(source, length)        // True if falling for length bars
```

## Writing Strategies

For complete strategy patterns and examples, see [reference/strategy-patterns.md](reference/strategy-patterns.md).

### Strategy Declaration

```pine
strategy("Name", overlay=true,
  initial_capital    = 10000,
  default_qty_type   = strategy.percent_of_equity,
  default_qty_value  = 100,
  commission_type    = strategy.commission.percent,
  commission_value   = 0.1,
  slippage           = 2,
  pyramiding         = 0,          // max entries in same direction
  calc_on_every_tick = false)
```

### Order Commands

```pine
// Entry
strategy.entry("Long", strategy.long)
strategy.entry("Short", strategy.short)

// Entry with stop/limit
strategy.entry("Long", strategy.long, stop=high, limit=low)

// Close by ID
strategy.close("Long")

// Close all
strategy.close_all()

// Exit with TP/SL
strategy.exit("Exit Long", from_entry="Long",
  profit = 100,       // ticks
  loss   = 50,        // ticks
  trail_points = 50,
  trail_offset = 20)

// Exit with price levels
strategy.exit("Exit", "Long",
  limit = entryPrice * 1.05,   // 5% TP
  stop  = entryPrice * 0.98)   // 2% SL
```

### Standard Strategy Template

```pine
//@version=6
strategy("Strategy Name", overlay=true, initial_capital=10000,
  default_qty_type=strategy.percent_of_equity, default_qty_value=100)

// === Inputs ===
fastLen = input.int(12, "Fast Length", minval=1)
slowLen = input.int(26, "Slow Length", minval=1)

// === Indicators ===
fastMA = ta.ema(close, fastLen)
slowMA = ta.ema(close, slowLen)

// === Signal Conditions ===
longEntryCondition  = ta.crossover(fastMA, slowMA)
longExitCondition   = ta.crossunder(fastMA, slowMA)
shortEntryCondition = ta.crossunder(fastMA, slowMA)
shortExitCondition  = ta.crossover(fastMA, slowMA)

// === Strategy Execution ===
if longEntryCondition
    strategy.entry("Long", strategy.long)
if longExitCondition
    strategy.close("Long")
if shortEntryCondition
    strategy.entry("Short", strategy.short)
if shortExitCondition
    strategy.close("Short")

// === Visuals ===
plot(fastMA, "Fast MA", color.blue)
plot(slowMA, "Slow MA", color.red)
```

## Plotting & Visuals

```pine
plot(series, title, color, linewidth, style)
plotshape(condition, style=shape.triangleup, location=location.belowbar, color=color.green)
plotchar(condition, char="★", location=location.abovebar)
bgcolor(condition ? color.new(color.green, 90) : na)
hline(level, title, color, linestyle)
fill(plot1, plot2, color)
```

### Plot Styles
`plot.style_line`, `plot.style_histogram`, `plot.style_columns`, `plot.style_area`, `plot.style_circles`, `plot.style_cross`, `plot.style_stepline`

## Common Pitfalls

1. **Variable resets every bar** — Use `var` to persist across bars.
2. **Series vs simple error** — `ta.sma(close, length)` requires `length` as `simple int`, not `series int`. Inputs and literals are fine; runtime-computed values may not be.
3. **Comparing with `na`** — Use `na(x)`, never `x == na`.
4. **History reference on bar 0** — `close[1]` is `na` on the first bar.
5. **`ta.*` functions in local scope** — Call TA functions in the global scope to ensure they execute on every bar.
6. **Repainting** — Functions using `barstate.isrealtime` or `request.security` without `lookahead=barmerge.lookahead_off` may repaint.
7. **Max 40 `request.security()` calls** — Each unique call counts toward the limit.
8. **Loop timeout** — Loops exceeding 500ms per bar cause a runtime error.

## Reference Files (Self-Contained)

All reference files are in this skill's `reference/` directory. No external dependencies.

### Quick References

| File | Content | When to read |
|------|---------|--------------|
| `reference/syntax-quick-ref.md` | Types, operators, variable declarations, colors, strings, annotations, enums, imports | Syntax lookup |
| `reference/strategy-patterns.md` | 6 reusable strategy templates with TP/SL, filters, multi-indicator logic | Writing a new strategy |
| `reference/ta-functions.md` | All `ta.*` function signatures, return types, and usage notes | Any TA function |

### Function References (by Namespace)

| File | Content | When to read |
|------|---------|--------------|
| `reference/functions-strategy.md` | `strategy.entry()`, `.exit()`, `.close()`, `.order()`, `.risk.*`, trade inspection (`.closedtrades.*`, `.opentrades.*`), all strategy variables and constants | Strategy orders, exits, risk management |
| `reference/functions-request.md` | `request.security()`, `.security_lower_tf()`, `.financial()`, `.economic()`, `.dividends()`, `.earnings()`, `.splits()`, `.seed()`, `.currency_rate()`, timeframe string format, non-repainting pattern | Multi-timeframe data, external data |
| `reference/functions-general.md` | `math.*` (arithmetic, trig, constants), `str.*` (formatting, search, manipulation), `input.*` (all input types), `color.*`, `alert()`, `ticker.*`, `runtime.*`, type casting, utility functions (`na`, `nz`, `timestamp`, time extraction) | Math, strings, inputs, colors, alerts, utilities |
| `reference/functions-collections.md` | `array.*` (creation, access, search, transform, aggregation), `map.*` (CRUD, keys/values), `matrix.*` (access, modification, linear algebra, boolean tests) | Arrays, maps, matrices |
| `reference/functions-drawing.md` | `plot()`, `plotshape()`, `plotchar()`, `plotcandle()`, `bgcolor()`, `barcolor()`, `hline()`, `fill()`, `line.*`, `label.*`, `box.*`, `table.*`, `polyline.*`, `linefill.*`, `chart.point.*`, drawing limits | Plotting, drawing, chart visuals |

### Concepts, Errors & Best Practices

| File | Content | When to read |
|------|---------|--------------|
| `reference/concepts-and-errors.md` | Execution model (bar-by-bar, `var`/`varip`, history `[]`, realtime), repainting, timeframe strings, UDTs & objects, methods, common error messages with fixes, script limitations table, style guide summary, debugging tips | "Why does my variable reset?", error messages, repainting, UDTs, debugging, style guide |
