# NumPy and pandas Essentials

**Prerequisites:** [lists, dicts and comprehensions](../../00-foundations/python-fundamentals/04-strings-lists-dicts-sets.md), [generators and functional tools](../generators-functional/README.md), [performance and memory](../performance-profiling/README.md), [relational SQL](../../05-databases/relational-sql/README.md) (`GROUP BY`, joins). **You will learn:** why **NumPy** arrays are fast (vectorization, contiguous typed memory), **shapes, indexing, broadcasting and views**, and the traps (dtype overflow, floating point); then **pandas** for tabular data: loading CSV, selecting and filtering, missing values, `groupby`, `pivot_table`, `merge` and time-based resampling, with the SQL equivalents. Both are third-party packages (`pip install numpy pandas`); every example was run and the outputs shown are real (pandas prints can differ slightly between versions).

## 1. In plain words

Python lists are flexible but slow for number crunching: each element is a full Python object, and each addition goes through the interpreter. **NumPy** stores numbers in one **contiguous block of typed memory** and runs loops in compiled C. You write whole-array expressions (`a * 2 + b`), and NumPy does the loop for you, often **50 to 100 times faster**. **pandas** builds on NumPy to give labelled, spreadsheet-like tables (**DataFrames**) with the operations analysts need: filter, group, join, summarise.

```
Python list:  [ptr] -> int object      NumPy array:  | 1 | 2 | 3 | 4 | 5 |   one block, one dtype
              [ptr] -> int object                    operations run in C over the block
```

## 2. NumPy arrays: shape, dtype and vectorized math

```python
import numpy as np

a = np.array([[1, 2, 3], [4, 5, 6]])
print(a.shape, a.dtype, a.ndim, a.size)          # shape = (rows, columns)
# (2, 3) int64 2 6
print(a * 10)                                    # one expression, applied to every element
# [[10 20 30]
#  [40 50 60]]
print(a + np.array([100, 200, 300]))             # broadcasting: the row is added to EVERY row of a
# [[101 202 303]
#  [104 205 306]]
```

**Broadcasting** lets arrays of different shapes combine when their shapes are compatible (compare shapes from the right: each pair of sizes must be equal or one of them 1). It replaces Python loops with a single expression and no copying.

**Reductions** (`sum`, `mean`, `max`, ...) collapse an axis: `axis=0` collapses **down the rows** (one result per column), `axis=1` collapses **across the columns** (one result per row).

```python
print(a.sum(), a.sum(axis=0), a.sum(axis=1), a.mean(axis=0))
# 21 [5 7 9] [ 6 15] [2.5 3.5 4.5]
```

Creating arrays:

```python
print(np.arange(0, 10, 3), np.linspace(0, 1, 5))
# [0 3 6 9] [0.   0.25 0.5  0.75 1.  ]
print(np.zeros((2, 2)), np.eye(2), sep="\n")
# [[0. 0.]
#  [0. 0.]]
# [[1. 0.]
#  [0. 1.]]

rng = np.random.default_rng(42)                  # a seeded generator: reproducible "random" numbers
print(rng.integers(0, 10, size=5), rng.normal(size=3).round(3))
# [0 7 6 4 4] [ 0.941 -1.951 -1.302]
```

## 3. Indexing, slicing, masks and the view trap

```python
print(a[:, 1], a[1, :])                          # a column, a row
# [2 5] [4 5 6]
print(a[a > 2])                                  # a boolean mask keeps the elements where the condition is True
# [3 4 5 6]
```

**Slices are views, not copies:** they share memory with the original, so changing one changes the other. This is fast but surprising. Use `.copy()` when you want independence.

```python
view = a[:, :2]
view[0, 0] = 99                                  # writes through to a!
print(a[0, 0])
# 99

independent = a[:, :2].copy()
independent[0, 0] = -1                           # does not touch a
print(a[0, 0])
# 99
```

(Fancy indexing with a list of positions or a boolean mask, by contrast, returns a **copy**.)

## 4. Why it is fast: measuring

