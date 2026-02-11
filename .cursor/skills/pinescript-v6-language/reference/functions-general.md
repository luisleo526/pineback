# PineScript v6 — General Functions Reference

## Math Functions (`math.*`)

### Arithmetic

| Function | Description |
|----------|-------------|
| `math.abs(x)` | Absolute value |
| `math.ceil(x)` | Round up to integer |
| `math.floor(x)` | Round down to integer |
| `math.round(x)` | Round to nearest integer |
| `math.round(x, precision)` | Round to N decimal places |
| `math.round_to_mintick(x)` | Round to symbol's minimum tick |
| `math.sign(x)` | Returns 1, 0, or -1 |
| `math.max(x, y)` | Maximum of two values (also 3, 4 arg versions) |
| `math.min(x, y)` | Minimum of two values (also 3, 4 arg versions) |
| `math.avg(x, y, ...)` | Average of 2-6 values |
| `math.sum(source, length)` | Sum of source over length bars |
| `math.pow(base, exp)` | Power: base^exp |
| `math.sqrt(x)` | Square root |
| `math.exp(x)` | e^x |
| `math.log(x)` | Natural logarithm (ln) |
| `math.log10(x)` | Base-10 logarithm |
| `math.random(min, max, seed)` | Random float in [min, max) |

### Trigonometry

| Function | Description |
|----------|-------------|
| `math.sin(x)` | Sine (radians) |
| `math.cos(x)` | Cosine (radians) |
| `math.tan(x)` | Tangent (radians) |
| `math.asin(x)` | Arcsine |
| `math.acos(x)` | Arccosine |
| `math.atan(x)` | Arctangent |
| `math.todegrees(x)` | Radians to degrees |
| `math.toradians(x)` | Degrees to radians |

### Constants

| Constant | Value |
|----------|-------|
| `math.pi` | 3.14159... |
| `math.e` | 2.71828... |
| `math.phi` | 1.61803... (golden ratio) |
| `math.rphi` | 0.61803... (1/phi) |

---

## String Functions (`str.*`)

| Function | Returns | Description |
|----------|---------|-------------|
| `str.tostring(value)` | `string` | Convert number/bool to string |
| `str.tostring(value, format)` | `string` | Formatted: `format.mintick`, `format.percent`, `format.volume` |
| `str.tonumber(string)` | `float` | Parse string to number |
| `str.format(formatStr, arg0, ...)` | `string` | Template: `str.format("{0} is {1}", name, val)` |
| `str.format_time(time, format, timezone)` | `string` | Format UNIX time: `str.format_time(time, "yyyy-MM-dd HH:mm")` |
| `str.length(string)` | `int` | String length |
| `str.contains(source, str)` | `bool` | Check if contains substring |
| `str.startswith(source, str)` | `bool` | Check prefix |
| `str.endswith(source, str)` | `bool` | Check suffix |
| `str.pos(source, str)` | `int` | Position of first occurrence (-1 if not found) |
| `str.substring(source, begin)` | `string` | Substring from index to end |
| `str.substring(source, begin, end)` | `string` | Substring from begin to end (exclusive) |
| `str.replace(source, target, replacement, occurrence)` | `string` | Replace Nth occurrence |
| `str.replace_all(source, target, replacement)` | `string` | Replace all occurrences |
| `str.split(string, separator)` | `array<string>` | Split into array |
| `str.repeat(source, count)` | `string` | Repeat N times |
| `str.lower(source)` | `string` | To lowercase |
| `str.upper(source)` | `string` | To uppercase |
| `str.trim(source)` | `string` | Remove leading/trailing whitespace |
| `str.match(source, regex)` | `string` | Regex match (first capturing group or full match) |

---

## Input Functions (`input.*`)

| Function | Returns | Key Params |
|----------|---------|------------|
| `input.int(defval, title, minval, maxval, step, ...)` | `input int` | Integer input with optional range |
| `input.float(defval, title, minval, maxval, step, ...)` | `input float` | Float input with optional range |
| `input.bool(defval, title, ...)` | `input bool` | Checkbox toggle |
| `input.string(defval, title, options, ...)` | `input string` | Text or dropdown. `options` = string array |
| `input.source(defval, title, ...)` | `series float` | Price source dropdown (close, open, etc.) |
| `input.color(defval, title, ...)` | `input color` | Color picker |
| `input.timeframe(defval, title, ...)` | `input string` | Timeframe selector dropdown |
| `input.session(defval, title, ...)` | `input string` | Session time selector |
| `input.symbol(defval, title, ...)` | `input string` | Symbol/ticker selector |
| `input.price(defval, title, ...)` | `input float` | Price level with interactive line |
| `input.time(defval, title, ...)` | `input int` | Date/time picker (UNIX ms) |
| `input.text_area(defval, title, ...)` | `input string` | Multi-line text input |
| `input.enum(defval, title, ...)` | `input enum` | Enum field selector |

