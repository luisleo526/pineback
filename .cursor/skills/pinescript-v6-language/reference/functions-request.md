# PineScript v6 — Request Functions Reference

## `request.security(symbol, timeframe, expression, gaps, lookahead, ignore_invalid_symbol, currency, calc_bars_count)`

Requests the result of an expression evaluated on another symbol/timeframe.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `symbol` | `simple string` | | Ticker ID (e.g., `"NASDAQ:AAPL"`, `syminfo.tickerid`) |
| `timeframe` | `simple string` | | Timeframe string (`""` = chart TF, `"1D"`, `"60"`, `"1W"`, etc.) |
| `expression` | any | | Value to evaluate in the requested context. Can be a variable, function call, or tuple `[open, close, ta.sma(close, 10)]` |
| `gaps` | `barmerge.gaps_off` (default) / `barmerge.gaps_on` | `gaps_off` | `gaps_on` returns `na` on bars without data from the requested TF |
| `lookahead` | `barmerge.lookahead_off` (default) / `barmerge.lookahead_on` | `lookahead_off` | `lookahead_on` uses future data (causes repainting!) |
| `ignore_invalid_symbol` | `simple bool` | `false` | If `true`, returns `na` for invalid symbols instead of error |
| `currency` | `simple string` | | Convert result to this currency |
| `calc_bars_count` | `simple int` | | Limit historical bars in requested dataset |

### Key behaviors

- **Max 40 unique `request.*()` calls** per script. Same function + same args = 1 call.
- **Repainting risk**: historical vs realtime bars may differ.
- **Non-repainting pattern**:
  ```pine
  indexHTF = barstate.isrealtime ? 1 : 0
  indexCurr = barstate.isrealtime ? 0 : 1
  safeClose = request.security(syminfo.tickerid, "1D", close[indexHTF])[indexCurr]
  ```
- **Tuple expression** for multiple values in one call:
  ```pine
  [o, h, l, c] = request.security(syminfo.tickerid, "1D", [open, high, low, close])
  ```
- **User-defined function** as expression:
  ```pine
  myFunc() =>
      var float maxVal = na
      maxVal := math.max(nz(maxVal), high)
  allTimeHigh = request.security(syminfo.tickerid, "1D", myFunc())
  ```

## `request.security_lower_tf(symbol, timeframe, expression, ignore_invalid_symbol, currency, ignore_invalid_timeframe, calc_bars_count)`

Requests data from a **lower** timeframe. Returns an `array` with one element per intrabar.

```pine
// On a 5min chart, requesting 1min data returns ~5 elements per bar
arr = request.security_lower_tf(syminfo.tickerid, "1", close)
```

**Warning:** LTF requests consume significant memory. Each bar stores an array of intrabar values.

## `request.financial(symbol, financial_id, period, gaps, ignore_invalid_symbol, currency)`

Requests financial data (fundamentals) for a symbol.

```pine
// Get quarterly revenue
rev = request.financial("NASDAQ:AAPL", "TOTAL_REVENUE", "FQ")
```

Periods: `"FQ"` (fiscal quarter), `"FY"` (fiscal year), `"TTM"` (trailing twelve months)

## `request.economic(country_code, field, gaps, ignore_invalid_symbol)`

Requests economic data (GDP, CPI, interest rates, etc.).

```pine
gdp = request.economic("US", "GDP")
```

## `request.dividends(ticker, field, gaps, lookahead, ignore_invalid_symbol, currency)`

Requests dividend data. Fields: `dividends.gross`, `dividends.net`

## `request.earnings(ticker, field, gaps, lookahead, ignore_invalid_symbol, currency)`

Requests earnings data. Fields: `earnings.actual`, `earnings.estimate`, `earnings.standardized`

## `request.splits(ticker, field, gaps, lookahead, ignore_invalid_symbol)`

Requests stock split data. Fields: `splits.numerator`, `splits.denominator`

## `request.seed(source, symbol, expression, ignore_invalid_symbol)`

Requests data from a user-maintained GitHub repository.

```pine
data = request.seed("seed_crypto_santiment", "BTC_DEV_ACTIVITY", close)
```

## `request.currency_rate(from, to, ignore_invalid_currency)`

Returns the conversion rate between two currencies.

```pine
rate = request.currency_rate("EUR", "USD")
```

## Timeframe String Format

| String | Meaning |
|--------|---------|
| `""` | Chart's current timeframe |
| `"1"` | 1 minute |
| `"5"` | 5 minutes |
| `"15"` | 15 minutes |
| `"60"` | 1 hour (no "H" unit!) |
| `"240"` | 4 hours |
| `"1D"` | 1 day |
| `"1W"` | 1 week |
| `"1M"` | 1 month |
| `"3M"` | 3 months |
| `"12M"` | 12 months (1 year) |
| `"1S"` | 1 second |
| `"1T"` | 1 tick |

Rules: no "H" for hours (use minutes), no letter = minutes, multiplier ranges vary by unit.
