# CTEs, Recursive Queries and Window Functions Lab

**Prerequisites:** [SQL first steps](01-sql-first-steps.md), [aggregation and joins](02-aggregation-and-joins-lab.md). **You will learn:** how to structure big queries with **CTEs** (`WITH`), how to walk hierarchies with **recursive CTEs**, and how **window functions** compute rankings, running totals, previous/next values and percentages **without collapsing rows**; plus `CASE` (conditional logic and pivots), **set operations** (`UNION`, `INTERSECT`, `EXCEPT`), **gaps-and-islands**, and SQLite date functions. All queries use the shared dataset [`sample-data.sql`](../sample-data.sql) and run as written.

## 1. Setup

```python
import sqlite3, pathlib

db = sqlite3.connect(":memory:")
db.executescript(pathlib.Path("05-databases/sample-data.sql").read_text())      # run from the handbook's root folder

def q(sql, *params):
    return db.execute(sql, params).fetchall()

print(q("SELECT id, name, department_id, manager_id, salary, hired_on FROM employees ORDER BY id LIMIT 3"))
# [(1, 'Amina', 1, None, 9000, '2019-03-01'), (2, 'Bilal', 1, 1, 7000, '2020-06-15'), (3, 'Chen', 1, 1, 7000, '2021-01-10')]
```

## 2. CTEs: name a sub-result and build on it

A **common table expression (CTE)** is a named, temporary result defined with `WITH` and used in the query that follows. It reads like defining a variable before using it, which makes long queries readable top to bottom instead of nested inside out.

Question: *which employees earn more than their department's average?*

```python
print(q("""
    WITH dept_avg AS (                                      -- step 1: average salary per department
        SELECT department_id, AVG(salary) AS avg_salary
        FROM employees
        GROUP BY department_id
    )
    SELECT e.name, e.salary, ROUND(d.avg_salary) AS dept_average
    FROM employees e
    JOIN dept_avg d ON d.department_id = e.department_id    -- step 2: compare each employee with their department
    WHERE e.salary > d.avg_salary
    ORDER BY e.name
"""))
# [('Amina', 9000, 7667.0), ('Dana', 6000, 5250.0), ('Farah', 4000, 3750.0)]
```

You can chain several CTEs, each using the earlier ones:

```python
print(q("""
    WITH order_totals AS (
        SELECT o.id AS order_id, o.customer_id, SUM(i.quantity * i.unit_price) AS total
        FROM orders o JOIN order_items i ON i.order_id = o.id
        WHERE o.status <> 'cancelled'
        GROUP BY o.id
    ),
    customer_totals AS (
        SELECT customer_id, COUNT(*) AS orders, SUM(total) AS spent FROM order_totals GROUP BY customer_id
    )
    SELECT c.name, ct.orders, ct.spent
    FROM customer_totals ct JOIN customers c ON c.id = ct.customer_id
    ORDER BY ct.spent DESC
"""))
# [('Umbrella', 1, 2400), ('Globex', 2, 1350), ('Acme Ltd', 2, 420)]
```

Use a CTE when the same intermediate result is needed twice, when a query has several stages, or simply to give a name to an idea. (In PostgreSQL 12+ and SQLite a simple CTE is inlined like a subquery; semantics, not speed, are the reason to use it.)

## 3. Recursive CTEs: loops and hierarchies in SQL

A **recursive CTE** has two parts joined by `UNION ALL`: an **anchor** (the starting rows) and a **recursive step** that refers to the CTE itself, repeated until it produces no new rows.

### Generating a sequence

```python
print(q("""
    WITH RECURSIVE n(i) AS (
        SELECT 1                                  -- anchor: start at 1
        UNION ALL
        SELECT i + 1 FROM n WHERE i < 5           -- recursive step: add one, stop at 5
    )
    SELECT i, i * i AS square FROM n
"""))
# [(1, 1), (2, 4), (3, 9), (4, 16), (5, 25)]
```

(The `WHERE i < 5` is the **termination condition**; without it the query would run forever.)

### Walking a hierarchy: the org chart

`employees.manager_id` points at another employee. Starting from people with no manager, repeatedly add their direct reports:

