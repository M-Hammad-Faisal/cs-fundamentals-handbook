# The Relational Model and SQL

## Detailed lessons (start here if you are new)

1. [SQL first steps](01-sql-first-steps.md): create, insert, select, filter, NULL, constraints, using SQLite from Python
2. [Aggregation and joins lab](02-aggregation-and-joins-lab.md): GROUP BY/HAVING, inner/left/self joins, anti-joins, the join-multiplication pitfall
3. [CTEs, recursive queries and window functions lab](03-ctes-and-window-functions-lab.md): ranking, running totals, LAG/LEAD, top-N per group, pivots, set operations, gaps and islands

The rest of this page is the quick reference.

All examples use the dataset in [`../sample-data.sql`](../sample-data.sql) (departments, employees, customers, orders, order items). Load it into SQLite and run every query yourself:

```bash
sqlite3 shop.db < 05-databases/sample-data.sql
sqlite3 -header -column shop.db "SELECT * FROM employees;"
```

## 1. The concept

A **relational database** stores data in **tables** (relations). A table has **columns** (attributes, each with a type) and **rows** (tuples, one record each). Tables are connected by **keys**, not by physical pointers. You describe *what* data you want with **SQL** (Structured Query Language), and the database engine decides *how* to get it.

### Keys

| Key | Meaning |
|-----|---------|
| **Primary key (PK)** | Uniquely identifies each row; never `NULL` |
| **Foreign key (FK)** | A column referencing another table's key; enforces valid relationships |
| **Unique key** | No two rows may share the value |
| **Composite key** | A key made of several columns (`order_items(order_id, product)`) |
| **Candidate key** | Any column set that could serve as the primary key |
| **Surrogate key** | An artificial ID (auto-increment, UUID) |
| **Natural key** | A real-world value (email, ISBN) |

### Relationship types

| Type | Example | Implemented by |
|------|---------|-----------------|
| One-to-many | One customer, many orders | FK on the "many" side (`orders.customer_id`) |
| Many-to-many | Orders and products | A junction table (`order_items`) |
| One-to-one | User and profile | FK with a unique constraint |

### Types of SQL statements

| Group | Purpose | Commands |
|-------|---------|----------|
| **DDL** (definition) | Define structure | `CREATE`, `ALTER`, `DROP` |
| **DML** (manipulation) | Change data | `INSERT`, `UPDATE`, `DELETE` |
| **DQL** (query) | Read data | `SELECT` |
| **TCL** (transaction control) | Group changes | `BEGIN`, `COMMIT`, `ROLLBACK` |
| **DCL** (control) | Permissions | `GRANT`, `REVOKE` |

## 2. Defining and changing data

```sql
CREATE TABLE products (
    id    INTEGER PRIMARY KEY,
    name  TEXT    NOT NULL UNIQUE,
    price INTEGER NOT NULL CHECK (price >= 0)
);

INSERT INTO products (name, price) VALUES ('Keyboard', 50), ('Mouse', 20);

UPDATE products SET price = price + 5 WHERE name = 'Mouse';

DELETE FROM products WHERE price > 1000;

ALTER TABLE products ADD COLUMN in_stock INTEGER NOT NULL DEFAULT 1;
```

**Constraints** (`NOT NULL`, `UNIQUE`, `CHECK`, `PRIMARY KEY`, `FOREIGN KEY`) make the database reject bad data, which is far safer than trusting every application to validate.

> Always give `UPDATE` and `DELETE` a `WHERE` clause. Without one they touch every row.

## 3. Reading data: SELECT

### Logical order of evaluation

You write `SELECT ... FROM ... WHERE ...`, but the database processes it in this order:

```
FROM / JOIN  ->  WHERE  ->  GROUP BY  ->  HAVING  ->  SELECT  ->  DISTINCT  ->  ORDER BY  ->  LIMIT
```

That explains why you cannot use a `SELECT` alias inside `WHERE` (it does not exist yet), but you can use it in `ORDER BY`.

### Filtering and sorting

```sql
SELECT name, salary
FROM employees
WHERE department_id = 1 AND salary >= 7000
ORDER BY salary DESC, name ASC
LIMIT 5;
```

Useful operators:

