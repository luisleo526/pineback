---
name: backtest-results-frontend
description: Build a web frontend that displays backtest results — equity curves, drawdown charts, trade tables, and performance stats. Covers the data contract, UI components, charting with lightweight-charts, formatting rules, and polling. Use when building or modifying the frontend that renders backtest results.
---

# Backtest Results Frontend

Simple frontend for a backtest system — data contract, components, charting.

For system-wide architecture context, see [architecture.md](../architecture.md).

## Frontend ↔ Backend Contract

The frontend is a **thin rendering layer**. All financial calculations happen
on the backend. The frontend:

1. Submits PineScript + parameters → `POST /api/backtests`
2. Polls for completion → `GET /api/backtests/{id}` every 2-3s
3. Renders the pre-computed result

## Result Data Shape

### Scalars (stats cards)

```
total_return_pct      float       +28.82
sharpe_ratio          float|null  2.15        (null if insufficient data)
sortino_ratio         float|null  3.20
calmar_ratio          float|null  1.85
max_drawdown_pct      float       -12.50
total_trades          int         28
win_rate_pct          float       57.14
profit_factor         float       1.85
expectancy            float       106.75
initial_capital       float       10000
final_value           float       12882.45
```

### Time Series (charts, ~1000 points each)

```
equity_curve     [{timestamp, value}, ...]
returns          [{timestamp, return}, ...]
drawdown_curve   [{timestamp, drawdown_pct}, ...]
```

### Records (tables)

```
trades     [{direction, status, entry_time, exit_time, entry_price,
             exit_price, pnl, return_pct, duration, size}, ...]
orders     [{timestamp, side, price, size, fees}, ...]
drawdowns  [{peak_time, valley_time, drawdown_pct, duration, status}, ...]
```

## UI Components

**1. Submit Form** — Code editor (Monaco/CodeMirror) for PineScript,
dropdowns for symbol/timeframe/exchange (populated from `GET /api/symbols`),
date range, capital.

**2. Stats Dashboard** — 8 cards in 2 rows: Return, Sharpe, Max DD, Trades,
Win Rate, Profit Factor, Sortino, Expectancy.

**3. Equity Curve** — Area chart. X: timestamp, Y: portfolio value.

**4. Drawdown Chart** — Filled area below zero. X: timestamp, Y: drawdown_pct.

**5. Trade Table** — Sortable, paginated (>50 trades). Columns: direction,
entry/exit time+price, PnL, return%, duration. Color PnL green/red.

**6. History List** — Past backtests from `GET /api/backtests`. Summary
columns only (name, symbol, TF, status, return, sharpe). Click → detail.

## Charting

**Recommended:** TradingView's `lightweight-charts` — financial-native,
small bundle, supports timestamps and crosshairs.

```javascript
import { createChart } from 'lightweight-charts';

function renderEquity(container, data) {
    const chart = createChart(container, { width: 800, height: 400 });
    const series = chart.addAreaSeries({
        lineColor: '#2196F3',
        topColor: 'rgba(33,150,243,0.3)',
        bottomColor: 'rgba(33,150,243,0)',
    });
    series.setData(data.map(p => ({
        time: Math.floor(new Date(p.timestamp).getTime() / 1000),
        value: p.value,
    })));
    chart.timeScale().fitContent();
}
```

Alternatives: Chart.js (simple), ECharts (powerful), Plotly (interactive).

## Formatting

| Type | Format | Example |
|------|--------|---------|
| Return | sign + 2 decimals | `+28.82%` |
| Ratio | 2 decimals | `2.15` |
| Drawdown | 2 decimals, negative | `-12.50%` |
| Dollar | comma + 2 decimals | `$12,882.45` |
| PnL | sign + dollar | `+$330.83` |
| Count | integer | `28` |
| Duration | human readable | `3d 4h` |
| Null metrics | dash | `—` |

```javascript
function formatRatio(v) { return v == null ? "—" : v.toFixed(2); }
function formatPct(v) {
    if (v == null) return "—";
    return (v > 0 ? "+" : "") + v.toFixed(2) + "%";
}
```

**Null ≠ 0.** Sharpe of 0 means zero excess return. Sharpe of null means
not enough data. Display `—`, never `0`.

## Color Coding

| Metric | Green | Red |
|--------|-------|-----|
| Return / PnL | > 0 | < 0 |
| Sharpe | > 1 | < 0 |
| Win Rate | > 50% | < 40% |
| Drawdown | — | always red |

## Polling

```javascript
async function waitForResult(id) {
    while (true) {
        const r = await fetch(`/api/backtests/${id}`).then(r => r.json());
        if (r.status === "completed") return r.result;
        if (r.status === "failed") throw new Error(r.error_message);
        await new Promise(r => setTimeout(r, 2500));
    }
}
```

Stop polling immediately on terminal status. Show spinner while pending/running.

## Tech Stack (recommended for simple frontend)

Vue 3 or React + Vite + Tailwind CSS + lightweight-charts + native HTML tables.
Desktop-first (min 1024px). No Vuex/Redux — framework reactivity is enough.

## Pitfalls

| Pitfall | Prevention |
|---------|-----------|
| Display null as "0" | Use `—` for null metrics |
| Wrong timestamp format | lightweight-charts wants Unix seconds; convert ISO 8601 |
| `result_json` in list view | Only use summary columns for listing |
| Render 500+ trade rows | Paginate or virtualize |
| No loading state | Show spinner during pending/running |
| No compile error feedback | Show 400 error near code editor |
| Chart gaps (stocks) | Use logical time for non-24/7 markets |
