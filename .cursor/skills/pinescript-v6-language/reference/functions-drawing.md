# PineScript v6 — Drawing & Plotting Functions Reference

## Plot Functions

### `plot(series, title, color, linewidth, style, trackprice, histbase, offset, join, editable, show_last, display, force_overlay)`

Main plotting function. Draws a line/histogram/columns on each bar.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `series` | `series int/float` | | **Required.** Values to plot |
| `title` | `const string` | | Plot title |
| `color` | `series color` | | Line/fill color |
| `linewidth` | `input int` | 1 | Line width (1-4) |
| `style` | `plot_style` | `plot.style_line` | Plot style |
| `trackprice` | `input bool` | false | Show horizontal price tracking line |
| `histbase` | `input float` | 0.0 | Histogram/columns baseline |
| `offset` | `series int` | 0 | Shift plot left (negative) or right (positive) |
| `display` | `plot_display` | `display.all` | Where to show: `display.all`, `display.none`, `display.pane`, `display.data_window`, `display.status_line`, `display.price_scale` |
| `force_overlay` | `const bool` | false | Force plot to main chart pane |

**Returns** a plot ID (used with `fill()`).

### Plot Styles

| Constant | Description |
|----------|-------------|
| `plot.style_line` | Continuous line |
| `plot.style_linebr` | Line with breaks at `na` |
| `plot.style_stepline` | Step line |
| `plot.style_steplinebr` | Step line with breaks |
| `plot.style_histogram` | Histogram from `histbase` |
| `plot.style_columns` | Wide columns from `histbase` |
| `plot.style_area` | Filled area to `histbase` |
| `plot.style_areabr` | Area with breaks |
| `plot.style_circles` | Circles |
| `plot.style_cross` | Crosses |

### `plotshape(series, title, style, location, color, offset, text, textcolor, size, display, show_last, force_overlay)`

Plots a shape when condition is true.

Shape styles: `shape.xcross`, `shape.cross`, `shape.triangleup`, `shape.triangledown`, `shape.flag`, `shape.circle`, `shape.arrowup`, `shape.arrowdown`, `shape.labelup`, `shape.labeldown`, `shape.square`, `shape.diamond`

Locations: `location.abovebar`, `location.belowbar`, `location.top`, `location.bottom`, `location.absolute`

Sizes: `size.auto`, `size.tiny`, `size.small`, `size.normal`, `size.large`, `size.huge`

### `plotchar(series, title, char, location, color, offset, text, textcolor, size, display, force_overlay)`

Plots a Unicode character when condition is true.

### `plotarrow(series, title, colorup, colordown, offset, minheight, maxheight, display, force_overlay)`

Plots up/down arrows based on positive/negative values.

### `plotcandle(open, high, low, close, title, color, wickcolor, bordercolor, display, force_overlay)`

Plots custom OHLC candles.

### `plotbar(open, high, low, close, title, color, display, force_overlay)`

Plots custom OHLC bars.

---

## Background & Color

### `bgcolor(color, offset, editable, show_last, title, display, force_overlay, overlay)`

Color the chart background.

```pine
bgcolor(close > open ? color.new(color.green, 90) : na)
```

### `barcolor(color, offset, editable, show_last, title, display)`

Color the price bars/candles.

```pine
barcolor(close > open ? color.green : color.red)
```

### `hline(price, title, color, linestyle, linewidth, editable, display)`

Draw a horizontal level. Returns hline ID for `fill()`.

Styles: `hline.style_solid`, `hline.style_dashed`, `hline.style_dotted`

### `fill(plot1, plot2, color, title, editable, show_last, fillgaps, display)`

Fill between two `plot()` calls or two `hline()` calls.

```pine
p1 = plot(upper)
p2 = plot(lower)
fill(p1, p2, color=color.new(color.blue, 90))
```

---

## Lines (`line.*`)

### `line.new(x1, y1, x2, y2, xloc, extend, color, style, width)`

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `x1`, `x2` | `series int` | | Start/end x (bar_index or time) |
| `y1`, `y2` | `series float` | | Start/end y (price) |
| `xloc` | `xloc.bar_index` / `xloc.bar_time` | `xloc.bar_index` | X-axis coordinate type |
| `extend` | `extend.none` / `extend.left` / `extend.right` / `extend.both` | `extend.none` | Line extension |
| `color` | `series color` | | Line color |
| `style` | line_style | `line.style_solid` | `line.style_solid`, `line.style_dashed`, `line.style_dotted`, `line.style_arrow_left`, `line.style_arrow_right`, `line.style_arrow_both` |
| `width` | `series int` | 1 | Line width |

### Setters

`line.set_x1()`, `line.set_y1()`, `line.set_x2()`, `line.set_y2()`, `line.set_xy1()`, `line.set_xy2()`, `line.set_color()`, `line.set_style()`, `line.set_width()`, `line.set_extend()`, `line.set_xloc()`

### Getters

`line.get_x1()`, `line.get_y1()`, `line.get_x2()`, `line.get_y2()`, `line.get_price(x)` (interpolated price at bar)

### Other

`line.delete(id)`, `line.copy(id)`, `line.all` (array of all lines)