```python
print(q("""
    WITH RECURSIVE chain(id, name, level, path) AS (
        SELECT id, name, 0, name FROM employees WHERE manager_id IS NULL               -- anchor: the top of each tree
        UNION ALL
        SELECT e.id, e.name, c.level + 1, c.path || ' > ' || e.name                     -- step: reports of people already found
        FROM employees e JOIN chain c ON e.manager_id = c.id
    )
    SELECT level, path FROM chain ORDER BY path
"""))
# [(0, 'Amina'), (1, 'Amina > Bilal'), (1, 'Amina > Chen'), (0, 'Dana'), (1, 'Dana > Eli'), (0, 'Farah'), (1, 'Farah > Gus'), (0, 'Hana')]
```

Typical uses: **org charts, category trees, bill-of-materials, comment threads, folder structures, graph reachability** ("everyone below this manager", "all ancestors of this category"). It is the SQL version of the [tree and graph traversals](../../02-data-structures/graphs/01-graph-basics-bfs-dfs.md) you wrote in Python.

## 4. Window functions: calculate across rows without collapsing them

`GROUP BY` squeezes many rows into one. A **window function** computes something over a *window* of related rows but **keeps every row**, adding the result as a new column. The shape:

```sql
function(...) OVER (
    PARTITION BY column     -- restart the calculation for each group (like GROUP BY, but rows stay)
    ORDER BY column         -- order of rows inside the window
    ROWS BETWEEN ...        -- optional: exactly which rows the window covers
)
```

### Ranking: ROW_NUMBER, RANK, DENSE_RANK

```python
rows = q("""
    SELECT name, salary, department_id,
           ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC, name) AS rn,
           RANK()       OVER (PARTITION BY department_id ORDER BY salary DESC)       AS rnk,
           DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC)       AS dense
    FROM employees
    WHERE department_id IS NOT NULL
    ORDER BY department_id, rn
""")
for r in rows:
    print(r)
# ('Amina', 9000, 1, 1, 1, 1)
# ('Bilal', 7000, 1, 2, 2, 2)
# ('Chen', 7000, 1, 3, 2, 2)      Bilal and Chen tie at 7000
# ('Dana', 6000, 2, 1, 1, 1)
# ('Eli', 4500, 2, 2, 2, 2)
# ('Farah', 4000, 3, 1, 1, 1)
# ('Gus', 3500, 3, 2, 2, 2)
```

| Function | Behavior on ties (the two 7000 salaries) |
|----------|------------------------------------------|
| `ROW_NUMBER()` | always unique: 2, 3 (order between ties is arbitrary unless you add a tie-breaker like `name`) |
| `RANK()` | ties share a rank and **leave a gap** afterwards: 2, 2, then 4 |
| `DENSE_RANK()` | ties share a rank, **no gap**: 2, 2, then 3 |

**Always add a tie-breaker** (`ORDER BY salary DESC, name`) to `ROW_NUMBER`, or results can differ between runs and databases.

### Top N per group (the most-asked window query)

Rank inside each group, then keep rank 1 (a window function cannot be used directly in `WHERE`, so wrap it):

```python
print(q("""
    SELECT name, department_id, salary FROM (
        SELECT name, department_id, salary,
               ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC, name) AS rn
        FROM employees WHERE department_id IS NOT NULL
    ) WHERE rn = 1
    ORDER BY department_id
"""))
# [('Amina', 1, 9000), ('Dana', 2, 6000), ('Farah', 3, 4000)]       the highest earner of each department
```

Without windows you would need a correlated subquery or a self join; this form is clearer and faster.

### Running totals and moving averages

With `ORDER BY` inside `OVER`, an aggregate becomes cumulative. `ROWS BETWEEN ...` chooses the window frame.

