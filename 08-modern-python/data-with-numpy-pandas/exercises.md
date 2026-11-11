# Data with NumPy and pandas: Exercises

These problems go with the [Data with NumPy and pandas lesson](README.md). Try each one before opening its solution.

<details>
<summary>Setup code the solutions use (copied from the lessons)</summary>

```python
import numpy as np
import pandas as pd
import io

a = np.array([[1, 2, 3], [4, 5, 6]])
print(a.shape, a.dtype, a.ndim, a.size)          # shape = (rows, columns)
# (2, 3) int64 2 6
print(a * 10)                                    # one expression, applied to every element
# [[10 20 30]
#  [40 50 60]]
print(a + np.array([100, 200, 300]))             # broadcasting: the row is added to EVERY row of a
# [[101 202 303]
#  [104 205 306]]


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

</details>

## Problems

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

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [NumPy and pandas Essentials](01-numpy-and-pandas-essentials.md)
