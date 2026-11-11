# PostgreSQL: One-Page Summary

## Questions worth remembering

- **Why prefer `timestamptz` and `numeric` for time and money?** `timestamptz` stores an unambiguous instant (UTC) and avoids time-zone errors; `numeric` is exact decimal arithmetic, unlike binary floating point.
- **What does `INSERT ... ON CONFLICT DO UPDATE` give you that "select, then insert or update" does not?** One atomic statement that is safe under concurrency; the two-step version races (two clients can both see "missing" and both insert).
- **Which index type for jsonb containment, for a huge append-only time series, and for "only open orders"?** GIN for jsonb containment; BRIN for the huge append-only series; a partial index (`WHERE status = 'open'`) for open orders.
- **What is MVCC, and what problem does it create that `VACUUM` solves?** Multi-version concurrency control keeps old row versions so readers and writers do not block each other; the old versions become dead space that `VACUUM` reclaims.
- **What does `FOR UPDATE SKIP LOCKED` do?** It locks the chosen rows and makes other transactions skip rows that are already locked, so workers can claim distinct jobs without waiting.
- **What is the difference between `EXPLAIN` and `EXPLAIN ANALYZE`?** `EXPLAIN` shows the planned strategy and cost estimates without running the query; `EXPLAIN ANALYZE` runs it and reports actual timings and row counts.

Practice problems with solutions are in the **Practice** section of each lesson.

[Lesson](README.md) · [PostgreSQL-Specific Features](01-postgresql-specific-features.md)
