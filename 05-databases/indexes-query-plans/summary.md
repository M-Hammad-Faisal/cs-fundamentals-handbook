# Indexes and Query Plans: One-Page Summary

## What an index is
A sorted side structure (usually a **B+ tree**) that turns an `O(n)` scan into an `O(log n)` seek (3 to 4 page reads for huge tables). Demo: ~7 ms scan vs ~0.003 ms seek on 200,000 rows.

## Types
B-tree (default) · hash (equality only) · composite · unique · **covering** (answers from the index alone) · partial/filtered · expression · full-text · GIN/GiST (PostgreSQL).
**Clustered** = physical row order (one per table); **secondary** = keys + pointer to the row.

## Composite indexes
- **Leftmost-prefix rule:** `(country, age)` serves `country` and `country + age`, not `age` alone.
- Order: **equality columns first, then the range column**.
- Match `WHERE` + `ORDER BY` to avoid a sort (`customer_id, ordered_on`).

## Reading plans
`EXPLAIN QUERY PLAN` (SQLite) · `EXPLAIN ANALYZE` (PostgreSQL) · `EXPLAIN` (MySQL).
- `SCAN` / `Seq Scan` = full scan; `SEARCH … INDEX` = seek; `COVERING INDEX` = no table lookup; `TEMP B-TREE FOR ORDER BY` / `Sort` = extra sort.
- Joins: nested loop, hash join, merge join. Keep **statistics** fresh (`ANALYZE`).

## Why an index is ignored
Function on the column · leading wildcard `LIKE '%x'` · skipped leftmost column · type mismatch · arithmetic on the column · low selectivity · `OR` across columns · tiny tables.

## Cost
Slower writes, more disk/memory, maintenance. Index for real queries; drop unused or redundant indexes.

## Tips
Index filter/join/sort columns (including foreign keys) · prefer covering indexes for hot queries · use keyset pagination over `OFFSET` · build indexes online in production (`CONCURRENTLY`).

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Indexes Lab](01-indexes-lab.md)
