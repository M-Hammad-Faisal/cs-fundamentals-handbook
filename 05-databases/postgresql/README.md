# PostgreSQL

What PostgreSQL adds beyond standard SQL and SQLite: rich types, upserts, advanced indexes, MVCC and the tools to inspect it.

## Detailed lesson

- [PostgreSQL-specific features](01-postgresql-specific-features.md): data types (jsonb, arrays, timestamptz), `RETURNING` and upserts, index types (B-tree, GIN, GiST, BRIN, partial, expression), MVCC and VACUUM, locking queues with `SKIP LOCKED`, `LISTEN/NOTIFY`, `EXPLAIN (ANALYZE, BUFFERS)` and `psql`. **Not executed in this repository's test run** (no PostgreSQL server was available); see the note at the top of the lesson.

Related: [relational SQL](../relational-sql/README.md), [indexes and query plans](../indexes-query-plans/README.md), [transactions and ACID](../transactions-acid/README.md).

Back to [databases](../README.md).