Common params for all: `title`, `tooltip`, `inline` (group on same line), `group` (section name), `display` (`display.all`, `display.none`, `display.status_line`, `display.data_window`), `confirm` (require confirmation)

---

## Color Functions (`color.*`)

| Function | Returns | Description |
|----------|---------|-------------|
| `color.new(color, transp)` | `color` | Set transparency (0=opaque, 100=invisible) |
| `color.rgb(red, green, blue, transp)` | `color` | Create from RGB (0-255) + transparency (0-100) |
| `color.from_gradient(value, bottom, top, bottomColor, topColor)` | `color` | Gradient between two colors based on value |
| `color.r(color)` | `float` | Red component (0-255) |
| `color.g(color)` | `float` | Green component (0-255) |
| `color.b(color)` | `float` | Blue component (0-255) |
| `color.t(color)` | `float` | Transparency (0-100) |

### Color Constants

`color.aqua`, `color.black`, `color.blue`, `color.fuchsia`, `color.gray`, `color.green`, `color.lime`, `color.maroon`, `color.navy`, `color.olive`, `color.orange`, `color.purple`, `color.red`, `color.silver`, `color.teal`, `color.white`, `color.yellow`

---

## Alert Function

```pine
alert(message, freq)
```

| Param | Description |
|-------|-------------|
| `message` | `series string` — alert text |
| `freq` | `alert.freq_all` (every call), `alert.freq_once_per_bar`, `alert.freq_once_per_bar_close` |

```pine
alertcondition(condition, title, message)
```
Defines an alert condition selectable in TradingView's alert dialog. Only works in indicators (not strategies).

---

## Runtime

```pine
runtime.error(message)
```
Throws a custom runtime error and stops the script.

---

## Ticker Functions (`ticker.*`)

| Function | Description |
|----------|-------------|
| `ticker.new(prefix, ticker, session, adjustment)` | Create custom ticker ID |
| `ticker.modify(tickerid, session, adjustment)` | Modify existing ticker |
| `ticker.standard(tickerid)` | Normalize to `"PREFIX:TICKER"` format |
| `ticker.heikinashi(symbol)` | Heikin Ashi ticker |
| `ticker.renko(symbol, style, param)` | Renko ticker |
| `ticker.kagi(symbol, reversal)` | Kagi ticker |
| `ticker.linebreak(symbol, number_of_breaks)` | Line Break ticker |
| `ticker.pointfigure(symbol, style, param, reversal)` | Point & Figure ticker |
| `ticker.inherit(from_tickerid, symbol)` | Inherit session/adjustment from another ticker |

Sessions: `session.regular`, `session.extended`
Adjustments: `adjustment.none`, `adjustment.splits`, `adjustment.dividends`

---

## Timeframe Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `timeframe.in_seconds(timeframe)` | `simple float` | Convert TF string to seconds |
| `timeframe.change(timeframe)` | `series bool` | `true` on first bar of a new period |

---

## Type Casting Functions

| Function | Description |
|----------|-------------|
| `int(x)` | Cast to int |
| `float(x)` | Cast to float |
| `bool(x)` | Cast to bool |
| `string(x)` | Cast to string |
| `color(x)` | Cast to color |

---

## Utility Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `na(x)` | `bool` | `true` if x is `na` |
| `nz(x)` | same as x | Replace `na` with 0 (or 0.0, false, "") |
| `nz(x, y)` | same as x | Replace `na` with y |
| `fixnan(x)` | same as x | Replace `na` with last non-na value |
| `max_bars_back(var, num)` | `void` | Set historical buffer size for a variable |
| `bar_index` | `series int` | Current bar number (0-based) |
| `last_bar_index` | `series int` | Index of last chart bar |
| `time(timeframe, session, timezone)` | `series int` | Bar time in session filter |
| `time_close(timeframe, session, timezone)` | `series int` | Bar close time in session filter |
| `timestamp(year, month, day, hour, minute, second)` | `simple int` | Create UNIX timestamp |
| `year(time, timezone)` | `series int` | Extract year |
| `month(time, timezone)` | `series int` | Extract month |
| `dayofmonth(time, timezone)` | `series int` | Extract day |
| `dayofweek(time, timezone)` | `series int` | Extract day of week |
| `hour(time, timezone)` | `series int` | Extract hour |
| `minute(time, timezone)` | `series int` | Extract minute |
| `second(time, timezone)` | `series int` | Extract second |
| `weekofyear(time, timezone)` | `series int` | Extract week number |
| `log.error(message)` | `void` | Pine Logs: error |
| `log.warning(message)` | `void` | Pine Logs: warning |
| `log.info(message)` | `void` | Pine Logs: info |
