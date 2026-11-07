# Aggregation and Joins Lab

**Prerequisites:** [SQL first steps](01-sql-first-steps.md). **You will learn:** how to summarize data with **aggregate functions**, **`GROUP BY`** and **`HAVING`**; how to combine tables with **`INNER`, `LEFT`, self and cross joins**; how to find rows that have **no match** (anti-joins); the most common **join pitfall** (inflated counts); and how to write **subqueries and `EXISTS`**. All queries run on the shared dataset [`sample-data.sql`](../sample-data.sql) (departments, employees, customers, orders, order items).

## 1. Setup

```python
import sqlite3, pathlib

db = sqlite3.connect(":memory:")
db.executescript(pathlib.Path("05-databases/sample-data.sql").read_text())      # run from the handbook's root folder

def q(sql, *params):
    return db.execute(sql, params).fetchall()

print(q("SELECT * FROM departments"))
# [(1, 'Engineering'), (2, 'Sales'), (3, 'Support'), (4, 'Legal')]
```

The tables and how they connect:

```text
departments (id, name) <---- employees (id, name, department_id, manager_id, salary, hired_on)
                                     ^__ manager_id points back to employees.id (a self reference)

customers (id, name, country) <---- orders (id, customer_id, ordered_on, status) <---- order_items (order_id, product, quantity, unit_price)
```

Notice the **foreign keys**: `employees.department_id -> departments.id`, `orders.customer_id -> customers.id`, `order_items.order_id -> orders.id`. Joins follow these links.

## 2. Aggregate functions: many rows in, one value out

| Function | Result | Ignores NULLs? |
|----------|--------|----------------|
| `COUNT(*)` | number of rows | counts every row |
| `COUNT(col)` | rows where `col` is not NULL | yes |
| `COUNT(DISTINCT col)` | number of different non-NULL values | yes |
| `SUM`, `AVG`, `MIN`, `MAX` | the obvious | yes |

```python
print(q("SELECT COUNT(*), COUNT(department_id), AVG(salary), MIN(salary), MAX(salary), SUM(salary) FROM employees"))
# [(8, 7, 5750.0, 3500, 9000, 46000)]
```

Read it: 8 employees, but only 7 have a department (`Hana` has `NULL`), so `COUNT(department_id)` is 7. `AVG` divides by the non-NULL count, which can surprise you when a column has NULLs.

```python
print(q("SELECT COUNT(DISTINCT country) FROM customers"))              # [(3,)]
print(q("SELECT SUM(salary) FROM employees WHERE department_id = 99")) # [(None,)]    SUM of zero rows is NULL, not 0
print(q("SELECT COALESCE(SUM(salary), 0) FROM employees WHERE department_id = 99"))      # [(0,)]
```

## 3. GROUP BY: one result per group

`GROUP BY` splits the rows into groups that share a value, then applies the aggregates to **each group**.

```python
print(q("""
    SELECT department_id, COUNT(*) AS people, ROUND(AVG(salary), 1) AS avg_salary
    FROM employees
    GROUP BY department_id
    ORDER BY department_id
"""))
# [(None, 1, 5000.0), (1, 3, 7666.7), (2, 2, 5250.0), (3, 2, 3750.0)]
```

How to picture it:

```text
employees rows  ->  split by department_id  ->  one output row per group
 (3 rows dept 1)       [Amina, Bilal, Chen]     (1, 3, 7666.7)
 (2 rows dept 2)       [Dana, Eli]              (2, 2, 5250.0)
 (2 rows dept 3)       [Farah, Gus]             (3, 2, 3750.0)
 (1 row NULL)          [Hana]                   (None, 1, 5000.0)    NULLs form one group
```

**The golden rule:** every column in `SELECT` must either appear in `GROUP BY` or be inside an aggregate function. (SQLite is lenient and picks an arbitrary value; PostgreSQL rejects it. Follow the strict rule.)

