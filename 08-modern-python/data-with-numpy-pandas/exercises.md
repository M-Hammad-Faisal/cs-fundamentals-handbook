# Data with NumPy and pandas: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## NumPy and pandas Essentials

1. Without a loop, compute the mean of every column of a `(1000, 5)` array of random numbers and the index of the maximum in each row.
2. Use broadcasting to standardise each column of `a = np.array([[1., 2.], [3., 6.], [5., 10.]])` to mean 0 and standard deviation 1 (subtract the column mean, divide by the column standard deviation).
3. Create two views of the same array and show a change through one appears in the other. How do you prove two arrays share memory? (`np.shares_memory`)
4. On the sales `df`, find the product with the highest total revenue and the region with the highest average units per order.
5. Add a column `weekday` and compute the total revenue for each weekday, listing Monday first.
6. Explain why `df.groupby("region")["revenue"].mean().mean()` can differ from `df["revenue"].mean()`.

<details>
<summary>Solutions</summary>

1. ```python no-run
   rng = np.random.default_rng(0)
   data = rng.random((1000, 5))
   col_means = data.mean(axis=0)
   row_argmax = data.argmax(axis=1)
   print(col_means.shape, row_argmax.shape, bool(0.45 < col_means.min() and col_means.max() < 0.55))
   # (5,) (1000,) True
   ```
2. ```python no-run
   a2 = np.array([[1., 2.], [3., 6.], [5., 10.]])
   z = (a2 - a2.mean(axis=0)) / a2.std(axis=0)       # (3,2) minus (2,) broadcasts across rows
   print(z.round(3).tolist(), z.mean(axis=0).round(6).tolist())
   # [[-1.225, -1.225], [0.0, 0.0], [1.225, 1.225]] [0.0, 0.0]
   ```
3. ```python no-run
   base = np.arange(6)
   v1, v2 = base[:4], base[2:]
   v1[2] = 100
   print(v2[0], np.shares_memory(v1, v2))
   # 100 True
   ```
4. ```python no-run
   print(df.groupby("product")["revenue"].sum().idxmax(), df.groupby("region")["units"].mean().idxmax())
   # book North
   ```
   (Book: 24 + 12 = 36, pen: 25.5. North's average of 4.67 units beats South's 4.5 and East's 0.)
5. ```python no-run
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