```python
for r in q("""
    SELECT name, salary,
           SUM(salary) OVER (ORDER BY hired_on, id)                                             AS running_payroll,
           ROUND(AVG(salary) OVER (ORDER BY hired_on, id ROWS BETWEEN 1 PRECEDING AND CURRENT ROW)) AS avg_last_two
    FROM employees
    ORDER BY hired_on, id
"""):
    print(r)
# ('Dana', 6000, 6000, 6000.0)
# ('Amina', 9000, 15000, 7500.0)
# ('Bilal', 7000, 22000, 8000.0)
# ('Farah', 4000, 26000, 5500.0)
# ('Chen', 7000, 33000, 5500.0)
# ('Eli', 4500, 37500, 5750.0)
# ('Hana', 5000, 42500, 4750.0)
# ('Gus', 3500, 46000, 4250.0)
```

`running_payroll` is the payroll cost as people were hired, in hiring order. `avg_last_two` averages the current row with the one before it (a 2-row **moving average**; `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` gives a 7-day moving average over daily data).

The same pattern on sales data: cumulative revenue by day.

```python
print(q("""
    SELECT ordered_on,
           SUM(i.quantity * i.unit_price)                                    AS day_total,
           SUM(SUM(i.quantity * i.unit_price)) OVER (ORDER BY ordered_on)    AS cumulative        -- a window over an aggregate
    FROM orders o JOIN order_items i ON i.order_id = o.id
    WHERE o.status <> 'cancelled'
    GROUP BY ordered_on
    ORDER BY ordered_on
"""))
# [('2024-01-05', 120, 120), ('2024-02-11', 300, 420), ('2024-02-14', 50, 470), ('2024-03-20', 1300, 1770), ('2024-03-25', 2400, 4170)]
```

### LAG and LEAD: look at the previous or next row

```python
for r in q("""
    SELECT name, hired_on,
           LAG(name)  OVER (ORDER BY hired_on, id) AS hired_before_them,
           LEAD(name) OVER (ORDER BY hired_on, id) AS hired_after_them
    FROM employees
    ORDER BY hired_on, id LIMIT 4
"""):
    print(r)
# ('Dana', '2018-09-20', None, 'Amina')
# ('Amina', '2019-03-01', 'Dana', 'Bilal')
# ('Bilal', '2020-06-15', 'Amina', 'Farah')
# ('Farah', '2020-11-05', 'Bilal', 'Chen')
```

`NULL` appears at the edges (nothing before the first row). Real uses: **change from the previous period** (`revenue - LAG(revenue) OVER (ORDER BY month)`), time since a customer's previous order, detecting a status change.

```python
print(q("""
    SELECT customer_id, ordered_on,
           CAST(julianday(ordered_on) - julianday(LAG(ordered_on) OVER (PARTITION BY customer_id ORDER BY ordered_on)) AS INTEGER) AS days_since_previous
    FROM orders ORDER BY customer_id, ordered_on
"""))
# [(1, '2024-01-05', None), (1, '2024-02-11', 37), (2, '2024-02-14', None), (2, '2024-03-20', 35), (3, '2024-03-02', None), (4, '2024-03-25', None)]
```

### Share of the total, FIRST_VALUE and NTILE

```python
print(q("""SELECT name, salary, ROUND(100.0 * salary / SUM(salary) OVER (PARTITION BY department_id), 1) AS pct_of_department
           FROM employees WHERE department_id = 1 ORDER BY salary DESC, name"""))
# [('Amina', 9000, 39.1), ('Bilal', 7000, 30.4), ('Chen', 7000, 30.4)]

print(q("""SELECT name, salary, FIRST_VALUE(name) OVER (PARTITION BY department_id ORDER BY salary DESC) AS top_earner
           FROM employees WHERE department_id = 2 ORDER BY salary DESC"""))
# [('Dana', 6000, 'Dana'), ('Eli', 4500, 'Dana')]

print(q("""SELECT name, NTILE(3) OVER (ORDER BY salary DESC) AS tier FROM employees ORDER BY salary DESC, name"""))
# [('Amina', 1), ('Bilal', 1), ('Chen', 1), ('Dana', 2), ('Hana', 2), ('Eli', 2), ('Farah', 3), ('Gus', 3)]
```

`NTILE(n)` splits the ordered rows into `n` near-equal buckets (quartiles, deciles, percentile groups).

### Window function cheat sheet