```python
print(q("SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY status"))
# [('cancelled', 1), ('pending', 1), ('shipped', 4)]
print(q("SELECT strftime('%Y-%m', ordered_on) AS month, COUNT(*) FROM orders GROUP BY month"))
# [('2024-01', 1), ('2024-02', 2), ('2024-03', 3)]
print(q("SELECT product, SUM(quantity) AS units, SUM(quantity * unit_price) AS revenue FROM order_items GROUP BY product ORDER BY revenue DESC"))
# [('Laptop', 3, 3600), ('Monitor', 3, 900), ('Keyboard', 3, 150), ('Mouse', 6, 120)]
```

### HAVING versus WHERE

- **`WHERE`** filters **rows before** grouping.
- **`HAVING`** filters **groups after** aggregation (so it may use aggregate functions).

```python
print(q("SELECT department_id, COUNT(*) AS n FROM employees GROUP BY department_id HAVING COUNT(*) >= 2 ORDER BY department_id"))
# [(1, 3), (2, 2), (3, 2)]     groups of at least two employees

print(q("""SELECT d.name, ROUND(AVG(e.salary), 0) AS avg_salary
           FROM employees e JOIN departments d ON d.id = e.department_id
           WHERE e.hired_on >= '2019-01-01'          -- WHERE: only people hired in 2019 or later (row filter)
           GROUP BY d.id
           HAVING AVG(e.salary) > 5000               -- HAVING: keep only the high-paying groups
           ORDER BY d.id"""))
# [('Engineering', 7667.0)]
```

The `WHERE` removed Dana (hired in 2018) before grouping, which left Eli alone in Sales with an average of 4500, so `HAVING` dropped the Sales group too. Row filters first, group filters second.

## 4. Joins: combining tables

Data is split into tables to avoid repetition ([normalization](../normalization-schema-design/README.md)), so answering real questions means **joining** them back by matching key columns.

### INNER JOIN: only rows that match on both sides

```python
print(q("""
    SELECT d.name AS department, e.name AS employee
    FROM employees e
    INNER JOIN departments d ON d.id = e.department_id
    ORDER BY d.name, e.name
"""))
# [('Engineering', 'Amina'), ('Engineering', 'Bilal'), ('Engineering', 'Chen'), ('Sales', 'Dana'), ('Sales', 'Eli'), ('Support', 'Farah'), ('Support', 'Gus')]
```

`Hana` (no department) and `Legal` (no employees) are **missing**: an inner join keeps only matched pairs.

```text
employees e                 departments d
(Hana, dept NULL)  --X-->   no match         dropped
(Amina, dept 1)    ------>  (1, Engineering) kept
                            (4, Legal)        dropped: nobody points to it
```

### LEFT JOIN: keep every row of the left table

If there is no match, the right-side columns are `NULL`.

```python
print(q("SELECT e.name, d.name FROM employees e LEFT JOIN departments d ON d.id = e.department_id ORDER BY e.id"))
# [('Amina', 'Engineering'), ('Bilal', 'Engineering'), ('Chen', 'Engineering'), ('Dana', 'Sales'), ('Eli', 'Sales'), ('Farah', 'Support'), ('Gus', 'Support'), ('Hana', None)]
```

Now `Hana` appears with `None` for the department. To list **all departments including empty ones**, put departments on the left:

```python
print(q("""
    SELECT d.name, COUNT(e.id) AS headcount
    FROM departments d
    LEFT JOIN employees e ON e.department_id = d.id
    GROUP BY d.id
    ORDER BY d.id
"""))
# [('Engineering', 3), ('Sales', 2), ('Support', 2), ('Legal', 0)]
```

`COUNT(e.id)` counts non-NULL matches, so `Legal` gets 0. (`COUNT(*)` would wrongly give 1, counting the NULL-filled row.)

### Anti-join: rows with NO match

"Which customers never ordered?" Left join, then keep rows where the right side is `NULL`:

```python
print(q("""
    SELECT c.name
    FROM customers c
    LEFT JOIN orders o ON o.customer_id = c.id
    WHERE o.id IS NULL
"""))
# [('Hooli',)]
```

Two equivalent alternatives (the optimizer treats them similarly):