```python
import time

x = np.arange(1_000_000)

start = time.perf_counter()
python_total = sum(int(v) * int(v) for v in x)          # a Python-level loop over a million items
t_loop = time.perf_counter() - start

start = time.perf_counter()
numpy_total = int((x * x).sum())                         # the same sum of squares, vectorized
t_vec = time.perf_counter() - start

print("same answer:", python_total == numpy_total, "| vectorized is more than 10x faster:", t_loop / t_vec > 10)
# same answer: True | vectorized is more than 10x faster: True
print(x.nbytes, "bytes in the array")                    # 1,000,000 elements x 8 bytes, with no per-element objects
# 8000000 bytes in the array
```

(On a typical laptop the ratio is around 50x to 100x.) Rules: **avoid Python `for` loops over array elements**; express the operation on whole arrays; and remember vectorized expressions create temporary arrays (memory), so for huge data process in chunks.

## 5. Traps: dtypes and floating point

Every array has a single **dtype**, and fixed-size integers **wrap around silently** instead of raising an error:

```python
small = np.array([1, 2, 3], dtype=np.int8)               # 8-bit integers: range -128 to 127
print(small * 100)                                       # 2*100 = 200 does not fit
# [100 -56  44]
```

Floats are inexact (as in plain Python): compare with a tolerance.

```python
print(0.1 + 0.2 == 0.3, np.isclose(0.1 + 0.2, 0.3))
# False True
```

Linear algebra is available too: `@` is matrix multiplication, `np.linalg.inv`, `np.linalg.solve` and friends.

```python
m = np.array([[2, 0], [0, 3]])
print(m @ np.array([1, 1]), np.linalg.inv(m).round(3).tolist())
# [2 3] [[0.5, 0.0], [0.0, 0.333]]
```

## 6. pandas: Series and DataFrames

A **DataFrame** is a table: labelled columns (each a typed **Series**), and an index. Real data usually arrives as CSV; here it is inline so the example is self-contained.

```python
import io
import pandas as pd

csv = """date,region,product,units,price
2026-01-03,North,pen,10,1.5
2026-01-03,South,book,2,12.0
2026-01-04,North,book,1,12.0
2026-01-05,East,pen,,1.5
2026-01-05,South,pen,7,1.5
2026-01-06,North,mug,3,4.0
"""
df = pd.read_csv(io.StringIO(csv), parse_dates=["date"])      # use pd.read_csv("file.csv") for a real file
print(df.to_string())
#         date region product  units  price
# 0 2026-01-03  North     pen   10.0    1.5
# 1 2026-01-03  South    book    2.0   12.0
# 2 2026-01-04  North    book    1.0   12.0
# 3 2026-01-05   East     pen    NaN    1.5
# 4 2026-01-05  South     pen    7.0    1.5
# 5 2026-01-06  North     mug    3.0    4.0
print(df["units"].dtype, "(float because one value is missing: NaN)")
# float64 (float because one value is missing: NaN)
```

First things to do with any new data: `df.head()`, `df.info()`, `df.describe()`, `df.isna().sum()` (missing values per column) and `df["col"].value_counts()`.

### Missing values, new columns

```python
df["units"] = df["units"].fillna(0).astype(int)               # decide explicitly how to treat missing data
df["revenue"] = df["units"] * df["price"]                     # a new column from vectorized arithmetic
print(df[["region", "units", "revenue"]].to_string())
#   region  units  revenue
# 0  North     10     15.0
# 1  South      2     24.0
# 2  North      1     12.0
# 3   East      0      0.0
# 4  South      7     10.5
# 5  North      3     12.0
```

Missing data needs a decision, not a default: `fillna(0)`, `dropna()`, filling with a mean or carrying the last value (`ffill`) each tell a different story. Never let `NaN` slip silently into totals.

### Selecting and filtering

`df["col"]` selects a column; `df.loc[rows, cols]` selects by **label or boolean mask**; `df.iloc[rows, cols]` selects by **position**. A boolean condition filters rows (the pandas `WHERE`):

```python
print(df[df["revenue"] > 10][["date", "region", "revenue"]].to_string())
#         date region  revenue
# 0 2026-01-03  North     15.0
# 1 2026-01-03  South     24.0
# 2 2026-01-04  North     12.0
# 4 2026-01-05  South     10.5
# 5 2026-01-06  North     12.0
print(df.loc[df["product"] == "pen", "units"].mean())          # filter rows, pick a column, then aggregate
# 5.666666666666667
```

