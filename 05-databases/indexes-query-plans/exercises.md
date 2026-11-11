# Indexes and Query Plans: Exercises

These problems go with the [Indexes and Query Plans lesson](README.md). Try each one before opening its solution.

Use [`demo_indexes.py`](demo_indexes.py) as a playground, or any SQLite database.

## Problems

### Hands-on
1. Run `demo_indexes.py`. Record the plan and time for query 1 and query 2. How many times faster is the indexed lookup?
2. Create a table with 100,000 rows and a `status` column that has only two values. Add an index on `status`. Does the plan use it for `WHERE status = 'a'`? Why or why not?
3. With an index on `(country, age)`, write three queries: one that uses both columns, one that uses only the first, and one that **cannot** use it. Confirm each with `EXPLAIN QUERY PLAN`.
4. Show that `WHERE lower(email) = 'x'` does not use an index on `email`. Then fix it with an **expression index**.
5. Make `SELECT country, age FROM users WHERE country = 'PK' AND age > 70` use a **covering index** and show the plan.

### Design
6. A table `orders(id, customer_id, status, ordered_on, total)` serves these frequent queries. Propose a minimal set of indexes:
   - A: `WHERE customer_id = ? ORDER BY ordered_on DESC LIMIT 20`
   - B: `WHERE status = 'pending' AND ordered_on < ?`
   - C: `WHERE id = ?`
7. A query `WHERE a = 1 OR b = 2` is slow even though `a` and `b` are both indexed separately. Why might that happen and how can you rewrite it?
8. Explain why `OFFSET 1000000 LIMIT 20` is slow, and rewrite it with keyset pagination.
9. List three reasons **not** to index every column.
10. A table has 5 rows. Should you add an index? Explain.

<details>
<summary>Solutions</summary>

**1.** Typically `SCAN users` at several milliseconds versus `SEARCH ... USING INDEX` at a few microseconds: well over 1,000 times faster on 200,000 rows. Your numbers will differ; the plans are what to compare.

**2.** It barely helps, and what the optimizer does depends on its statistics. A two-value column has very low selectivity: half the table matches, so reading the index and then the table rows is slower than a straight scan. In SQLite, before `ANALYZE` the planner may still pick the index (`SEARCH ... USING INDEX`); after `ANALYZE` it learns the value distribution and switches to `SCAN`. Run both and compare. Better options: a partial index on the rare value, or a composite index that also includes a selective column.

**3.**
```sql
CREATE INDEX idx_country_age ON users(country, age);
EXPLAIN QUERY PLAN SELECT * FROM users WHERE country='PK' AND age > 70;   -- both columns
EXPLAIN QUERY PLAN SELECT * FROM users WHERE country='PK';                 -- leftmost prefix
EXPLAIN QUERY PLAN SELECT * FROM users WHERE age > 70;                     -- cannot use it (SCAN)
```

**4.**
```sql
CREATE INDEX idx_email ON users(email);
EXPLAIN QUERY PLAN SELECT * FROM users WHERE lower(email) = 'x';   -- SCAN (function on column)
CREATE INDEX idx_email_lower ON users(lower(email));
EXPLAIN QUERY PLAN SELECT * FROM users WHERE lower(email) = 'x';   -- SEARCH using idx_email_lower
```

**5.** Create `(country, age)`; the plan shows `COVERING INDEX` because both selected columns are in the index.

**6.**
```sql
-- A: equality on customer_id, then sorted by date
CREATE INDEX idx_orders_customer_date ON orders(customer_id, ordered_on);
-- B: equality on status, then range on date
CREATE INDEX idx_orders_status_date ON orders(status, ordered_on);
-- C: id is the primary key, already indexed
```
A reads the newest 20 entries for the customer straight from the index (no sort). B seeks to `'pending'` and scans the date range.

**7.** Whether `OR` is fast depends on the engine and the plan. SQLite shows `MULTI-INDEX OR` using both indexes; PostgreSQL can use a bitmap OR and MySQL an index merge. But an `OR` needs results from two separate index searches, so some plans fall back to one index plus a filter, or to a full scan. Always check the plan. If it scans, rewrite with `UNION` (or `UNION ALL` with care about overlaps):
```sql
SELECT * FROM t WHERE a = 1
UNION
SELECT * FROM t WHERE b = 2;
```

**8.** `OFFSET N` makes the database read and discard the first `N` rows every time, so deep pages get slower and slower. Keyset pagination remembers the last seen key:
```sql
SELECT * FROM items WHERE id > :last_id ORDER BY id LIMIT 20;
```
With an index on `id` it jumps straight to the next page.

**9.** (a) Every write must update every index, slowing inserts, updates and deletes; (b) indexes consume disk and memory; (c) many are never used, and some are redundant or low-selectivity; the optimizer must also consider more plans.

**10.** No. With 5 rows a scan is as fast as any index seek, and the index only adds write and storage cost. Indexes pay off as tables grow. (Primary and unique constraints still create indexes automatically.)

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Indexes Lab](01-indexes-lab.md)
