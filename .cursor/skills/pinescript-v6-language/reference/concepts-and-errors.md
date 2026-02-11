# PineScript v6 — Concepts, Execution Model & Common Errors

## Execution Model

### Bar-by-Bar Execution

- Script code executes **once per bar** from left (oldest) to right (newest).
- On each execution, all global-scope code runs top-to-bottom.
- Variables are **re-declared** each bar unless using `var` or `varip`.
- After each bar, variable states are saved to an internal **time series**.

### `var` — Persist Across Bars

```pine
var int counter = 0    // initialized once on bar 0, persists
counter += 1           // accumulates across all bars
```

### `varip` — Persist Across Ticks (Realtime)

```pine
varip int tickCount = 0   // persists even between ticks on realtime bar
tickCount += 1
```

### History Referencing (`[]`)

```pine
close[1]      // previous bar's close
close[10]     // 10 bars ago
myVar[1]      // previous bar's value of myVar
```

- `close[1]` is `na` on bar 0 (no previous bar exists).
- Only reference history of variables/expressions evaluated **every bar** in the **global scope**.
- History of local-scope variables (inside `if`, `for`) can produce unexpected results.

### Historical vs Realtime Bars

| Context | Behavior |
|---------|----------|
| Historical bars | Script executes **once** per bar. Values are final. |
| Realtime bar | Script executes on **every tick**. Values may change until bar closes. |

**Barstate variables:**

| Variable | True when... |
|----------|-------------|
| `barstate.isfirst` | First bar in dataset |
| `barstate.islast` | Last bar (realtime or final historical) |
| `barstate.ishistory` | Any historical bar |
| `barstate.isrealtime` | Realtime bar |
| `barstate.isconfirmed` | Last tick of current bar (bar about to close) |
| `barstate.isnew` | First tick of a new bar |
| `barstate.islastconfirmedhistory` | Last historical bar before realtime |

### Repainting

A script **repaints** when it produces different results on historical vs realtime bars. Common causes:

1. Using `barstate.isrealtime` to branch logic
2. `request.security()` with `lookahead=barmerge.lookahead_on`
3. `ta.valuewhen()`, `ta.barssince()`, `ta.pivothigh/low()` on realtime data
4. Using `timenow` or `calendar.*` variables

**Non-repainting `request.security` pattern:**
```pine
indexHTF = barstate.isrealtime ? 1 : 0
indexCurr = barstate.isrealtime ? 0 : 1
safeValue = request.security(syminfo.tickerid, "1D", close[indexHTF])[indexCurr]
```

---

## Timeframe Strings

| String | Meaning |
|--------|---------|
| `""` | Current chart timeframe |
| `"1"` through `"1440"` | Minutes (no letter) |
| `"1S"`, `"5S"`, `"10S"`, `"15S"`, `"30S"`, `"45S"` | Seconds |
| `"1D"` through `"365D"` | Days |
| `"1W"` through `"52W"` | Weeks |
| `"1M"` through `"12M"` | Months |
| `"1T"`, `"10T"`, `"100T"`, `"1000T"` | Ticks |

**No "H" unit** — use minutes: `"60"` = 1 hour, `"240"` = 4 hours.

```pine
// Compare timeframes
chartTFMinutes = timeframe.in_seconds() / 60
inputTFMinutes = timeframe.in_seconds("1D") / 60

// Detect timeframe change
if timeframe.change("1D")
    // New daily bar started
```

---

## Objects and User-Defined Types (UDT)

```pine
// Define a type
type TradeInfo
    float entryPrice = na
    float stopLoss = na
    int   barCount = 0

// Create instance
trade = TradeInfo.new(close, close * 0.98, 0)

// Access fields
trade.entryPrice
trade.barCount += 1
```

- UDTs are always `series` form.
- Use `var` to persist objects across bars.
- Objects passed to `request.security()` return copies (consumes memory).

---

## Methods

```pine
// Declare a method (first param = receiver type)
method update(TradeInfo self, float newPrice) =>
    self.entryPrice := newPrice

// Call with dot notation
trade.update(close)

// Built-in types also support method syntax
myArray.push(close)    // same as array.push(myArray, close)
myLine.set_color(color.red)
```