```sql
SELECT name FROM employees WHERE salary BETWEEN 4000 AND 6000;
SELECT name FROM employees WHERE name LIKE 'A%';           -- starts with A
SELECT name FROM employees WHERE department_id IN (1, 3);
SELECT name FROM employees WHERE manager_id IS NULL;       -- never "= NULL"
SELECT DISTINCT country FROM customers;
```

### NULL: the three-valued logic trap

`NULL` means *unknown*. Any comparison with `NULL` yields *unknown*, which `WHERE` treats as false.

```sql
SELECT name FROM employees WHERE department_id = NULL;     -- returns nothing (wrong)
SELECT name FROM employees WHERE department_id IS NULL;    -- Hana (right)
SELECT name, COALESCE(department_id, 0) AS dept FROM employees;   -- replace NULL
```

`NOT IN` with a list containing `NULL` returns no rows at all. Prefer `NOT EXISTS`.

## 4. Aggregation and grouping

Aggregate functions collapse many rows into one: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`.

```sql
SELECT COUNT(*) AS employees,
       AVG(salary) AS avg_salary,
       MAX(salary) AS top_salary
FROM employees;
```

`COUNT(*)` counts rows; `COUNT(col)` counts non-`NULL` values; `COUNT(DISTINCT col)` counts distinct non-`NULL` values.

### GROUP BY and HAVING

```sql
SELECT department_id, COUNT(*) AS headcount, AVG(salary) AS avg_salary
FROM employees
GROUP BY department_id
HAVING COUNT(*) >= 2
ORDER BY avg_salary DESC;
```

- `WHERE` filters **rows before** grouping.
- `HAVING` filters **groups after** aggregation.

Every selected column must be either in `GROUP BY` or inside an aggregate.

## 5. Joins

A **join** combines rows from two tables on a condition (usually primary key = foreign key).

| Join | Returns |
|------|---------|
| `INNER JOIN` | Only rows that match in both tables |
| `LEFT JOIN` | All rows from the left table, matched rows from the right (`NULL` when none) |
| `RIGHT JOIN` | Mirror of `LEFT JOIN` |
| `FULL OUTER JOIN` | All rows from both sides |
| `CROSS JOIN` | Every combination (cartesian product) |
| Self join | A table joined to itself |

```sql
-- INNER JOIN: employees that have a department
SELECT e.name, d.name AS department
FROM employees e
JOIN departments d ON d.id = e.department_id;

-- LEFT JOIN: all employees, department may be NULL (Hana)
SELECT e.name, d.name AS department
FROM employees e
LEFT JOIN departments d ON d.id = e.department_id;

-- Find rows with NO match (anti-join): customers without orders
SELECT c.name
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.id IS NULL;

-- Self join: each employee with their manager
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON m.id = e.manager_id;
```

### Joining several tables with aggregation

```sql
-- Revenue per customer for shipped orders
SELECT c.name,
       SUM(oi.quantity * oi.unit_price) AS revenue
FROM customers c
JOIN orders o       ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id   = o.id
WHERE o.status = 'shipped'
GROUP BY c.id, c.name
ORDER BY revenue DESC;
```

> **Join trap:** joining a "one" table to a "many" table repeats the "one" side's values. Summing a column from the repeated side inflates results. Aggregate first, or aggregate at the correct grain.

A `LEFT JOIN` followed by a `WHERE` on the right table's column silently turns it into an inner join; put such filters in the `ON` clause instead.

## 6. Subqueries and CTEs

A **subquery** is a query inside another query.

```sql
-- Scalar subquery: employees paid above the company average
SELECT name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- IN subquery: customers who placed at least one shipped order
SELECT name FROM customers
WHERE id IN (SELECT customer_id FROM orders WHERE status = 'shipped');

-- EXISTS: usually efficient, and NULL-safe
SELECT c.name
FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);

-- Correlated subquery: top earner per department
SELECT e.name, e.department_id, e.salary
FROM employees e
WHERE e.salary = (SELECT MAX(salary) FROM employees
                  WHERE department_id = e.department_id);
