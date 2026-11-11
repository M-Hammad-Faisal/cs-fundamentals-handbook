# The Relational Model and SQL: One-Page Summary

## Model
- Tables of rows and typed columns. **PK** identifies a row; **FK** references another table; **unique**, **composite**, **surrogate** vs **natural** keys.
- Relationships: 1-to-many (FK on the many side), many-to-many (junction table), 1-to-1 (FK + unique).
- Constraints (`NOT NULL`, `UNIQUE`, `CHECK`, `FOREIGN KEY`) enforce integrity in the database.

## Statement groups
DDL (`CREATE/ALTER/DROP`) · DML (`INSERT/UPDATE/DELETE`) · DQL (`SELECT`) · TCL (`BEGIN/COMMIT/ROLLBACK`) · DCL (`GRANT/REVOKE`).

## SELECT evaluation order
`FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT`

## Cheat sheet
| Need | Use |
|------|-----|
| Filter rows / groups | `WHERE` / `HAVING` |
| Missing values | `IS NULL`, `COALESCE` |
| Combine tables | `INNER`, `LEFT`, `FULL`, `CROSS`, self join |
| Rows with no match | `LEFT JOIN … WHERE r.id IS NULL` or `NOT EXISTS` |
| Per-group stats | `GROUP BY` + `COUNT/SUM/AVG/MIN/MAX` |
| Stats without collapsing rows | Window functions (`OVER (PARTITION BY … ORDER BY …)`) |
| Ranking | `ROW_NUMBER`, `RANK` (gaps), `DENSE_RANK` (no gaps) |
| Previous/next row | `LAG`, `LEAD` |
| Readable subqueries | `WITH` (CTE); `WITH RECURSIVE` for hierarchies |
| Conditional logic | `CASE WHEN … THEN … END` |
| Reusable query | `VIEW` (materialized view stores results) |

## Pitfalls
- `= NULL` never matches; `NOT IN` with `NULL` returns nothing (use `NOT EXISTS`).
- Joining one-to-many before `SUM` inflates totals.
- `LEFT JOIN` + `WHERE` on the right table acts like an inner join.
- `UPDATE`/`DELETE` without `WHERE`.
- `SELECT *` in application code.
- Build SQL with **parameters**, never string concatenation (SQL injection).
- Money: integers or `DECIMAL`, not floats.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [SQL First Steps](01-sql-first-steps.md) · [Aggregation and Joins Lab](02-aggregation-and-joins-lab.md) · [CTEs, Recursive Queries and Window Functions Lab](03-ctes-and-window-functions-lab.md)