Namespaces supporting method syntax: `array`, `matrix`, `map`, `line`, `linefill`, `label`, `box`, `table`, `polyline`.

---

## Common Errors & Fixes

### "The if statement is too long"
**Fix:** Split large if blocks into smaller functions.

### "Script requesting too many securities"
**Cause:** Max 40 unique `request.*()` calls.
**Fix:** Combine requests using tuples: `[a, b, c] = request.security(...)`.

### "Loop is too long (> 500 ms)"
**Fix:** Optimize algorithm, reduce loop iterations, use built-in functions instead.

### "Script has too many local variables"
**Cause:** Max ~1000 variables per function (including implicit ones).
**Fix:** Inline expressions: `var3 = expr1 + expr2` instead of `var1 = expr1; var2 = expr2; var3 = var1 + var2`.

### "The requested historical offset (X) is beyond the historical buffer's limit (Y)"
**Cause:** Accessing `close[N]` where N exceeds the buffer.
**Fixes:**
1. `max_bars_back(close, 1000)` — set buffer for specific variable
2. `indicator("...", max_bars_back=1000)` — set for all variables (less efficient)
3. Access `close[maxN]` on first bar to force buffer size

### "Memory limits exceeded"
**Causes:** Large collections from `request.*()`, excessive drawings, large `max_bars_back`.
**Fixes:**
- Return calculated **results** from requests, not entire collections
- Return collections only on specific bars (`barstate.islast`), not every bar
- Use `var` for tables, fill only on `barstate.islast`
- Minimize drawing updates on historical bars
- Reduce `max_bars_back` to minimum necessary

### "Mismatched input / no viable alternative"
**Cause:** Syntax error — usually wrong indentation or missing expression.
**Fix:** Check indentation (4 spaces / 1 tab for local blocks), ensure all expressions return values.

### Type qualifier errors ("Cannot call X with series Y")
**Cause:** Passing `series` value where `simple` or `input` is required.
**Example:** `ta.sma(close, mySeriesLen)` fails if `mySeriesLen` changes per bar.
**Fix:** Use `input.int()` or a constant for the length parameter.

---

## Script Limitations

| Limit | Value |
|-------|-------|
| Max `request.*()` calls | 40 unique |
| Max local variables per function | ~1000 |
| Max bars back (default buffer) | Auto-sized |
| Max bars back (settable) | 5000 |
| Loop timeout | 500ms per bar |
| Max lines/labels/boxes | 500 each |
| Max tables | 50 |
| Max polylines | 100 |
| Max `alert()` calls | 1 per script |
| Max `alertcondition()` calls | Unlimited |
| Script compilation size | ~80KB compiled |

---

## Style Guide Summary

### Naming Conventions
- `camelCase` for variables and functions: `maFast`, `rsiPeriod`, `getSignal()`
- `SNAKE_CASE` for constants: `BULL_COLOR`, `MAX_LOOKBACK`
- Suffix inputs with `Input`: `maLengthInput`, `showFilterInput`

### Script Organization
1. `//@version=6`
2. Declaration (`indicator()` / `strategy()`)
3. Imports
4. Constants (`SNAKE_CASE`)
5. Inputs (grouped)
6. Functions
7. Calculations
8. Strategy calls
9. Visuals (plots, drawings)
10. Alerts

### Best Practices
- Use explicit types: `float x = close` not just `x = close`
- Use `=` for declarations, `:=` for reassignment
- Space around operators: `a = b + c`, not `a=b+c`
- 4 spaces or 1 tab for indentation
- Don't use `var` for constants (minor perf penalty)

---

## Debugging Tips

1. **Plot intermediate values** to see what's happening:
   ```pine
   plot(myCondition ? 1 : 0, "Debug condition")
   ```

2. **Use labels** for string/complex debugging:
   ```pine
   if barstate.islast
       label.new(bar_index, high, str.tostring(myVar))
   ```

3. **Pine Logs** for detailed logging:
   ```pine
   log.info(str.format("RSI={0}, MA={1}", myRSI, myMA))
   ```

4. **`str.tostring()` with format** for readable numbers:
   ```pine
   str.tostring(value, "#.##")
   str.tostring(value, format.mintick)
   ```

5. **Check `na`** at every step — many bugs are `na` propagation.
