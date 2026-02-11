# PineScript v6 — Strategy Patterns

## Strategy Declaration Options

```pine
strategy("Name",
  overlay            = true,        // plot on price chart
  initial_capital    = 10000,
  default_qty_type   = strategy.percent_of_equity,  // or strategy.fixed, strategy.cash
  default_qty_value  = 100,
  commission_type    = strategy.commission.percent,
  commission_value   = 0.1,
  slippage           = 2,           // ticks
  pyramiding         = 0,           // 0 = no pyramiding
  calc_on_every_tick = false,
  process_orders_on_close = false,
  margin_long        = 100,         // 100 = no margin
  margin_short       = 100,
  max_bars_back      = 500)
```

### Quantity Types

| Type | Description |
|------|-------------|
| `strategy.percent_of_equity` | % of current equity |
| `strategy.fixed` | Fixed number of contracts/shares |
| `strategy.cash` | Fixed cash amount |

---

## Pattern 1: Simple MA Crossover (Long/Short)

```pine
//@version=6
strategy("MA Crossover", overlay=true, initial_capital=10000,
  default_qty_type=strategy.percent_of_equity, default_qty_value=100)

fastLen = input.int(10, "Fast Length", minval=1)
slowLen = input.int(30, "Slow Length", minval=1)

fastMA = ta.ema(close, fastLen)
slowMA = ta.ema(close, slowLen)

longEntry  = ta.crossover(fastMA, slowMA)
shortEntry = ta.crossunder(fastMA, slowMA)

if longEntry
    strategy.entry("Long", strategy.long)
if shortEntry
    strategy.entry("Short", strategy.short)

plot(fastMA, "Fast", color.blue)
plot(slowMA, "Slow", color.red)
```

---

## Pattern 2: RSI Mean Reversion with TP/SL

```pine
//@version=6
strategy("RSI Mean Reversion", overlay=true, initial_capital=10000,
  default_qty_type=strategy.percent_of_equity, default_qty_value=100)

rsiLen     = input.int(14, "RSI Period")
overbought = input.int(70, "Overbought")
oversold   = input.int(30, "Oversold")
tpPercent  = input.float(5.0, "Take Profit %") / 100
slPercent  = input.float(2.0, "Stop Loss %") / 100

myRSI = ta.rsi(close, rsiLen)

longEntry  = myRSI < oversold
shortEntry = myRSI > overbought

if longEntry
    strategy.entry("Long", strategy.long)
    strategy.exit("TP/SL Long", "Long",
      limit = close * (1 + tpPercent),
      stop  = close * (1 - slPercent))

if shortEntry
    strategy.entry("Short", strategy.short)
    strategy.exit("TP/SL Short", "Short",
      limit = close * (1 - tpPercent),
      stop  = close * (1 + slPercent))
```

---

## Pattern 3: MACD + Signal Filter

```pine
//@version=6
strategy("MACD Filtered", overlay=true, initial_capital=10000,
  default_qty_type=strategy.percent_of_equity, default_qty_value=100)

fastLen   = input.int(12, "MACD Fast")
slowLen   = input.int(26, "MACD Slow")
sigLen    = input.int(9, "Signal Length")
maFilter  = input.int(200, "Trend Filter MA")

[macdLine, signalLine, hist] = ta.macd(close, fastLen, slowLen, sigLen)
trendMA = ta.sma(close, maFilter)

// Only long when above 200 MA, only short when below
longEntry  = ta.crossover(macdLine, signalLine) and close > trendMA
longExit   = ta.crossunder(macdLine, signalLine)
shortEntry = ta.crossunder(macdLine, signalLine) and close < trendMA
shortExit  = ta.crossover(macdLine, signalLine)

if longEntry
    strategy.entry("Long", strategy.long)
if longExit
    strategy.close("Long")
if shortEntry
    strategy.entry("Short", strategy.short)
if shortExit
    strategy.close("Short")
```

---

## Pattern 4: ATR Trailing Stop

```pine
//@version=6
strategy("ATR Trailing Stop", overlay=true, initial_capital=10000,
  default_qty_type=strategy.percent_of_equity, default_qty_value=100)

atrLen  = input.int(14, "ATR Length")
atrMult = input.float(2.0, "ATR Multiplier")
maLen   = input.int(50, "Entry MA Length")

atrVal = ta.atr(atrLen)
ma     = ta.sma(close, maLen)

longEntry = ta.crossover(close, ma)

if longEntry
    strategy.entry("Long", strategy.long)

// Trail using ATR-based points
if strategy.position_size > 0
    strategy.exit("Trail", "Long",
      trail_points = atrVal * atrMult / syminfo.mintick,
      trail_offset = atrVal * atrMult / syminfo.mintick)
```

---

## Pattern 5: Multi-Indicator Confluence