```python
print(q("SELECT name FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)"))        # [('Hooli',)]
print(q("SELECT name FROM customers WHERE id NOT IN (SELECT customer_id FROM orders)"))                              # [('Hooli',)]
```

Beware `NOT IN` when the subquery can return `NULL`: one `NULL` makes `NOT IN` return **no rows at all** (three-valued logic from the previous lesson). Prefer `NOT EXISTS`.

### Self join: a table joined to itself

`employees.manager_id` points at another row of the same table. Use **two aliases** of one table:

```python
print(q("""
    SELECT e.name AS employee, m.name AS manager
    FROM employees e
    LEFT JOIN employees m ON m.id = e.manager_id
    ORDER BY e.id
"""))
# [('Amina', None), ('Bilal', 'Amina'), ('Chen', 'Amina'), ('Dana', None), ('Eli', 'Dana'), ('Farah', None), ('Gus', 'Farah'), ('Hana', None)]
```

### Joining three tables

Revenue per order: follow `orders -> customers` and `orders -> order_items`.

```python
print(q("""
    SELECT o.id AS order_id, c.name AS customer, SUM(i.quantity * i.unit_price) AS total
    FROM orders o
    JOIN customers c   ON c.id = o.customer_id
    JOIN order_items i ON i.order_id = o.id
    GROUP BY o.id
    ORDER BY o.id
"""))
# [(1, 'Acme Ltd', 120), (2, 'Acme Ltd', 300), (3, 'Globex', 50), (4, 'Initech', 600), (5, 'Globex', 1300), (6, 'Umbrella', 2400)]
```

### CROSS JOIN: every combination

No condition: every row of one table paired with every row of the other (`8 * 4 = 32`). Rarely wanted by accident, occasionally useful for generating combinations.

```python
print(q("SELECT COUNT(*) FROM employees CROSS JOIN departments"))         # [(32,)]
print(q("SELECT COUNT(*) FROM employees, departments"))                   # [(32,)]   a comma with no WHERE is a cross join: a classic accident
```

### Other join types

| Join | Keeps | SQLite support |
|------|-------|----------------|
| `INNER JOIN` | matches only | yes |
| `LEFT JOIN` | all left + matches | yes |
| `RIGHT JOIN` | all right + matches | yes (3.39+); or just swap the table order and use `LEFT JOIN` |
| `FULL OUTER JOIN` | all rows from both | yes (3.39+); older versions: `UNION` of two left joins |

## 5. The classic pitfall: joins multiply rows

A join returns **one row per matching pair**. If one order has three line items, joining orders to items yields three rows for that order. Counting rows then **over-counts**:

```python
print(q("SELECT COUNT(*) FROM orders"))                                                               # [(6,)]
print(q("SELECT COUNT(*) FROM orders o JOIN order_items i ON i.order_id = o.id"))                     # [(8,)]    8 pairs, not 6 orders!

print(q("SELECT c.name, COUNT(o.id)  FROM customers c JOIN orders o ON o.customer_id = c.id GROUP BY c.id ORDER BY c.id"))
# [('Acme Ltd', 2), ('Globex', 2), ('Initech', 1), ('Umbrella', 1)]              correct: orders per customer
print(q("SELECT c.name, COUNT(*)     FROM customers c JOIN orders o ON o.customer_id = c.id JOIN order_items i ON i.order_id = o.id GROUP BY c.id ORDER BY c.id"))
# [('Acme Ltd', 3), ('Globex', 3), ('Initech', 1), ('Umbrella', 1)]              WRONG: it counted item rows (Acme has 2 orders, 3 items)
print(q("SELECT c.name, COUNT(DISTINCT o.id) FROM customers c JOIN orders o ON o.customer_id = c.id JOIN order_items i ON i.order_id = o.id GROUP BY c.id ORDER BY c.id"))
# [('Acme Ltd', 2), ('Globex', 2), ('Initech', 1), ('Umbrella', 1)]              fixed with COUNT(DISTINCT ...)
```

Rule: **after each join, ask "how many rows does this join produce per row I already had?"** If more than one, aggregate carefully (`COUNT(DISTINCT ...)`, or pre-aggregate the many-side in a subquery before joining).

