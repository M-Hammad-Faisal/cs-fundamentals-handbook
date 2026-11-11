# Data with NumPy and pandas: One-Page Summary

## Key facts

- **ndarray:** one dtype, fixed shape, operations run in C; replace Python loops with vectorized expressions. Broadcasting aligns shapes from the right: dimensions must match or be 1.
- **Axes:** `axis=0` runs down the rows (one result per column), `axis=1` runs across columns (one result per row).
- **Views and copies:** basic slices are views that share memory (`np.shares_memory`); boolean masks and fancy indexing return copies; use `.copy()` when you need independence.
- **dtype traps:** fixed-width integers wrap around on overflow; `float64` carries about 15 digits; `np.nan` spreads through sums, so use `nanmean` and `np.isclose`.
- **pandas shapes:** a `Series` is a labelled column, a `DataFrame` a table; select with `df["col"]`, `.loc` (labels or masks) and `.iloc` (positions); filter with `df[df["units"] > 2]`.
- **Everyday verbs:** `groupby(...).agg`, `merge` (a SQL join), `pivot_table`, `value_counts`, `isna`, `fillna`, `sort_values`, and `.dt` for dates.
- **Habits:** prefer vectorized columns over `iterrows`, assign with `.loc`, read only the columns and dtypes you need.

## Pitfalls

- Changing a view and silently changing the original array.
- Chained assignment (`df[mask]["x"] = 1`) writes to a temporary copy: use `df.loc[mask, "x"] = 1`.
- Looping with `iterrows` or `apply` where a vectorized expression exists.
- A single missing value turning an integer column into floats.
- Averaging averages: the mean of group means differs from the overall mean when groups have different sizes.
- Loading a huge CSV whole instead of using `usecols`, `dtype` or `chunksize`.

## Self-check

- **Why is a NumPy array faster than a list for numeric work?** Contiguous typed memory with no per-element objects, and loops run in compiled code.
- **What does `axis=0` mean in `a.sum(axis=0)`?** Collapse down the rows, giving one result per column.
- **What is broadcasting?** Combining arrays of different but compatible shapes by virtually stretching the smaller one, with no explicit loop or copy.
- **What is the difference between a view and a copy, and which operations give which?** A view shares memory with the original (basic slicing); a copy is independent (`.copy()`, fancy indexing, boolean masks).
- **What does `groupby` do conceptually?** Split rows into groups by key, apply an aggregate to each group, and combine the results.
- **How do you filter rows by two conditions in pandas?** `df[(cond1) & (cond2)]`, with parentheses around each condition (use `|` for or).

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [NumPy and pandas Essentials](01-numpy-and-pandas-essentials.md)