Combine conditions with `&` and `|` and **parentheses**: `df[(df.units > 2) & (df.region == "North")]` (not `and`/`or`).

### Group, aggregate, pivot (SQL `GROUP BY`)

```python
by_region = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
print(by_region.to_string())
# region
# North    39.0
# South    34.5
# East      0.0

summary = df.groupby(["region", "product"]).agg(units=("units", "sum"), revenue=("revenue", "sum"))
print(summary.to_string())
#                 units  revenue
# region product                
# East   pen          0      0.0
# North  book         1     12.0
#        mug          3     12.0
#        pen         10     15.0
# South  book         2     24.0
#        pen          7     10.5

print(df.pivot_table(index="region", columns="product", values="revenue", aggfunc="sum", fill_value=0).to_string())
# product  book   mug   pen
# region                   
# East      0.0   0.0   0.0
# North    12.0  12.0  15.0
# South    24.0   0.0  10.5
```

The SQL equivalent of the first query is `SELECT region, SUM(revenue) FROM df GROUP BY region ORDER BY 2 DESC`. The pattern is **split, apply, combine**: split rows into groups, apply an aggregate to each, combine the results.

### Joins (`merge`) and time series

```python
managers = pd.DataFrame({"region": ["North", "South", "East"], "manager": ["Ana", "Bo", "Cy"]})
joined = df.merge(managers, on="region", how="left")          # SQL LEFT JOIN
print(joined[["region", "manager"]].drop_duplicates().to_string())
#   region manager
# 0  North     Ana
# 1  South      Bo
# 3   East      Cy

daily = df.set_index("date").resample("D")["revenue"].sum()   # total per calendar day
print(daily.to_string())
# date
# 2026-01-03    39.0
# 2026-01-04    12.0
# 2026-01-05    10.5
# 2026-01-06    12.0
# Freq: D
print(df["date"].dt.day_name().tolist())                       # the .dt accessor exposes date parts
# ['Saturday', 'Saturday', 'Sunday', 'Monday', 'Monday', 'Tuesday']
print(df["product"].value_counts().to_string())
# product
# pen     3
# book    2
# mug     1
```

`merge` supports `how="inner" | "left" | "right" | "outer"` and checks for duplicate keys with `validate="one_to_one"` (worth using: an accidental many-to-many join multiplies rows silently).

## 7. pandas habits that keep code fast and correct

- **Vectorize.** Operate on whole columns (`df["a"] * df["b"]`), not row by row. `df.apply(f, axis=1)` and `iterrows()` are Python loops in disguise and can be 100x slower.
- **Chain, don't mutate in place:** `df.assign(revenue=...).query("revenue > 10").sort_values("revenue")` reads like a recipe and avoids the infamous `SettingWithCopyWarning`; use `.loc` for assignment (`df.loc[mask, "col"] = value`).
- **Check shapes and uniqueness after joins and filters** (`len(df)` before and after).
- **Use proper dtypes:** dates as `datetime64`, repeated strings as `category`, integers as ints, not strings. Smaller dtypes mean less memory.
- **Mind memory:** `pd.read_csv(..., usecols=[...], dtype={...}, chunksize=100_000)` for big files; for data larger than memory consider Polars, DuckDB (SQL over files) or a database.
- **Know the SQL alternative:** for data already in a database, push filtering and aggregation into SQL ([database access lesson](../database-access/01-sqlalchemy-and-database-access.md)) and pull only the result with `pd.read_sql`.
- **Reproducibility:** pin library versions; seed random generators; keep raw data unchanged and do cleaning in code.

## 8. Common mistakes

- Python loops over arrays or DataFrame rows when a vectorized form exists.
- Mutating a view and unknowingly changing the original array.
- Integer dtype overflow in small dtypes; comparing floats with `==`.
- Forgetting parentheses around conditions combined with `&` and `|`.
- Averaging averages (a mean of group means is not the overall mean unless the groups have equal size).
- Silent `NaN` propagation, or `fillna(0)` where zero is a meaningful value.
- Duplicated join keys exploding row counts.
- Chained indexing (`df[df.a > 1]["b"] = 0`) that assigns to a temporary copy.
- Reading a huge CSV fully into memory without `usecols`/`dtype`/`chunksize`.
- Drawing conclusions from data you have not looked at (always inspect, plot and sanity-check).