**Limits:** Default max 50 lines; set `max_lines_count` in `indicator()`/`strategy()` (max 500).

---

## Labels (`label.*`)

### `label.new(x, y, text, xloc, yloc, color, style, textcolor, size, textalign, tooltip, text_font_family, force_overlay)`

| Key Params | Description |
|------------|-------------|
| `yloc` | `yloc.price` (default), `yloc.abovebar`, `yloc.belowbar` |
| `style` | `label.style_label_up/down/left/right/center`, `label.style_none`, `label.style_circle`, `label.style_cross`, etc. |
| `textalign` | `text.align_left`, `text.align_center`, `text.align_right` |
| `text_font_family` | `font.family_default`, `font.family_monospace` |

### Setters

`label.set_x()`, `label.set_y()`, `label.set_xy()`, `label.set_text()`, `label.set_color()`, `label.set_textcolor()`, `label.set_style()`, `label.set_size()`, `label.set_tooltip()`, `label.set_textalign()`, `label.set_xloc()`, `label.set_yloc()`, `label.set_point()`, `label.set_text_font_family()`

### Other

`label.get_x()`, `label.get_y()`, `label.get_text()`, `label.delete(id)`, `label.copy(id)`, `label.all`

**Limits:** Default max 50; set `max_labels_count` (max 500).

---

## Boxes (`box.*`)

### `box.new(left, top, right, bottom, border_color, border_width, border_style, extend, xloc, bgcolor, text, text_size, text_color, text_halign, text_valign, text_wrap, text_font_family, force_overlay)`

Draws a rectangle.

### Setters

`box.set_left()`, `box.set_top()`, `box.set_right()`, `box.set_bottom()`, `box.set_lefttop()`, `box.set_rightbottom()`, `box.set_border_color()`, `box.set_border_width()`, `box.set_border_style()`, `box.set_bgcolor()`, `box.set_extend()`, `box.set_text()`, etc.

### Other

`box.get_left()`, `box.get_top()`, `box.get_right()`, `box.get_bottom()`, `box.delete(id)`, `box.copy(id)`, `box.all`

**Limits:** Default max 50; set `max_boxes_count` (max 500).

---

## Tables (`table.*`)

### `table.new(position, columns, rows, bgcolor, frame_color, frame_width, border_color, border_width, force_overlay)`

| Position Constants |
|---|
| `position.top_left`, `position.top_center`, `position.top_right` |
| `position.middle_left`, `position.middle_center`, `position.middle_right` |
| `position.bottom_left`, `position.bottom_center`, `position.bottom_right` |

### `table.cell(table_id, column, row, text, width, height, text_color, text_halign, text_valign, text_size, bgcolor, tooltip, text_font_family)`

### Cell Setters

`table.cell_set_text()`, `table.cell_set_bgcolor()`, `table.cell_set_text_color()`, `table.cell_set_text_size()`, `table.cell_set_tooltip()`, `table.cell_set_text_halign()`, `table.cell_set_text_valign()`, `table.cell_set_text_font_family()`

### Table Setters

`table.set_position()`, `table.set_bgcolor()`, `table.set_frame_color()`, `table.set_frame_width()`, `table.set_border_color()`, `table.set_border_width()`

### Other

`table.delete(id)`, `table.clear(table_id, from_column, to_column, from_row, to_row)`, `table.all`

**Performance tip:** Use `var` for table creation, fill only on `barstate.islast`:

```pine
var t = table.new(position.top_right, 2, 2)
if barstate.islast
    table.cell(t, 0, 0, "Header", bgcolor=color.gray)
    table.cell(t, 0, 1, str.tostring(close))
```

---

## Polylines (`polyline.*`)

### `polyline.new(points, curved, closed, xloc, line_color, fill_color, line_style, line_width, force_overlay)`

Draws a multi-point line/polygon from an array of `chart.point` objects.

```pine
points = array.new<chart.point>()
points.push(chart.point.from_index(bar_index - 10, high))
points.push(chart.point.from_index(bar_index, low))
polyline.new(points, line_color=color.blue)
```

### Chart Points

| Constructor | Description |
|-------------|-------------|
| `chart.point.new(time, index, price)` | Full constructor |
| `chart.point.from_index(index, price)` | From bar_index |
| `chart.point.from_time(time, price)` | From UNIX time |
| `chart.point.now(price)` | Current bar |

### Other

`polyline.delete(id)`, `polyline.all`

**Limits:** Default max 50; set `max_polylines_count` (max 100).

---

## Linefills (`linefill.*`)

### `linefill.new(line1, line2, color)`

Fills the space between two lines.

`linefill.set_color()`, `linefill.get_line1()`, `linefill.get_line2()`, `linefill.delete()`, `linefill.all`

---

## Drawing Limits Summary

| Object | Default Max | Max Settable |
|--------|------------|--------------|
| Lines | 50 | 500 |
| Labels | 50 | 500 |
| Boxes | 50 | 500 |
| Tables | 50 | 50 |
| Polylines | 50 | 100 |

Set via `indicator()`/`strategy()` params: `max_lines_count`, `max_labels_count`, `max_boxes_count`, `max_polylines_count`.
