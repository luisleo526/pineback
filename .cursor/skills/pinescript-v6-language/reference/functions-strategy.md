# PineScript v6 — Strategy Functions Reference

## Order Placement

### `strategy.entry(id, direction, qty, limit, stop, oca_name, oca_type, comment, alert_message, disable_alert, qty_type)`

Opens or adds to a position. If an unfilled order with the same `id` exists, modifies it. If an opposite position exists, reverses it.

| Param | Type | Description |
|-------|------|-------------|
| `id` | `series string` | **Required.** Order identifier |
| `direction` | `strategy.long` / `strategy.short` | **Required.** Trade direction |
| `qty` | `series int/float` | Order quantity. Defaults to `default_qty_value` from `strategy()` |
| `limit` | `series int/float` | Limit price. `na` = market order |
| `stop` | `series int/float` | Stop price. `na` = no stop trigger |
| `oca_name` | `series string` | OCA group name |
| `oca_type` | `strategy.oca.cancel` / `.none` / `.reduce` | OCA behavior |
| `comment` | `series string` | Trade comment |
| `alert_message` | `series string` | Alert message text |
| `disable_alert` | `series bool` | Disable alert for this order |
| `qty_type` | constant | Override qty type: `strategy.fixed`, `strategy.cash`, `strategy.percent_of_equity` |

### `strategy.order(id, direction, qty, limit, stop, oca_name, oca_type, comment, alert_message, disable_alert, qty_type)`

Like `strategy.entry()` but does NOT reverse positions automatically. Creates a raw order that can open, add to, or reduce a position.

Same parameters as `strategy.entry()`.

**Key difference:** `strategy.entry` automatically closes the opposite position before opening; `strategy.order` does not — you manage position sizing manually.

### `strategy.exit(id, from_entry, qty, qty_percent, profit, loss, limit, stop, trail_price, trail_points, trail_offset, oca_name, comment, comment_profit, comment_loss, comment_trailing, alert_message, alert_profit, alert_loss, alert_trailing, disable_alert)`

Places price-based exit orders (limit, stop, trailing stop). Does NOT create market orders.

| Param | Type | Description |
|-------|------|-------------|
| `id` | `series string` | **Required.** Exit order identifier |
| `from_entry` | `series string` | Entry ID to exit from. If omitted, exits all entries |
| `qty` | `series int/float` | Quantity to exit |
| `qty_percent` | `series int/float` | Percentage of position to exit (0-100) |
| `profit` | `series int/float` | Take-profit distance in **ticks** |
| `loss` | `series int/float` | Stop-loss distance in **ticks** |
| `limit` | `series int/float` | Take-profit **price** |
| `stop` | `series int/float` | Stop-loss **price** |
| `trail_price` | `series int/float` | Price that activates trailing stop |
| `trail_points` | `series int/float` | Trailing activation distance in **ticks** |
| `trail_offset` | `series int/float` | Trailing distance behind price in **ticks** |
| `comment_profit` | `series string` | Comment for TP fill |
| `comment_loss` | `series string` | Comment for SL fill |
| `comment_trailing` | `series string` | Comment for trailing fill |

**Important notes:**
- `profit`/`loss` are in **ticks** (not price). Convert: `priceDistance / syminfo.mintick = ticks`
- `limit`/`stop` are **absolute prices**
- If both `stop` and `trail_*` are specified, only the first to trigger is placed (both are stop-type)
- Without `from_entry`, exit applies to ALL entries including future ones until position closes
- FIFO rule: exits start from the first open trade by default

### `strategy.close(id, comment, qty, qty_percent, alert_message, disable_alert, immediately)`

Closes position(s) opened by entries with matching `id` using a **market order**.

| Param | Type | Description |
|-------|------|-------------|
| `id` | `series string` | **Required.** Entry ID to close |
| `qty` | `series int/float` | Quantity to close |
| `qty_percent` | `series int/float` | Percentage to close (0-100) |
| `immediately` | `series bool` | If `true`, fills at current bar's close |
| `comment` | `series string` | Trade comment |

### `strategy.close_all(comment, alert_message, disable_alert, immediately)`

Closes entire position regardless of entry IDs.

### `strategy.cancel(id)` / `strategy.cancel_all()`

Cancels pending/unfilled orders. `strategy.cancel(id)` cancels all unfilled orders with that ID.

## Risk Management

```pine
strategy.risk.allow_entry_in(value)
// value: strategy.direction.long, strategy.direction.short, strategy.direction.all

strategy.risk.max_cons_loss_days(count)
// Stop trading after N consecutive losing days

strategy.risk.max_drawdown(value, type)
// type: strategy.percent_of_equity or strategy.cash

strategy.risk.max_intraday_filled_orders(count)
// Max filled orders per day

strategy.risk.max_intraday_loss(value, type)
// type: strategy.percent_of_equity or strategy.cash

strategy.risk.max_position_size(contracts)
// Maximum position size in contracts
```

## Trade Inspection Functions

### Closed Trades (`strategy.closedtrades.*`)

