# PostgreSQL: One-Page Summary

## Key facts

- **Types to prefer:** `timestamptz` for instants, `numeric` for money, `jsonb` for flexible documents, `uuid`, arrays and ranges; `text` needs no length limit.
- **Write helpers:** `RETURNING` hands back inserted or updated rows; `INSERT … ON CONFLICT (key) DO UPDATE` is an atomic upsert; `WITH` (CTE) names a step of a query.
- **Index types:** B-tree (default: equality, ranges, sorting), GIN (`jsonb` containment, arrays, full-text), GiST (ranges, geometry), BRIN (huge append-only, naturally ordered tables), plus partial indexes (`WHERE status = 'open'`), expression indexes and `INCLUDE` columns.
- **MVCC:** an update writes a new row version, so readers never block writers; dead versions are removed by `VACUUM` (autovacuum), and long-running transactions hold cleanup back (bloat). Default isolation level is read committed.
- **Queues and events:** `SELECT … FOR UPDATE SKIP LOCKED` lets workers claim different rows; `LISTEN` / `NOTIFY` is lightweight, non-durable pub/sub.
- **Read plans:** `EXPLAIN (ANALYZE, BUFFERS)` shows actual time and rows; compare estimated and actual rows, and look for sequential scans on big tables.
- **`psql`:** `\d table`, `\dt`, `\x` (expanded output), `\timing`.

## Pitfalls

- `timestamp` without time zone, or money stored as `float`.
- `NOT IN (subquery)` when the subquery can return `NULL`: use `NOT EXISTS`.
- A function on an indexed column in `WHERE` (`lower(email)`) skips the plain index; create an expression index.
- Deep paging with `OFFSET`; `SELECT *` in application code.
- Connections left "idle in transaction", which block vacuum and hold locks.
- Skipping `ANALYZE` after a bulk load, so the planner works from stale statistics.

## Self-check

- **Why prefer `timestamptz` and `numeric` for time and money?** `timestamptz` stores an unambiguous instant (UTC) and avoids time-zone errors; `numeric` is exact decimal arithmetic, unlike binary floating point.
- **What does `INSERT ... ON CONFLICT DO UPDATE` give you that "select, then insert or update" does not?** One atomic statement that is safe under concurrency; the two-step version races (two clients can both see "missing" and both insert).
- **Which index type for jsonb containment, for a huge append-only time series, and for "only open orders"?** GIN for jsonb containment; BRIN for the huge append-only series; a partial index (`WHERE status = 'open'`) for open orders.
- **What is MVCC, and what problem does it create that `VACUUM` solves?** Multi-version concurrency control keeps old row versions so readers and writers do not block each other; the old versions become dead space that `VACUUM` reclaims.
- **What does `FOR UPDATE SKIP LOCKED` do?** It locks the chosen rows and makes other transactions skip rows that are already locked, so workers can claim distinct jobs without waiting.
- **What is the difference between `EXPLAIN` and `EXPLAIN ANALYZE`?** `EXPLAIN` shows the planned strategy and cost estimates without running the query; `EXPLAIN ANALYZE` runs it and reports actual timings and row counts.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [PostgreSQL-Specific Features](01-postgresql-specific-features.md)