| Function | Gives |
|----------|-------|
| `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()` | position within the partition |
| `SUM/AVG/COUNT/MIN/MAX(...) OVER (...)` | running or group-wide aggregates kept per row |
| `LAG(col, n)`, `LEAD(col, n)` | value `n` rows before / after |
| `FIRST_VALUE`, `LAST_VALUE`, `NTH_VALUE` | a specific row's value in the frame |
| `NTILE(n)` | bucket number (1 to `n`) |
| `PERCENT_RANK`, `CUME_DIST` | relative position (0 to 1) |

Remember: **window functions run after `WHERE`, `GROUP BY` and `HAVING`**, which is why you cannot filter on them in the same `SELECT`'s `WHERE`; wrap the query in a subquery or CTE and filter outside (as in "top N per group").

## 5. CASE: conditional logic and pivots

`CASE` is SQL's if/else. It works in `SELECT`, `ORDER BY`, `WHERE` and inside aggregates.

```python
print(q("""SELECT name, CASE WHEN salary >= 7000 THEN 'senior' WHEN salary >= 4500 THEN 'mid' ELSE 'junior' END AS band
           FROM employees ORDER BY salary DESC, name"""))
# [('Amina', 'senior'), ('Bilal', 'senior'), ('Chen', 'senior'), ('Dana', 'mid'), ('Hana', 'mid'), ('Eli', 'mid'), ('Farah', 'junior'), ('Gus', 'junior')]
```

**Pivot (rows to columns)** with conditional aggregation: count orders by status per country as columns:

```python
print(q("""
    SELECT c.country,
           SUM(CASE WHEN o.status = 'shipped'   THEN 1 ELSE 0 END) AS shipped,
           SUM(CASE WHEN o.status = 'pending'   THEN 1 ELSE 0 END) AS pending,
           SUM(CASE WHEN o.status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled
    FROM orders o JOIN customers c ON c.id = o.customer_id
    GROUP BY c.country ORDER BY c.country
"""))
# [('PK', 2, 0, 0), ('UK', 1, 0, 0), ('US', 1, 1, 1)]
```

This "conditional aggregation" trick is the portable way to build cross-tab reports in every database.

## 6. Set operations

Combine the **results of two queries** that have the same number of compatible columns.

| Operator | Result |
|----------|--------|
| `UNION` | rows in either query, **duplicates removed** |
| `UNION ALL` | rows in either, duplicates kept (faster; use when duplicates are impossible or wanted) |
| `INTERSECT` | rows in **both** |
| `EXCEPT` | rows in the first but **not** the second |

```python
print(q("SELECT name FROM customers WHERE country = 'PK' UNION SELECT name FROM customers WHERE country = 'US' ORDER BY 1"))
# [('Acme Ltd',), ('Globex',), ('Hooli',), ('Initech',)]
print(q("SELECT customer_id FROM orders INTERSECT SELECT id FROM customers WHERE country = 'US'"))        # customers who ordered AND are in the US
# [(2,), (3,)]
print(q("SELECT id FROM customers EXCEPT SELECT customer_id FROM orders"))                                # customers who never ordered
# [(5,)]
```

## 7. Gaps and islands

A classic pattern: find **runs of consecutive values**. Subtract the row number from the value: within a run of consecutive numbers the difference is constant, so grouping by it yields one group per run (an "island").

```python
print(q("""
    WITH t(d) AS (SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 9)
    SELECT MIN(d) AS run_start, MAX(d) AS run_end, COUNT(*) AS length
    FROM (SELECT d, d - ROW_NUMBER() OVER (ORDER BY d) AS grp FROM t)
    GROUP BY grp
    ORDER BY run_start
"""))
# [(1, 3, 3), (5, 6, 2), (9, 9, 1)]
```

Uses: **login streaks** ("longest run of consecutive days with activity"), uptime intervals, sequence gaps (missing invoice numbers).

## 8. Dates in SQLite (and the traps)

```python
print(q("SELECT date('2024-01-31', '+1 month'), strftime('%w', '2024-03-25'), julianday('2024-03-25') - julianday('2024-01-05')"))
# [('2024-03-02', '1', 80.0)]
```

