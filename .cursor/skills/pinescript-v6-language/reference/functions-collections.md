# PineScript v6 — Collections Reference (Array, Map, Matrix)

## Arrays (`array.*`)

### Creation

```pine
array.new<float>(size, initial_value)    // typed constructor
array.new<int>(0)                         // empty int array
array.from(1, 2, 3, 4, 5)               // from literal values
float[] myArr = array.new<float>(0)      // type alias syntax
var array<float> persistent = array.new<float>(0)  // persists across bars
```

Type-specific constructors: `array.new_float()`, `array.new_int()`, `array.new_bool()`, `array.new_string()`, `array.new_color()`, `array.new_line()`, `array.new_label()`, `array.new_box()`, `array.new_table()`, `array.new_linefill()`

### Access & Modification

| Function | Returns | Description |
|----------|---------|-------------|
| `.get(index)` | element | Get element at index |
| `.set(index, value)` | `void` | Set element at index |
| `.push(value)` | `void` | Add to end |
| `.unshift(value)` | `void` | Add to beginning |
| `.insert(index, value)` | `void` | Insert at index |
| `.pop()` | element | Remove and return last element |
| `.shift()` | element | Remove and return first element |
| `.remove(index)` | element | Remove and return element at index |
| `.first()` | element | Get first element |
| `.last()` | element | Get last element |
| `.size()` | `int` | Number of elements |
| `.clear()` | `void` | Remove all elements |
| `.fill(value, from, to)` | `void` | Fill range with value |

### Search

| Function | Returns | Description |
|----------|---------|-------------|
| `.includes(value)` | `bool` | Check if contains value |
| `.indexof(value)` | `int` | Index of first occurrence (-1 if not found) |
| `.lastindexof(value)` | `int` | Index of last occurrence |
| `.binary_search(value)` | `int` | Binary search (sorted array) |
| `.binary_search_leftmost(value)` | `int` | Leftmost index in sorted array |
| `.binary_search_rightmost(value)` | `int` | Rightmost index in sorted array |

### Transformation

| Function | Returns | Description |
|----------|---------|-------------|
| `.sort(order)` | `void` | Sort in place. `order.ascending` (default) or `order.descending` |
| `.sort_indices(order)` | `array<int>` | Return sorted index array |
| `.reverse()` | `void` | Reverse in place |
| `.slice(from, to)` | `array` | Sub-array [from, to) |
| `.copy()` | `array` | Shallow copy |
| `.concat(other)` | `array` | Append another array |
| `.join(separator)` | `string` | Join elements into string |

### Aggregation

| Function | Returns | Description |
|----------|---------|-------------|
| `.sum()` | `float` | Sum of elements |
| `.avg()` | `float` | Average |
| `.min()` | element | Minimum value |
| `.max()` | element | Maximum value |
| `.median()` | `float` | Median |
| `.mode()` | element | Most frequent value |
| `.range()` | `float` | Max − min |
| `.stdev()` | `float` | Standard deviation |
| `.variance()` | `float` | Variance |
| `.covariance(other)` | `float` | Covariance with another array |
| `.percentrank(value)` | `float` | Percent rank |
| `.percentile_nearest_rank(pct)` | `float` | Percentile (nearest rank) |
| `.percentile_linear_interpolation(pct)` | `float` | Percentile (interpolated) |
| `.abs()` | `array` | Absolute values |
| `.standardize()` | `array<float>` | Standardized values (z-scores) |
| `.every()` | `bool` | True if all elements are truthy |
| `.some()` | `bool` | True if any element is truthy |

---

## Maps (`map.*`)

### Creation

```pine
map.new<string, float>()               // empty map
var myMap = map.new<int, string>()      // persistent map
```

Key types: `int`, `float`, `bool`, `string`, `color`, enum fields
Value types: any type including UDTs, arrays, etc.

### Operations