```

### Common Table Expressions (CTEs)

A **CTE** (`WITH`) names a subquery so complex queries read top to bottom.

```sql
WITH order_totals AS (
    SELECT o.id, o.customer_id, SUM(oi.quantity * oi.unit_price) AS total
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.id
    GROUP BY o.id, o.customer_id
)
SELECT c.name, AVG(ot.total) AS avg_order_value
FROM customers c
JOIN order_totals ot ON ot.customer_id = c.id
GROUP BY c.id, c.name;
```

### Recursive CTEs: hierarchies

```sql
-- Everyone who reports (directly or indirectly) to Amina
WITH RECURSIVE chain AS (
    SELECT id, name, manager_id, 0 AS depth FROM employees WHERE id = 1
    UNION ALL
    SELECT e.id, e.name, e.manager_id, chain.depth + 1
    FROM employees e
    JOIN chain ON e.manager_id = chain.id
)
SELECT name, depth FROM chain ORDER BY depth, name;
```

## 7. Window functions

A **window function** computes a value across a set of related rows **without collapsing them** (unlike `GROUP BY`).

```sql
-- Rank employees by salary within each department
SELECT name, department_id, salary,
       RANK()       OVER (PARTITION BY department_id ORDER BY salary DESC) AS rnk,
       ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC, name) AS rn
FROM employees
WHERE department_id IS NOT NULL;
```

| Function | Purpose |
|----------|---------|
| `ROW_NUMBER()` | Unique sequence 1, 2, 3 |
| `RANK()` | Ties share a rank; gaps follow (1, 1, 3) |
| `DENSE_RANK()` | Ties share a rank; no gaps (1, 1, 2) |
| `LAG(col)` / `LEAD(col)` | Value from the previous / next row |
| `SUM(col) OVER (...)` | Running totals and moving averages |
| `NTILE(n)` | Split into `n` buckets |

```sql
-- Running total of order values by date, and the change from the previous order
WITH order_totals AS (
    SELECT o.id, o.ordered_on, SUM(oi.quantity * oi.unit_price) AS total
    FROM orders o JOIN order_items oi ON oi.order_id = o.id
    GROUP BY o.id, o.ordered_on
)
SELECT ordered_on, total,
       SUM(total) OVER (ORDER BY ordered_on) AS running_total,
       total - LAG(total) OVER (ORDER BY ordered_on) AS change
FROM order_totals;

-- Top 1 per group: highest paid employee in each department
SELECT name, department_id, salary FROM (
    SELECT name, department_id, salary,
           ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn
    FROM employees WHERE department_id IS NOT NULL
) WHERE rn = 1;
```

## 8. Set operations and CASE

```sql
-- UNION removes duplicates, UNION ALL keeps them (and is faster)
SELECT country FROM customers WHERE country = 'PK'
UNION
SELECT country FROM customers WHERE country = 'US';

-- INTERSECT / EXCEPT
SELECT id FROM customers
EXCEPT
SELECT customer_id FROM orders;               -- customers with no orders

-- CASE: conditional logic in a query
SELECT name, salary,
       CASE WHEN salary >= 7000 THEN 'senior'
            WHEN salary >= 4500 THEN 'mid'
            ELSE 'junior' END AS band
FROM employees;

-- Conditional aggregation (pivot-style counts)
SELECT department_id,
       SUM(CASE WHEN salary >= 7000 THEN 1 ELSE 0 END) AS high_earners,
       COUNT(*) AS total
FROM employees
GROUP BY department_id;
```

## 9. Dates, strings and other useful functions

SQLite shown; PostgreSQL and MySQL have close equivalents with different names.

```sql
SELECT name,
       hired_on,
       strftime('%Y', hired_on)        AS hire_year,        -- extract part of a date
       length(name)                    AS name_length,
       upper(name)                     AS shouted,
       substr(name, 1, 2)              AS first_two,
       name || ' (' || salary || ')'   AS label             -- || concatenates
FROM employees
LIMIT 3;
```

## 10. Views

A **view** stores a query under a name, so you can reuse it like a table.

```sql
CREATE VIEW dept_stats AS
SELECT d.name AS department, COUNT(e.id) AS headcount, AVG(e.salary) AS avg_salary
FROM departments d
LEFT JOIN employees e ON e.department_id = d.id
GROUP BY d.id, d.name;