A realistic report combining several ideas: revenue per customer, excluding cancelled orders, including customers with no orders:

```python
print(q("""
    SELECT c.name,
           COUNT(DISTINCT o.id)                       AS orders,
           COALESCE(SUM(i.quantity * i.unit_price), 0) AS revenue
    FROM customers c
    LEFT JOIN orders o      ON o.customer_id = c.id AND o.status <> 'cancelled'    -- the condition goes in ON, not WHERE
    LEFT JOIN order_items i ON i.order_id = o.id
    GROUP BY c.id
    ORDER BY revenue DESC, c.name
"""))
# [('Umbrella', 1, 2400), ('Globex', 2, 1350), ('Acme Ltd', 2, 420), ('Hooli', 0, 0), ('Initech', 0, 0)]
```

**`ON` versus `WHERE` with outer joins:** putting `o.status <> 'cancelled'` in `WHERE` would turn the `LEFT JOIN` into an inner join (rows with `NULL` order status are filtered out), dropping customers with no qualifying orders (`Hooli`, `Initech`). Conditions on the *optional* side belong in `ON`.

## 6. Subqueries and EXISTS

A **subquery** is a query inside a query.

```python
# scalar subquery: returns one value
print(q("SELECT name FROM employees WHERE salary > (SELECT AVG(salary) FROM employees) ORDER BY name"))
# [('Amina',), ('Bilal',), ('Chen',), ('Dana',)]            earn more than the company average of 5750

# EXISTS: true when the subquery returns at least one row (it stops at the first match)
print(q("""SELECT name FROM customers c
           WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.status = 'shipped')
           ORDER BY name"""))
# [('Acme Ltd',), ('Globex',), ('Umbrella',)]
```

Use `EXISTS` for "is there at least one ...?" (it avoids the row multiplication pitfall), and `IN (subquery)` for membership tests. CTEs (`WITH ...`) and window functions, the next level, are in the [relational SQL reference](README.md).

## 7. Reading a query like the database does

```text
SELECT  c.name, COUNT(DISTINCT o.id), SUM(...)      5. compute the output columns
FROM    customers c                                  1. start with customers
LEFT JOIN orders o ON ...                            1. attach matching orders (NULLs if none)
LEFT JOIN order_items i ON ...                       1. attach matching items
WHERE   (none here)                                  2. filter rows
GROUP BY c.id                                        3. one group per customer
HAVING  (none here)                                  4. filter groups
ORDER BY revenue DESC                                7. sort
```

When a result looks wrong, **build the query up one clause at a time**: first just the join (look at the raw rows), then add the filter, then the grouping. Print intermediate results; it is the fastest way to find where rows multiplied or vanished.

```python
print(q("""SELECT c.name, o.id, i.product FROM customers c
           LEFT JOIN orders o ON o.customer_id = c.id
           LEFT JOIN order_items i ON i.order_id = o.id
           WHERE c.name = 'Acme Ltd' ORDER BY o.id"""))
# [('Acme Ltd', 1, 'Keyboard'), ('Acme Ltd', 1, 'Mouse'), ('Acme Ltd', 2, 'Monitor')]     three raw rows: this is why COUNT(*) said 3
```

## 8. Two real-world examples

**Example 1: Sales dashboard.** "Revenue per country per month" is `orders JOIN customers JOIN order_items`, grouped by `country` and `strftime('%Y-%m', ordered_on)`. The same query shape powers every business dashboard; BI tools generate exactly this SQL behind their drag-and-drop charts.

**Example 2: Data quality checks.** Anti-joins find broken data: "orders whose customer no longer exists" is `orders LEFT JOIN customers ... WHERE customers.id IS NULL`. Teams run such queries nightly to catch orphan records that missing foreign keys let through.

## 9. Common mistakes

- Selecting a non-aggregated column that is not in `GROUP BY`.
- Using `WHERE` for a condition on an aggregate (use `HAVING`).
- `COUNT(*)` on a left-joined table, which counts the NULL-filled row.
- Row multiplication through one-to-many joins, inflating `COUNT`/`SUM`.
- Putting the filter for the optional table of a `LEFT JOIN` in `WHERE` (turns it into an inner join).
- Forgetting the join condition (accidental cross join: millions of rows).
- `NOT IN` with a subquery that can return `NULL`.
- Comparing `AVG` of a column containing NULLs to a count of all rows without thinking.

