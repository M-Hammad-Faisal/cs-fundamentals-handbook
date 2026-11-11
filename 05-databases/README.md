# Databases

How applications store, find and protect their data. Every lesson here runs **entirely on your computer** with Python's built-in `sqlite3` module (no server to install): you build tables, break them on purpose, measure indexes on 200 000 rows, run two connections against each other, and build a mini search engine and a replicated store.

**Prerequisites:** [Python basics](../00-foundations/python-fundamentals/README.md) and [data structures](../02-data-structures/README.md) (hash tables and B-trees explain a lot of database behavior). The shared dataset used by several lessons is [sample-data.sql](sample-data.sql).

## Start here

[What is a database? And how to model one (ER diagrams)](00-what-is-a-database-and-er-modeling.md): why databases exist, the modeling process, ER diagrams, turning them into tables, and enforcing the design with constraints.

## Reading order

| # | Topic | Quick reference | Hands-on labs |
|---|-------|-----------------|---------------|
| 1 | The relational model and SQL | [lesson](relational-sql/README.md) | [SQL first steps](relational-sql/01-sql-first-steps.md) · [aggregation and joins](relational-sql/02-aggregation-and-joins-lab.md) · [CTEs and window functions](relational-sql/03-ctes-and-window-functions-lab.md) |
| 2 | Schema design and normalization | [lesson](normalization-schema-design/README.md) | [ER modeling](00-what-is-a-database-and-er-modeling.md) · [normalization lab](normalization-schema-design/01-normalization-lab.md) |
| 3 | Indexes and query plans | [lesson](indexes-query-plans/README.md) | [indexes lab](indexes-query-plans/01-indexes-lab.md) |
| 4 | Transactions, ACID and isolation | [lesson](transactions-acid/README.md) | [transactions lab](transactions-acid/01-transactions-lab.md) |
| 5 | NoSQL and choosing a database | [lesson](nosql/README.md) | [NoSQL lab](nosql/01-nosql-lab.md) |
| 6 | PostgreSQL-specific features (run on PostgreSQL 18.6) | [lesson](postgresql/README.md) | [PostgreSQL features](postgresql/01-postgresql-specific-features.md) |

Each topic folder also has `exercises.md` and a one-page `summary.md`.

## The five questions every database answers

1. **How is data shaped?** Tables, keys and constraints (relational) or documents/key-value pairs. [SQL first steps](relational-sql/01-sql-first-steps.md), [normalization](normalization-schema-design/01-normalization-lab.md)
2. **How do I ask for it?** Declarative queries: say *what*, the planner chooses *how*. [joins and aggregation](relational-sql/02-aggregation-and-joins-lab.md)
3. **How is it found fast?** Indexes (B-trees) turn scans into lookups. [indexes lab](indexes-query-plans/01-indexes-lab.md)
4. **How is it kept correct when many users write at once, or the power fails?** Transactions, isolation, logging. [transactions lab](transactions-acid/01-transactions-lab.md)
5. **What changes when one machine is not enough?** Replication, partitioning, consistency trade-offs. [NoSQL lab](nosql/01-nosql-lab.md)

## SQL cheat sheet

```sql
SELECT   columns, aggregate(...)      -- what to return
FROM     table JOIN other ON key      -- where from, combined
WHERE    row condition                -- filter rows (before grouping)
GROUP BY columns                      -- one result per group
HAVING   group condition              -- filter groups (after aggregation)
ORDER BY column DESC                  -- sort
LIMIT    n;                           -- how many
-- evaluated in this order: FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT
```

| Task | Pattern |
|------|---------|
| Rows with no match in another table | `LEFT JOIN ... WHERE b.id IS NULL` or `NOT EXISTS` |
| Count including empty groups | `LEFT JOIN` + `COUNT(b.id)` (not `COUNT(*)`) |
| Top N per group | window function `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` |
| Safe update of a counter | `UPDATE t SET n = n + 1 WHERE id = ?` (atomic, never read-modify-write in Python) |
| Avoid SQL injection | placeholders: `execute("... WHERE id = ?", (value,))` |

## Rules of thumb

- **Constraints** (`NOT NULL`, `UNIQUE`, `CHECK`, foreign keys) belong in the database, not only in application code.
- **Index** columns used in `WHERE`, `JOIN` and `ORDER BY`; check the **query plan** to confirm it is used.
- **Normalize first**, denormalize only for a measured read bottleneck.
- Keep **transactions short**; never hold one open while waiting for a user or a network call.
- Use **atomic statements, locks or version checks** instead of read-then-write in application code.
- Start with **PostgreSQL**; add specialized stores (cache, search, warehouse) when a measured need appears.

Back to the [index](../INDEX.md).