- `date('2024-01-31', '+1 month')` gives `2024-03-02`: SQLite adds a month and **overflows** (31 January plus one month is "31 February", which becomes 2 March). Month arithmetic needs care in every database.
- `strftime('%w', ...)` gives the weekday (0 = Sunday), so 25 March 2024 (a Monday) is `'1'`.
- `julianday(a) - julianday(b)` is the number of days between two dates.
- Store dates as **ISO text** (`YYYY-MM-DD`) so they sort and compare correctly; keep times in **UTC**; other databases have real `DATE`/`TIMESTAMP` types and `INTERVAL` arithmetic.

## 9. Writing readable, correct analytical SQL

1. Start from the **question in words**, then name each step (CTEs).
2. Build up **one stage at a time** and print intermediate results.
3. For each join ask "how many rows per row?" (the [join multiplication pitfall](02-aggregation-and-joins-lab.md)).
4. Use a **window function** when you want the detail rows *and* a group figure; use **GROUP BY** when you only want the summary.
5. Always add **tie-breakers** to orderings used for ranking and pagination.
6. Check **NULL** behavior at every boundary (`LAG` on the first row, `AVG` over missing values).
7. Look at the **plan** if it is slow ([indexes lab](../indexes-query-plans/01-indexes-lab.md)).

## 10. Two real-world examples

**Example 1: A retention report.** "For each customer, how many days passed between consecutive orders, and what is the running total of their spending?" is `LAG` plus a windowed `SUM ... PARTITION BY customer`. The same report with self-joins and correlated subqueries is several times longer and slower.

**Example 2: A category tree on an e-commerce site.** Categories reference a parent category. A recursive CTE returns "this category and all its descendants" in one query, which powers breadcrumbs and "show all products under Electronics".

## 11. Common mistakes

- Filtering on a window function in the same query's `WHERE` (wrap it in a subquery or CTE).
- `ROW_NUMBER` without a tie-breaker (non-deterministic results and unstable pagination).
- Forgetting `PARTITION BY` and getting one global ranking.
- A recursive CTE without a termination condition (infinite loop) or on data with cycles (use `UNION` instead of `UNION ALL`, or track visited ids and a depth limit).
- Confusing `RANK` (gaps) with `DENSE_RANK` (no gaps).
- Using `UNION` when `UNION ALL` is enough (the dedupe sort costs time) or the reverse (duplicates sneak in).
- Relying on the default window frame: with `ORDER BY` the default is `RANGE ... CURRENT ROW`, which treats tied rows as one group; state `ROWS BETWEEN ...` explicitly when it matters.
- Assuming month arithmetic is safe at month ends.

## 12. Practice

1. Using a CTE, list customers whose total spend on shipped orders exceeds the average customer total.
2. Show each employee with the **highest salary in their department** as an extra column (a window function, not a join).
3. Rank all employees by salary company-wide with `DENSE_RANK`, and list those ranked 2 or 3.
4. For each order, show the order total and the **percentage of its customer's total** (windows over a grouped CTE).
5. Use a recursive CTE to list the numbers 1 to 10 and their running sum.
6. List every employee with the **chain of managers above them** (their path from the top).
7. Find customers who have orders but **no shipped** order (`EXCEPT`).
8. Find, per department, employees earning above the department average using a window function instead of a CTE join.

<details>
<summary>Solutions</summary>

1. ```python
   print(q("""WITH totals AS (SELECT o.customer_id, SUM(i.quantity * i.unit_price) AS spent
                             FROM orders o JOIN order_items i ON i.order_id = o.id WHERE o.status = 'shipped' GROUP BY o.customer_id)
              SELECT c.name, t.spent FROM totals t JOIN customers c ON c.id = t.customer_id
              WHERE t.spent > (SELECT AVG(spent) FROM totals) ORDER BY t.spent DESC"""))
   # [('Umbrella', 2400)]          the average of the three shipped totals (420, 1300, 2400) is about 1373, so Globex's 1300 falls just below it
   ```
2. ```python
   print(q("""SELECT name, salary, MAX(salary) OVER (PARTITION BY department_id) AS dept_max FROM employees
              WHERE department_id IS NOT NULL ORDER BY department_id, salary DESC, name LIMIT 3"""))
   # [('Amina', 9000, 9000), ('Bilal', 7000, 9000), ('Chen', 7000, 9000)]
   ```
