# The Relational Model and SQL: Exercises

These problems go with the [The Relational Model and SQL lesson](README.md). Try each one before opening its solution.

Load [`../sample-data.sql`](../sample-data.sql) and write each query yourself before opening the solution. Tables: `departments`, `employees`, `customers`, `orders`, `order_items`.

## Problems

### Basics
1. List the names and salaries of employees earning more than 5000, highest first.
2. List employees hired in 2020 or later, with their hire year.
3. Count employees per department (include only departments with at least 2).
4. Show employees who have **no** department.

### Joins
5. Show each employee with their department name (including employees without one).
6. Show each employee with their manager's name (managers may be `NULL`).
7. List customers who have **never** placed an order.
8. Show every department and how many employees it has, including empty ones (Legal).

### Aggregation and subqueries
9. Compute total revenue (`quantity * unit_price`) for **shipped** orders only.
10. Find customers whose total shipped revenue exceeds 500.
11. Find employees earning more than the average salary of **their own department**.
12. Find the second highest distinct salary.

### Window functions and CTEs
13. Rank employees by salary within each department, with ties sharing a rank.
14. For each order, show the order total and the running total ordered by date.
15. Show the highest-paid employee in each department using a window function.
16. Using a recursive CTE, list everyone under Amina with their depth in the hierarchy.

### Design
17. Write the `CREATE TABLE` statement for a `payments` table linked to `orders`, with sensible types and constraints (positive amount, required order).
18. Explain why `SELECT department_id, name, COUNT(*) FROM employees GROUP BY department_id` is invalid in standard SQL.

<details>
<summary>Solutions</summary>

```sql
-- 1
SELECT name, salary FROM employees WHERE salary > 5000 ORDER BY salary DESC;

-- 2
SELECT name, strftime('%Y', hired_on) AS hire_year
FROM employees WHERE hired_on >= '2020-01-01';

-- 3
SELECT department_id, COUNT(*) AS headcount
FROM employees
WHERE department_id IS NOT NULL
GROUP BY department_id
HAVING COUNT(*) >= 2;

-- 4
SELECT name FROM employees WHERE department_id IS NULL;

-- 5
SELECT e.name, d.name AS department
FROM employees e LEFT JOIN departments d ON d.id = e.department_id;

-- 6
SELECT e.name AS employee, m.name AS manager
FROM employees e LEFT JOIN employees m ON m.id = e.manager_id;

-- 7
SELECT c.name FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);

-- 8
SELECT d.name, COUNT(e.id) AS headcount
FROM departments d LEFT JOIN employees e ON e.department_id = d.id
GROUP BY d.id, d.name;

-- 9
SELECT SUM(oi.quantity * oi.unit_price) AS revenue
FROM orders o JOIN order_items oi ON oi.order_id = o.id
WHERE o.status = 'shipped';

-- 10
SELECT c.name, SUM(oi.quantity * oi.unit_price) AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id = o.id
WHERE o.status = 'shipped'
GROUP BY c.id, c.name
HAVING SUM(oi.quantity * oi.unit_price) > 500;

-- 11
SELECT e.name, e.salary
FROM employees e
WHERE e.salary > (SELECT AVG(salary) FROM employees
                  WHERE department_id = e.department_id);

-- 12
SELECT MAX(salary) FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);

-- 13
SELECT name, department_id, salary,
       DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rnk
FROM employees WHERE department_id IS NOT NULL;

-- 14
WITH order_totals AS (
    SELECT o.id, o.ordered_on, SUM(oi.quantity * oi.unit_price) AS total
    FROM orders o JOIN order_items oi ON oi.order_id = o.id
    GROUP BY o.id, o.ordered_on
)
SELECT id, ordered_on, total,
       SUM(total) OVER (ORDER BY ordered_on, id) AS running_total
FROM order_totals;

-- 15
SELECT name, department_id, salary FROM (
    SELECT name, department_id, salary,
           ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn
    FROM employees WHERE department_id IS NOT NULL
) WHERE rn = 1;

-- 16
WITH RECURSIVE chain AS (
    SELECT id, name, 0 AS depth FROM employees WHERE id = 1
    UNION ALL
    SELECT e.id, e.name, chain.depth + 1
    FROM employees e JOIN chain ON e.manager_id = chain.id
)
SELECT name, depth FROM chain ORDER BY depth, name;
```

```sql
-- 17 (new table, standalone)
CREATE TABLE payments (
    id         INTEGER PRIMARY KEY,
    order_id   INTEGER NOT NULL REFERENCES orders(id),
    amount     INTEGER NOT NULL CHECK (amount > 0),   -- cents
    paid_on    TEXT    NOT NULL,
    method     TEXT    NOT NULL CHECK (method IN ('card', 'bank', 'cash'))
);
```

**18.** `name` is neither in `GROUP BY` nor inside an aggregate, so there is no single value to return for each group. Select only `department_id` and aggregates, or add `name` to `GROUP BY` (which changes the grouping). SQLite and MySQL (in lenient mode) may accept it and return an arbitrary row's value, which hides the bug.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [SQL First Steps](01-sql-first-steps.md) · [Aggregation and Joins Lab](02-aggregation-and-joins-lab.md) · [CTEs, Recursive Queries and Window Functions Lab](03-ctes-and-window-functions-lab.md)