SELECT * FROM dept_stats ORDER BY headcount DESC;
```

Views simplify queries and restrict access to columns. **Materialized views** (PostgreSQL, Oracle) store the result physically and refresh on demand, trading freshness for speed.

## 11. Two real-world examples

### Example 1: Business reporting and dashboards

A weekly sales dashboard answers "revenue by country and month, plus each customer's rank". That is a join across orders, items and customers, a `GROUP BY` for the totals, and a window function for rankings. Analysts write exactly these queries (often with CTEs) against warehouses like BigQuery, Snowflake and Redshift. The skill transfers directly because they all speak SQL.

### Example 2: Application back ends and data integrity

An e-commerce back end stores customers, orders and items in related tables. **Foreign keys** guarantee that no order can reference a nonexistent customer, **`CHECK` constraints** reject negative quantities, and **unique constraints** prevent duplicate accounts, all enforced in the database even if three different services write to it. Fraud and support teams then query the same tables to find, for example, customers with several cancelled orders (`GROUP BY` plus `HAVING`).

## 12. Tips, tricks and pitfalls

- **Name your columns in `SELECT`;** avoid `SELECT *` in application code (it breaks when columns change and reads unneeded data).
- **Use `IS NULL`,** never `= NULL`. Beware `NOT IN` with `NULL`s; prefer `NOT EXISTS`.
- **Know `WHERE` vs `HAVING`:** rows before grouping vs groups after.
- **Aggregate at the right grain.** Joining one-to-many before `SUM` can double-count.
- **Use `LEFT JOIN ... WHERE right.id IS NULL`** (or `NOT EXISTS`) for "rows with no match".
- **Prefer `UNION ALL`** when duplicates are impossible or acceptable.
- **Index the columns you filter and join on** (see [indexes](../indexes-query-plans/README.md)).
- **Limit before you explore.** Use `LIMIT` on big tables while developing.
- **Parameterize queries** (`?` or `%s` placeholders) to prevent SQL injection; never build SQL by string concatenation with user input.
- **Be careful with integer division** (`5 / 2 = 2` in SQLite and PostgreSQL integer math); cast to a decimal when needed.
- **Store money as integers (cents) or `DECIMAL`,** never floats.
- **Dialect differences exist:** `LIMIT` vs `TOP`/`FETCH FIRST`, string concatenation, date functions, `ILIKE` (PostgreSQL), upserts.

## 13. Check yourself

1. What is the difference between a primary key and a foreign key?
2. In what order does the database logically evaluate the clauses of a `SELECT`?
3. Why does `WHERE x = NULL` return nothing, and what should you write instead?
4. What is the difference between `WHERE` and `HAVING`?
5. Explain `INNER`, `LEFT`, and `FULL OUTER` joins. How do you find rows with no match?
6. How does a window function differ from `GROUP BY`?
7. What is the difference between `RANK` and `DENSE_RANK`?
8. Why can `NOT IN` give surprising results, and what is the safer alternative?
9. What does a recursive CTE let you do?
10. How does a many-to-many relationship get stored?

<details>
<summary>Answers</summary>

1. A primary key uniquely identifies rows in its own table. A foreign key is a column that references another table's key and enforces that the referenced row exists.
2. `FROM`/`JOIN`, `WHERE`, `GROUP BY`, `HAVING`, `SELECT`, `DISTINCT`, `ORDER BY`, `LIMIT`.
3. Comparing anything to `NULL` yields unknown, which `WHERE` treats as false. Use `IS NULL` / `IS NOT NULL`.
4. `WHERE` filters individual rows before grouping; `HAVING` filters groups after aggregation.
5. Inner returns only matches; left returns all left rows plus matches (`NULL` where none); full outer returns all rows from both sides. Find non-matches with `LEFT JOIN ... WHERE right.key IS NULL` or `NOT EXISTS`.
6. Window functions compute over related rows but keep every row; `GROUP BY` collapses each group into one row.
7. `RANK` leaves gaps after ties (1, 1, 3); `DENSE_RANK` does not (1, 1, 2).
8. If the subquery returns any `NULL`, `x NOT IN (...)` is never true, so no rows come back. `NOT EXISTS` handles `NULL` correctly.
9. It lets a query reference its own output, so you can walk hierarchies and graphs such as org charts, category trees, and bills of materials.
10. With a junction table holding foreign keys to both sides (such as `order_items`, linking orders and products).

</details>