All take `trade_num` (series int) — the index of the closed trade (0 = oldest).

| Function | Returns | Description |
|----------|---------|-------------|
| `.commission(trade_num)` | `float` | Total fees paid |
| `.entry_bar_index(trade_num)` | `int` | Bar index of entry |
| `.entry_comment(trade_num)` | `string` | Entry comment |
| `.entry_id(trade_num)` | `string` | Entry order ID |
| `.entry_price(trade_num)` | `float` | Entry fill price |
| `.entry_time(trade_num)` | `int` | Entry time (UNIX ms) |
| `.exit_bar_index(trade_num)` | `int` | Bar index of exit |
| `.exit_comment(trade_num)` | `string` | Exit comment |
| `.exit_id(trade_num)` | `string` | Exit order ID |
| `.exit_price(trade_num)` | `float` | Exit fill price |
| `.exit_time(trade_num)` | `int` | Exit time (UNIX ms) |
| `.max_drawdown(trade_num)` | `float` | Max drawdown during trade |
| `.max_drawdown_percent(trade_num)` | `float` | Max drawdown % |
| `.max_runup(trade_num)` | `float` | Max runup during trade |
| `.max_runup_percent(trade_num)` | `float` | Max runup % |
| `.profit(trade_num)` | `float` | Net profit of trade |
| `.profit_percent(trade_num)` | `float` | Profit % |
| `.size(trade_num)` | `float` | Trade size (contracts) |

### Open Trades (`strategy.opentrades.*`)

Same functions as closed trades (except exit-related ones):

`.commission()`, `.entry_bar_index()`, `.entry_comment()`, `.entry_id()`, `.entry_price()`, `.entry_time()`, `.max_drawdown()`, `.max_drawdown_percent()`, `.max_runup()`, `.max_runup_percent()`, `.profit()`, `.profit_percent()`, `.size()`

### Utility

| Function | Description |
|----------|-------------|
| `strategy.convert_to_account(value)` | Convert symbol currency to account currency |
| `strategy.convert_to_symbol(value)` | Convert account currency to symbol currency |
| `strategy.default_entry_qty(fill_price)` | Default entry qty at given price |

## Strategy Variables (Read-Only)

| Variable | Type | Description |
|----------|------|-------------|
| `strategy.position_size` | `series float` | Current position (>0 long, <0 short, 0 flat) |
| `strategy.position_avg_price` | `series float` | Average entry price |
| `strategy.position_entry_name` | `series string` | Name of initial entry order |
| `strategy.equity` | `series float` | Current equity |
| `strategy.initial_capital` | `series float` | Starting capital |
| `strategy.netprofit` | `series float` | Total realized P&L |
| `strategy.netprofit_percent` | `series float` | Net profit as % of initial capital |
| `strategy.openprofit` | `series float` | Unrealized P&L |
| `strategy.openprofit_percent` | `series float` | Unrealized P&L % |
| `strategy.grossprofit` | `series float` | Total winning trade value |
| `strategy.grossloss` | `series float` | Total losing trade value |
| `strategy.closedtrades` | `series int` | Number of closed trades |
| `strategy.opentrades` | `series int` | Number of open entries |
| `strategy.wintrades` | `series int` | Winning trades count |
| `strategy.losstrades` | `series int` | Losing trades count |
| `strategy.eventrades` | `series int` | Breakeven trades count |
| `strategy.max_drawdown` | `series float` | Maximum equity drawdown |
| `strategy.max_drawdown_percent` | `series float` | Max drawdown % |
| `strategy.max_runup` | `series float` | Maximum equity runup |
| `strategy.max_runup_percent` | `series float` | Max runup % |
| `strategy.avg_trade` | `series float` | Average P&L per trade |
| `strategy.avg_trade_percent` | `series float` | Average P&L % per trade |
| `strategy.avg_winning_trade` | `series float` | Average winning trade |
| `strategy.avg_losing_trade` | `series float` | Average losing trade |
| `strategy.margin_liquidation_price` | `series float` | Margin call liquidation price |
| `strategy.account_currency` | `simple string` | Account currency code |
| `strategy.opentrades.capital_held` | `series float` | Capital held by open trades (margin) |

## Strategy Constants

| Constant | Value | Use |
|----------|-------|-----|
| `strategy.long` | | Direction: long |
| `strategy.short` | | Direction: short |
| `strategy.fixed` | | Qty type: fixed contracts |
| `strategy.cash` | | Qty type: cash amount |
| `strategy.percent_of_equity` | | Qty type: % of equity |
| `strategy.commission.percent` | | Commission: percentage |
| `strategy.commission.cash_per_contract` | | Commission: per contract |
| `strategy.commission.cash_per_order` | | Commission: per order |
| `strategy.oca.cancel` | | OCA: cancel other orders |
| `strategy.oca.reduce` | | OCA: reduce other orders |
| `strategy.oca.none` | | OCA: no grouping |
| `strategy.direction.all` | | Allow both directions |
| `strategy.direction.long` | | Allow only long |
| `strategy.direction.short` | | Allow only short |
