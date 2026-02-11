# PineScript v6 — Syntax Quick Reference

## Script Declaration

```pine
//@version=6
indicator("Title", overlay=true)                 // indicator
strategy("Title", overlay=true, ...)             // strategy
library("Title", overlay=true)                   // library
```

## Variable Declarations

```pine
float x = 1.5                  // re-declared each bar
var float x = 0.0              // initialized once, persists across bars
varip int ticks = 0            // persists across ticks (realtime)
x := x + 1                    // reassignment (not =, use :=)
```

## Type Qualifiers (weakest → strongest)

```
const  →  input  →  simple  →  series
```

A parameter expecting `simple` rejects `series`. Literals are `const`, `input.*()` returns are `input`, `syminfo.*` are `simple`, `close`/`ta.*` are `series`.

## Operators

| Category | Operators |
|----------|-----------|
| Arithmetic | `+`, `-`, `*`, `/`, `%` |
| Comparison | `==`, `!=`, `<`, `>`, `<=`, `>=` |
| Logical | `and`, `or`, `not` |
| Ternary | `condition ? trueVal : falseVal` |
| Assignment | `=` (declare), `:=` (reassign), `+=`, `-=`, `*=`, `/=`, `%=` |
| History | `close[1]` (1 bar back), `high[n]` |
| String concat | `"a" + "b"` |

## Conditional Structures

```pine
// if / else if / else
x = if cond1
    val1
else if cond2
    val2
else
    val3

// switch with expression
result = switch expr
    val1 => action1
    val2 => action2
    =>      default_action   // default case

// switch without expression (first true wins)
switch
    cond1 => action1
    cond2 => action2
```

## Loops

```pine
for i = start to end          // inclusive, step defaults to 1
for i = start to end by step
for [idx, val] in myArray     // iterate array
for row in myMatrix           // iterate matrix rows
while condition
    body
break                          // exit loop
continue                       // skip to next iteration
```

## Functions

```pine
// Single-expression
f(x, y) => x + y

// Multi-line (last expression = return value)
f(x, y) =>
    z = x * 2
    z + y

// Tuple return
f() =>
    [val1, val2]

// Tuple destructuring
[a, b] = f()

// Method (first param = receiver type)
method name(array<float> self, float val) =>
    self.push(val)
```

## Input Functions

| Function | Returns | Example |
|----------|---------|---------|
| `input.int()` | `input int` | `input.int(14, "Len", minval=1)` |
| `input.float()` | `input float` | `input.float(1.5, "Mult", step=0.1)` |
| `input.bool()` | `input bool` | `input.bool(true, "Show")` |
| `input.string()` | `input string` | `input.string("EMA", "Type", options=[...])` |
| `input.source()` | `series float` | `input.source(close, "Source")` |
| `input.color()` | `input color` | `input.color(color.red, "Color")` |
| `input.timeframe()` | `input string` | `input.timeframe("D", "TF")` |
| `input.session()` | `input string` | `input.session("0930-1600")` |

## Color

```pine
color c = color.red                      // built-in constant
color c = #FF0000                        // hex RGB
color c = #FF000080                      // hex RGBA (80 ≈ 50% transparent)
color c = color.new(color.red, 50)       // 0=opaque, 100=invisible
color c = color.rgb(255, 0, 0, 50)      // RGBA with 0-100 transp
```

## String Operations

```pine
str.tostring(value)                      // number → string
str.tostring(value, format.mintick)      // formatted
str.format("{0} is {1}", name, val)      // template
str.contains(str, substr)               // bool
str.replace_all(str, old, new)
str.length(str)
str.upper(str) / str.lower(str)
```

## na Handling

```pine
na(x)                    // true if x is na (NEVER use x == na)
nz(x)                   // replace na with 0
nz(x, replacement)      // replace na with custom value
fixnan(x)               // replace na with last non-na value
```

## Annotations (Documentation Comments)

```pine
//@version=6
//@description Library description
//@function    Function description
//@param name  Parameter description
//@returns     Return value description
//@variable    Variable description
//@type        UDT description
//@field       UDT field description
```

## User-Defined Types

```pine
type MyType
    float price = na
    int   count = 0
    string label = ""

obj = MyType.new(close, 1, "test")
obj.price  // field access
```

## Enum

```pine
enum Direction
    up   = "Up"
    down = "Down"
    flat = "Flat"

selected = input.enum(Direction.up, "Direction")
```

## Import / Export

```pine
import username/libraryName/version as alias
alias.functionName(args)

// In library:
export myFunc(series float src) =>
    src * 2
```
