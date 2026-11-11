# Data with NumPy and pandas: One-Page Summary

## Questions worth remembering

- **Why is a NumPy array faster than a list for numeric work?** Contiguous typed memory with no per-element objects, and loops run in compiled code.
- **What does `axis=0` mean in `a.sum(axis=0)`?** Collapse down the rows, giving one result per column.
- **What is broadcasting?** Combining arrays of different but compatible shapes by virtually stretching the smaller one, with no explicit loop or copy.
- **What is the difference between a view and a copy, and which operations give which?** A view shares memory with the original (basic slicing); a copy is independent (`.copy()`, fancy indexing, boolean masks).
- **What does `groupby` do conceptually?** Split rows into groups by key, apply an aggregate to each group, and combine the results.
- **How do you filter rows by two conditions in pandas?** `df[(cond1) & (cond2)]`, with parentheses around each condition (use `|` for or).

Practice problems with solutions are in the **Practice** section of each lesson.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [NumPy and pandas Essentials](01-numpy-and-pandas-essentials.md)