## 9. Two real-world examples

**Example 1: The month-end report.** An analyst spent two days a month copying data between spreadsheets. A 40-line pandas script read the sales exports, merged them with the price list, grouped revenue by region and product, flagged rows with missing prices and wrote the result to Excel; the same script runs in seconds every month and the logic is reviewable in git.

**Example 2: The speed-up.** A data pipeline computed a risk score with a Python loop over 5 million rows and took 40 minutes. Rewriting the formula as column arithmetic and `np.where` for the conditional cases cut it to 6 seconds, with identical output (checked with `np.allclose` against the old result on a sample).

## 10. Practice

1. Without a loop, compute the mean of every column of a `(1000, 5)` array of random numbers and the index of the maximum in each row.
2. Use broadcasting to standardise each column of `a = np.array([[1., 2.], [3., 6.], [5., 10.]])` to mean 0 and standard deviation 1 (subtract the column mean, divide by the column standard deviation).
3. Create two views of the same array and show a change through one appears in the other. How do you prove two arrays share memory? (`np.shares_memory`)
4. On the sales `df`, find the product with the highest total revenue and the region with the highest average units per order.
5. Add a column `weekday` and compute the total revenue for each weekday, listing Monday first.
6. Explain why `df.groupby("region")["revenue"].mean().mean()` can differ from `df["revenue"].mean()`.

<details>
<summary>Solutions</summary>

1. ```python
   rng = np.random.default_rng(0)
   data = rng.random((1000, 5))
   col_means = data.mean(axis=0)
   row_argmax = data.argmax(axis=1)
   print(col_means.shape, row_argmax.shape, bool(0.45 < col_means.min() and col_means.max() < 0.55))
   # (5,) (1000,) True
   ```
2. ```python
   a2 = np.array([[1., 2.], [3., 6.], [5., 10.]])
   z = (a2 - a2.mean(axis=0)) / a2.std(axis=0)       # (3,2) minus (2,) broadcasts across rows
   print(z.round(3).tolist(), z.mean(axis=0).round(6).tolist())
   # [[-1.225, -1.225], [0.0, 0.0], [1.225, 1.225]] [0.0, 0.0]
   ```
3. ```python
   base = np.arange(6)
   v1, v2 = base[:4], base[2:]
   v1[2] = 100
   print(v2[0], np.shares_memory(v1, v2))
   # 100 True
   ```
4. ```python
   print(df.groupby("product")["revenue"].sum().idxmax(), df.groupby("region")["units"].mean().idxmax())
   # book North
   ```
   (Book: 24 + 12 = 36, pen: 25.5. North's average of 4.67 units beats South's 4.5 and East's 0.)
5. ```python
   order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
   df["weekday"] = df["date"].dt.day_name()
   print(df.groupby("weekday")["revenue"].sum().reindex(order).dropna().to_string())
   # weekday
   # Monday      10.5
   # Tuesday     12.0
   # Saturday    39.0
   # Sunday      12.0
   ```
6. The mean of group means gives every **group** equal weight, while `df["revenue"].mean()` gives every **row** equal weight. They differ whenever the groups have different sizes (North has three rows and East only one).

</details>

## 11. Check yourself

1. Why is a NumPy array faster than a list for numeric work?
2. What does `axis=0` mean in `a.sum(axis=0)`?
3. What is broadcasting?
4. What is the difference between a view and a copy, and which operations give which?
5. What does `groupby` do conceptually?
6. How do you filter rows by two conditions in pandas?
7. Why avoid `apply(axis=1)` and `iterrows()`?

<details>
<summary>Answers</summary>

1. Contiguous typed memory with no per-element objects, and loops run in compiled code.
2. Collapse down the rows, giving one result per column.
3. Combining arrays of different but compatible shapes by virtually stretching the smaller one, with no explicit loop or copy.
4. A view shares memory with the original (basic slicing); a copy is independent (`.copy()`, fancy indexing, boolean masks).
5. Split rows into groups by key, apply an aggregate to each group, and combine the results.
6. `df[(cond1) & (cond2)]`, with parentheses around each condition (use `|` for or).
7. They run a Python-level loop over rows; vectorized column operations are typically orders of magnitude faster.

</details>

[Back to Modern Python](../README.md)