```pine
//@version=6
strategy("Multi-Indicator", overlay=true, initial_capital=10000,
  default_qty_type=strategy.percent_of_equity, default_qty_value=100)

// Inputs
rsiLen  = input.int(14, "RSI Length")
maLen   = input.int(50, "MA Length")
adxLen  = input.int(14, "ADX Length")
adxMin  = input.float(25.0, "Min ADX")

// Indicators
myRSI = ta.rsi(close, rsiLen)
ma    = ta.ema(close, maLen)
[diplus, diminus, adx] = ta.dmi(adxLen, adxLen)

// Confluence conditions
trendUp   = close > ma
momentum  = myRSI > 50 and myRSI < 70
trending  = adx > adxMin
diConfirm = diplus > diminus

longEntry = trendUp and momentum and trending and diConfirm

shortConditions = close < ma and myRSI < 50 and myRSI > 30 and trending and diminus > diplus

if longEntry
    strategy.entry("Long", strategy.long)
if shortConditions
    strategy.entry("Short", strategy.short)

// Exit on momentum loss
if strategy.position_size > 0 and myRSI > 80
    strategy.close("Long")
if strategy.position_size < 0 and myRSI < 20
    strategy.close("Short")
```

---

## Pattern 6: Bollinger Band Breakout

```pine
//@version=6
strategy("BB Breakout", overlay=true, initial_capital=10000,
  default_qty_type=strategy.percent_of_equity, default_qty_value=100)

bbLen  = input.int(20, "BB Length")
bbMult = input.float(2.0, "BB Multiplier")

[basis, upper, lower] = ta.bb(close, bbLen, bbMult)

longEntry  = ta.crossover(close, upper)
longExit   = ta.crossunder(close, basis)
shortEntry = ta.crossunder(close, lower)
shortExit  = ta.crossover(close, basis)

if longEntry
    strategy.entry("Long", strategy.long)
if longExit
    strategy.close("Long")
if shortEntry
    strategy.entry("Short", strategy.short)
if shortExit
    strategy.close("Short")

plot(basis, "Basis", color.gray)
plot(upper, "Upper", color.green)
plot(lower, "Lower", color.red)
```

---

## Strategy Order Functions Reference

### `strategy.entry(id, direction, qty, limit, stop, ...)`

Places an entry order. If an opposite position exists, it reverses.

| Param | Type | Description |
|-------|------|-------------|
| `id` | `string` | Order identifier |
| `direction` | `strategy.long` / `strategy.short` | Trade direction |
| `qty` | `float` | Override quantity (optional) |
| `limit` | `float` | Limit price |
| `stop` | `float` | Stop price |
| `comment` | `string` | Comment on trade |
| `alert_message` | `string` | Alert message |

### `strategy.exit(id, from_entry, qty, profit, loss, limit, stop, trail_points, trail_offset, ...)`

Places exit order against a specific entry.

| Param | Type | Description |
|-------|------|-------------|
| `profit` | `float` | Take-profit in ticks |
| `loss` | `float` | Stop-loss in ticks |
| `limit` | `float` | Take-profit price |
| `stop` | `float` | Stop-loss price |
| `trail_points` | `float` | Trailing activation in ticks |
| `trail_offset` | `float` | Trailing distance in ticks |

### `strategy.close(id, ...)`

Closes position opened by the entry with matching `id`.

### `strategy.close_all(...)`

Closes all open positions.

### `strategy.cancel(id)` / `strategy.cancel_all()`

Cancels pending orders.

---

## Strategy Variables

| Variable | Description |
|----------|-------------|
| `strategy.position_size` | Current position size (>0 long, <0 short, 0 flat) |
| `strategy.position_avg_price` | Average entry price |
| `strategy.equity` | Current equity |
| `strategy.netprofit` | Total net profit |
| `strategy.closedtrades` | Number of closed trades |
| `strategy.wintrades` | Number of winning trades |
| `strategy.losstrades` | Number of losing trades |
| `strategy.max_drawdown` | Maximum drawdown |
| `strategy.initial_capital` | Starting capital |
| `strategy.openprofit` | Unrealized PnL |

---

## Tips

1. **`strategy.entry` reverses positions** — if long and you call `strategy.entry("Short", strategy.short)`, it closes the long and opens short.
2. **`strategy.exit` must reference `from_entry`** — e.g., `strategy.exit("Exit", "Long", ...)`.
3. **`strategy.exit` only works once** — after it fills, you need another `strategy.exit` call for the next trade.
4. **Ticks vs price** — `profit`/`loss` in `strategy.exit` are in ticks. Use `limit`/`stop` for absolute prices.
5. **`syminfo.mintick`** — use to convert between price and ticks: `priceDistance / syminfo.mintick = ticks`.
6. **Position sizing** — check `strategy.position_size != 0` before applying exits.
7. **`process_orders_on_close = true`** — fills orders at the current bar's close instead of next bar's open. Useful for testing but less realistic.