3. ```python
   print(q("""SELECT name, salary, r FROM (SELECT name, salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS r FROM employees)
              WHERE r IN (2, 3) ORDER BY r, name"""))
   # [('Bilal', 7000, 2), ('Chen', 7000, 2), ('Dana', 6000, 3)]
   ```
4. ```python
   print(q("""WITH t AS (SELECT o.id AS order_id, o.customer_id, SUM(i.quantity * i.unit_price) AS total
                        FROM orders o JOIN order_items i ON i.order_id = o.id WHERE o.status <> 'cancelled' GROUP BY o.id)
              SELECT order_id, customer_id, total, ROUND(100.0 * total / SUM(total) OVER (PARTITION BY customer_id), 1) AS pct
              FROM t ORDER BY order_id"""))
   # [(1, 1, 120, 28.6), (2, 1, 300, 71.4), (3, 2, 50, 3.7), (5, 2, 1300, 96.3), (6, 4, 2400, 100.0)]
   ```
5. ```python
   print(q("""WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < 10)
              SELECT i, SUM(i) OVER (ORDER BY i) AS running FROM n"""))
   # [(1, 1), (2, 3), (3, 6), (4, 10), (5, 15), (6, 21), (7, 28), (8, 36), (9, 45), (10, 55)]
   ```
6. The recursive CTE of section 3 builds exactly this path (`'Amina > Bilal'`). To list each employee's *management chain upward*, start from the employee and join to `manager_id` instead:
   ```python
   print(q("""WITH RECURSIVE up(id, name, boss_id, chain) AS (
                  SELECT id, name, manager_id, name FROM employees WHERE name = 'Gus'
                  UNION ALL
                  SELECT m.id, m.name, m.manager_id, up.chain || ' <- ' || m.name FROM employees m JOIN up ON m.id = up.boss_id)
              SELECT chain FROM up ORDER BY length(chain) DESC LIMIT 1"""))
   # [('Gus <- Farah',)]
   ```
7. ```python
   print(q("SELECT customer_id FROM orders EXCEPT SELECT customer_id FROM orders WHERE status = 'shipped'"))
   # [(3,)]      Initech has only a cancelled order
   ```
8. ```python
   print(q("""SELECT name, salary FROM (SELECT name, salary, AVG(salary) OVER (PARTITION BY department_id) AS avg_sal
                                        FROM employees WHERE department_id IS NOT NULL)
              WHERE salary > avg_sal ORDER BY name"""))
   # [('Amina', 9000), ('Dana', 6000), ('Farah', 4000)]
   ```

</details>

## 13. Check yourself

1. What does a CTE give you that a nested subquery does not?
2. What are the two parts of a recursive CTE and what stops it?
3. How does a window function differ from `GROUP BY`?
4. `ROW_NUMBER` versus `RANK` versus `DENSE_RANK` on ties?
5. Why do you need a subquery to filter on a window function?
6. What does `LAG` return for the first row of a partition?
7. How do you pivot rows into columns portably?

<details>
<summary>Answers</summary>

1. A name and top-to-bottom readability; it can be reused more than once in the query and chained in stages.
2. An anchor query (starting rows) and a recursive step joined with `UNION ALL`; it stops when the step produces no new rows (so include a termination condition such as `WHERE i < 5`, or a depth limit).
3. `GROUP BY` collapses rows into one per group; a window function keeps every row and adds a computed column over its window.
4. `ROW_NUMBER` always gives unique numbers (arbitrary among ties unless broken); `RANK` gives ties the same number and skips ahead afterwards; `DENSE_RANK` gives ties the same number without gaps.
5. Window functions are evaluated after `WHERE`, so the value does not exist yet when `WHERE` runs; compute it in an inner query or CTE, then filter outside.
6. `NULL` (there is no previous row), unless you give a default as the third argument.
7. Conditional aggregation: `SUM(CASE WHEN condition THEN 1 ELSE 0 END)` per desired column, grouped by the row key.

</details>

[Back to relational model and SQL](README.md) · Previous: [aggregation and joins lab](02-aggregation-and-joins-lab.md)