## 10. Practice

1. How many employees earn at least 5000? What is their average salary?
2. List each department with its **highest** salary (use `GROUP BY`).
3. Show employees with their manager's name; employees without a manager should still appear.
4. Which customers have placed **no shipped** orders? (anti-join)
5. For each country, how many customers and how many orders (include countries whose customers have no orders)?
6. Why does `SELECT COUNT(*) FROM departments d LEFT JOIN employees e ON e.department_id = d.id` return 8, not 4?
7. Write the total revenue of **shipped** orders only.

<details>
<summary>Solutions</summary>

1. ```python
   print(q("SELECT COUNT(*), AVG(salary) FROM employees WHERE salary >= 5000"))              # [(5, 6800.0)]
   ```
2. ```python
   print(q("""SELECT d.name, MAX(e.salary) FROM departments d JOIN employees e ON e.department_id = d.id
              GROUP BY d.id ORDER BY d.id"""))                                               # [('Engineering', 9000), ('Sales', 6000), ('Support', 4000)]
   ```
3. ```python
   print(q("SELECT e.name, m.name FROM employees e LEFT JOIN employees m ON m.id = e.manager_id ORDER BY e.id")[:3])
   # [('Amina', None), ('Bilal', 'Amina'), ('Chen', 'Amina')]
   ```
4. ```python
   print(q("""SELECT c.name FROM customers c
              WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.status = 'shipped')
              ORDER BY c.name"""))                                                           # [('Hooli',), ('Initech',)]
   ```
5. ```python
   print(q("""SELECT c.country, COUNT(DISTINCT c.id) AS customers, COUNT(o.id) AS orders
              FROM customers c LEFT JOIN orders o ON o.customer_id = c.id
              GROUP BY c.country ORDER BY c.country"""))
   # [('PK', 2, 2), ('UK', 1, 1), ('US', 2, 3)]
   ```
6. Each department row is repeated once per matching employee (3 + 2 + 2 = 7 rows), and `Legal`, which has no employees, still appears once with NULLs: `7 + 1 = 8`. `COUNT(*)` counts joined rows, not departments (use `COUNT(DISTINCT d.id)` for 4). Hana does not appear because she has no department to match.
   ```python
   print(q("SELECT COUNT(*), COUNT(DISTINCT d.id) FROM departments d LEFT JOIN employees e ON e.department_id = d.id"))      # [(8, 4)]
   ```
7. ```python
   print(q("""SELECT SUM(i.quantity * i.unit_price) FROM orders o JOIN order_items i ON i.order_id = o.id
              WHERE o.status = 'shipped'"""))                                                # [(4120,)]
   ```

</details>

## 11. Check yourself

1. What is the difference between `COUNT(*)` and `COUNT(column)`?
2. When do you use `HAVING` instead of `WHERE`?
3. What does a `LEFT JOIN` return when there is no match?
4. How do you find rows in table A that have no match in table B?
5. Why can a join inflate `COUNT` and `SUM`?
6. Where should a condition on the optional side of a `LEFT JOIN` go?

<details>
<summary>Answers</summary>

1. `COUNT(*)` counts rows; `COUNT(column)` counts rows where that column is not NULL.
2. When the condition involves an aggregate (it filters groups after aggregation); `WHERE` filters rows before grouping.
3. The left row with `NULL` in every right-table column.
4. `LEFT JOIN ... WHERE b.key IS NULL`, or `NOT EXISTS (subquery)`.
5. A join returns one row per matching pair; a one-to-many join repeats the "one" side's row for each "many" row, so aggregates over it count repeats.
6. In the `ON` clause; in `WHERE` it filters out the NULL-filled rows and turns the join into an inner join.

</details>

[Back to relational model and SQL](README.md) · Previous: [SQL first steps](01-sql-first-steps.md)
