# PostgreSQL

What PostgreSQL adds beyond standard SQL and SQLite: rich types, upserts, advanced indexes, MVCC and the tools to inspect it.

## Detailed lessons

- [PostgreSQL-specific features](01-postgresql-specific-features.md): data types (jsonb, arrays, timestamptz), `RETURNING` and upserts, index types (B-tree, GIN, GiST, BRIN, partial, expression), MVCC and VACUUM, locking queues with `SKIP LOCKED`, `LISTEN/NOTIFY`, `EXPLAIN (ANALYZE, BUFFERS)` and `psql`. SQL run against PostgreSQL 18.6; see the note at the top of the lesson.

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Question | Answer |
|----------|--------|
| Why prefer `timestamptz` and `numeric` for time and money? | `timestamptz` stores an unambiguous instant (UTC) and avoids time-zone errors; `numeric` is exact decimal arithmetic, unlike binary floating point. |
| What does `INSERT ... ON CONFLICT DO UPDATE` give you that "select, then insert or update" does not? | One atomic statement that is safe under concurrency; the two-step version races (two clients can both see "missing" and both insert). |
| Which index type for jsonb containment, for a huge append-only time series, and for "only open orders"? | GIN for jsonb containment; BRIN for the huge append-only series; a partial index (`WHERE status = 'open'`) for open orders. |
| What is MVCC, and what problem does it create that `VACUUM` solves? | Multi-version concurrency control keeps old row versions so readers and writers do not block each other; the old versions become dead space that `VACUUM` reclaims. |
| What does `FOR UPDATE SKIP LOCKED` do? | It locks the chosen rows and makes other transactions skip rows that are already locked, so workers can claim distinct jobs without waiting. |

Related: [relational SQL](../relational-sql/README.md), [indexes and query plans](../indexes-query-plans/README.md), [transactions and ACID](../transactions-acid/README.md).

Back to [databases](../README.md).