| Function | Returns | Description |
|----------|---------|-------------|
| `.put(key, value)` | previous value | Add/update key-value pair |
| `.get(key)` | value | Get value for key (na if not found) |
| `.contains(key)` | `bool` | Check if key exists |
| `.remove(key)` | value | Remove and return value |
| `.keys()` | `array<keyType>` | Array of all keys |
| `.values()` | `array<valueType>` | Array of all values |
| `.size()` | `int` | Number of entries |
| `.clear()` | `void` | Remove all entries |
| `.copy()` | `map` | Shallow copy |
| `.put_all(other)` | `void` | Merge another map into this one |

---

## Matrices (`matrix.*`)

### Creation

```pine
matrix.new<float>(rows, columns, initial_value)
matrix.new<int>(3, 3, 0)
var m = matrix.new<float>(2, 2, na)
```

### Access & Modification

| Function | Returns | Description |
|----------|---------|-------------|
| `.get(row, col)` | element | Get element |
| `.set(row, col, value)` | `void` | Set element |
| `.row(index)` | `array` | Get row as array |
| `.col(index)` | `array` | Get column as array |
| `.rows()` | `int` | Number of rows |
| `.columns()` | `int` | Number of columns |
| `.elements_count()` | `int` | Total elements |
| `.add_row(index, values)` | `void` | Insert row |
| `.add_col(index, values)` | `void` | Insert column |
| `.remove_row(index)` | `array` | Remove and return row |
| `.remove_col(index)` | `array` | Remove and return column |
| `.swap_rows(row1, row2)` | `void` | Swap two rows |
| `.swap_columns(col1, col2)` | `void` | Swap two columns |
| `.fill(value, from_row, to_row, from_col, to_col)` | `void` | Fill range |
| `.submatrix(from_row, to_row, from_col, to_col)` | `matrix` | Extract sub-matrix |
| `.reshape(rows, cols)` | `void` | Reshape matrix |

### Aggregation

| Function | Returns | Description |
|----------|---------|-------------|
| `.sum()` | `float` | Sum of all elements |
| `.avg()` | `float` | Average |
| `.min()` | element | Minimum |
| `.max()` | element | Maximum |
| `.median()` | `float` | Median |
| `.mode()` | element | Mode |

### Linear Algebra

| Function | Returns | Description |
|----------|---------|-------------|
| `.mult(other)` | `matrix` | Matrix multiplication |
| `.det()` | `float` | Determinant |
| `.inv()` | `matrix` | Inverse |
| `.pinv()` | `matrix` | Pseudo-inverse |
| `.transpose()` | `matrix` | Transpose |
| `.trace()` | `float` | Trace (sum of diagonal) |
| `.rank()` | `int` | Matrix rank |
| `.eigenvalues()` | `array<float>` | Eigenvalues |
| `.eigenvectors()` | `matrix` | Eigenvectors |
| `.pow(power)` | `matrix` | Matrix power |
| `.kron(other)` | `matrix` | Kronecker product |
| `.diff()` | `matrix` | Difference matrix |
| `.concat(other)` | `matrix` | Concatenate matrices |

### Boolean Tests

| Function | Returns | Description |
|----------|---------|-------------|
| `.is_square()` | `bool` | Square matrix? |
| `.is_identity()` | `bool` | Identity matrix? |
| `.is_diagonal()` | `bool` | Diagonal matrix? |
| `.is_antidiagonal()` | `bool` | Anti-diagonal? |
| `.is_symmetric()` | `bool` | Symmetric? |
| `.is_antisymmetric()` | `bool` | Anti-symmetric? |
| `.is_triangular()` | `bool` | Triangular? |
| `.is_stochastic()` | `bool` | Stochastic? |
| `.is_binary()` | `bool` | Binary (0/1 only)? |
| `.is_zero()` | `bool` | All zeros? |

### Other

| Function | Returns | Description |
|----------|---------|-------------|
| `.copy()` | `matrix` | Shallow copy |
| `.reverse()` | `void` | Reverse row order |
| `.sort(column, order)` | `void` | Sort by column |

---

## Method Syntax

All collection functions support dot-notation (method syntax):

```pine
arr = array.from(3, 1, 2)
arr.sort()              // method call
arr.push(4)             // method call
val = arr.get(0)        // method call

// Equivalent to:
array.sort(arr)
array.push(arr, 4)
val = array.get(arr, 0)
```
