# Indexes and Query Plans

This chapter has a runnable companion: [`demo_indexes.py`](demo_indexes.py) builds a 200,000-row table and shows the plans and timings quoted below. Run it with `python3 demo_indexes.py`.

## 1. The concept

An **index** is a separate, sorted data structure that lets the database find rows without reading the whole table. It works like the index at the back of a book: instead of reading every page to find "recursion", you look it up in a sorted list and jump to the page.

Without an index, a query on an unindexed column does a **full table scan**: read every row, `O(n)`. With an index, the database does an **index seek**, `O(log n)`.

Typical result from the demo (200,000 rows, one lookup by email):

| Plan | Time |
|------|------|
| `SCAN users` (no index) | about 7 ms |
| `SEARCH users USING INDEX idx_users_email (email=?)` | about 0.003 ms |

That is roughly a **2,000x** difference on a table this small; the gap grows with the table.

## 2. How indexes work: B-trees

Most indexes are **B-trees** (technically **B+ trees**): wide, shallow, balanced trees where each node holds many sorted keys and is sized to one disk page.

```
                 [ 300 | 700 ]                 root
                /      |      \
      [100|200]   [400|500|600]   [800|900]    internal nodes
       /  |  \       ...             ...
   leaf pages: key -> row location, linked left to right
```

- A tree with hundreds of keys per node is only **3 to 4 levels** deep even for hundreds of millions of rows, so a lookup reads 3 to 4 pages.
- Leaves are linked in order, so **range scans** (`BETWEEN`, `>`, `ORDER BY`) walk along the leaves.
- Because keys are sorted, an index also satisfies `ORDER BY` and `MIN/MAX` cheaply.

See [trees](../../02-data-structures/trees/README.md) for how B-trees keep themselves balanced.

### Index types

| Type | Good for | Notes |
|------|----------|-------|
| **B-tree** (default) | Equality, ranges, sorting, prefix `LIKE 'abc%'` | The workhorse |
| **Hash** | Equality only | `O(1)`, no ranges or sorting |
| **Composite (multi-column)** | Queries filtering on several columns | Column order matters |
| **Unique** | Enforcing uniqueness | Created automatically for `UNIQUE`/`PRIMARY KEY` |
| **Covering** | Queries answered entirely from the index | No table lookup needed |
| **Partial / filtered** | Indexing only some rows (`WHERE active = 1`) | Smaller, faster |
| **Expression** | Queries on a computed value (`lower(email)`) | Match the exact expression |
| **Full-text** | Word search in text | Inverted index (like a book index of words) |
| **GIN / GiST (PostgreSQL)** | JSON, arrays, geometry, full text | Specialized structures |

### Clustered vs non-clustered

- A **clustered** index defines the physical order of the table's rows (InnoDB's primary key; SQL Server clustered index). There is only one per table.
- A **secondary (non-clustered)** index stores keys plus a pointer (the primary key or row id) back to the row, so using it can cost an extra lookup.

## 3. Creating indexes

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);
CREATE INDEX idx_country_age ON users(country, age);        -- composite
CREATE INDEX idx_active_email ON users(email) WHERE active = 1;   -- partial (SQLite, PostgreSQL)
DROP INDEX idx_users_email;
```

## 4. Composite indexes and the leftmost-prefix rule

A composite index on `(country, age)` is sorted by `country` first, then by `age` within each country. It can serve:

| Query filter | Uses the index? |
|--------------|-----------------|
| `country = 'PK'` | Yes (leftmost column) |
| `country = 'PK' AND age > 70` | Yes (both) |
| `age > 70` alone | **No** (skips the leftmost column) |

Demo output for `WHERE age > 70` with only that composite index: `SCAN users`. Reverse the column order, or add a separate index, if you need the other access path.

**Column order rule of thumb:** put **equality** columns first, then the **range** column, and prefer the column that filters out the most rows when otherwise equal.

### Covering indexes

If the index contains every column the query needs, the database never touches the table:

```
SEARCH users USING COVERING INDEX idx_country_age (country=? AND age>?)
```

`SELECT country, age FROM users WHERE country = 'PK' AND age > 70` is fully answered from `idx_country_age`. `SELECT *` would need table lookups too.

## 5. Reading query plans

Ask the database how it will run a query:

```sql
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'a@example.com';   -- SQLite
```

```postgresql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'a@example.com';      -- PostgreSQL (runs it, shows real timings)
```

```text
-- MySQL
EXPLAIN SELECT * FROM users WHERE email = 'a@example.com';
```

### What to look for

| Plan wording | Meaning |
|--------------|---------|
| `SCAN` / `Seq Scan` / `type: ALL` | Full table scan (read everything) |
| `SEARCH ... USING INDEX` / `Index Scan` / `type: ref` | Index seek |
| `COVERING INDEX` / `Index Only Scan` | Answered from the index alone |
| `USE TEMP B-TREE FOR ORDER BY` / `Sort` | An explicit sort step (an index could avoid it) |
| Estimated vs actual rows far apart | Stale statistics; run `ANALYZE` |

### Join strategies you will see

| Strategy | How it works | Best when |
|----------|--------------|-----------|
| **Nested loop** | For each outer row, look up matching inner rows (ideally by index) | Small outer set, indexed inner |
| **Hash join** | Build a hash table of the smaller side, probe with the other | Large unsorted inputs, equality joins |
| **Merge join** | Walk two sorted inputs together | Both inputs already sorted |

The **query optimizer** estimates the cost of many plans using table **statistics** (row counts, value distributions) and chooses the cheapest. Stale statistics cause bad plans; refresh them with `ANALYZE`.

## 6. When an index will NOT be used

These are the classic traps. The demo shows the first few as `SCAN users`; the rest depend on your engine and its statistics, so always confirm in the plan.

| Trap | Example | Fix |
|------|---------|-----|
| **Function on the column** | `WHERE lower(email) = 'x'` | Rewrite, or create an expression index on `lower(email)` |
| **Leading wildcard** | `WHERE email LIKE '%@example.com'` | Use full-text search or a reversed-column index |
| **Skipping the leftmost column** | `WHERE age > 70` with index `(country, age)` | Add an index starting with `age` |
| **Type mismatch** | Comparing a text column to a number | Match the types |
| **Low selectivity** | Index on a boolean with 50/50 values | With good statistics the optimizer prefers a scan |
| **`OR` across columns** | `WHERE a = 1 OR b = 2` | Index both; many engines combine them, but check the plan and use `UNION` if it scans |
| **Very small table** | A few hundred rows | A scan is just as fast |
| **Arithmetic on the column** | `WHERE age + 1 > 30` | Rewrite as `age > 29` |

**Selectivity** is how well a condition narrows the rows. An index on `email` (unique) is highly selective; an index on `is_active` (two values) is not.

## 7. The cost of indexes

Indexes are not free.

- **Writes get slower.** Every `INSERT`, `UPDATE` and `DELETE` must also update each index.
- **They use disk and memory.** Each index is a copy of its columns, sorted.
- **They need maintenance.** Bloat, fragmentation, and stale statistics.

The rule: **index for the queries you actually run,** drop unused indexes, and do not index every column. Read-heavy workloads tolerate many indexes; write-heavy ones suffer.

## 8. Two real-world examples

### Example 1: A login page that suddenly got slow

A service looks users up by email at login. In development with 1,000 users the query takes 1 ms. In production with 20 million users, `WHERE email = ?` without an index does a full scan: seconds per login, and the database CPU spikes under load, taking down unrelated features. A single `CREATE UNIQUE INDEX ON users(email)` turns it into a 3 to 4 page read and also prevents duplicate accounts. The lesson: performance bugs often appear only at production scale, so check plans before shipping.

### Example 2: A feed or order history with `ORDER BY ... LIMIT`

"Show the 20 most recent orders for this customer" is `WHERE customer_id = ? ORDER BY ordered_on DESC LIMIT 20`. With an index on `(customer_id, ordered_on)`, the database seeks to the customer and reads the last 20 index entries in order, with no sort and no scan. Without it, the database gathers all of the customer's orders, sorts them, and discards all but 20. Pagination, activity feeds, and "latest N" dashboards all depend on a composite index that matches both the filter and the sort order.

## 9. Tips, tricks and pitfalls

- **Look at the plan, not your intuition.** Run `EXPLAIN` before and after adding an index.
- **Index the columns you filter, join, and sort on.** Foreign key columns are prime candidates (joins and cascading deletes).
- **Design composite indexes from your queries,** with equality columns first, then ranges.
- **Prefer covering indexes for hot queries,** and select only the columns you need.
- **Avoid wrapping indexed columns in functions;** compare the raw column to a computed value instead.
- **Keep statistics fresh** (`ANALYZE`, autovacuum in PostgreSQL).
- **Drop unused and duplicate indexes.** An index on `(a)` is redundant when `(a, b)` exists.
- **Add indexes in production carefully:** building one on a huge table can lock it. Use online options (`CREATE INDEX CONCURRENTLY` in PostgreSQL).
- **Beware of too many indexes on write-heavy tables.**
- **`LIKE 'abc%'` can use a B-tree;** `LIKE '%abc'` cannot.
- **Pagination:** prefer keyset pagination (`WHERE id > last_seen ORDER BY id LIMIT 20`) to `OFFSET`, which still reads and discards the skipped rows.

## 10. Check yourself

1. What is the difference between a full table scan and an index seek, and what are their complexities?
2. Why are B-trees used for database indexes instead of binary trees?
3. State the leftmost-prefix rule. Would an index on `(country, age)` help `WHERE age > 70`?
4. What is a covering index?
5. Give three ways a query can accidentally avoid using an available index.
6. Why can adding too many indexes hurt?
7. What does `EXPLAIN` tell you, and what should make you suspicious?
8. What makes a column a good candidate for an index (selectivity)?
9. How do clustered and secondary indexes differ?

<details>
<summary>Answers</summary>

1. A scan reads every row, `O(n)`. An index seek walks a tree, `O(log n)`, typically 3 to 4 page reads.
2. B-trees are wide and shallow, with many keys per node matched to a disk page, so they need very few page reads. They also keep leaves linked for efficient range scans.
3. A composite index can be used only for a leftmost prefix of its columns. No: filtering on `age` alone skips the leading `country` column.
4. An index that contains every column the query needs, so the database never reads the table.
5. A function on the column (`lower(email)`), a leading wildcard (`LIKE '%x'`), skipping the leftmost column, a type mismatch, or arithmetic on the column.
6. Each write must update every index, and indexes consume disk and memory, so write throughput drops and storage grows.
7. It shows the chosen plan: scan or seek, join strategy, sort steps. Be suspicious of full scans on big tables, explicit sorts, and estimated rows far from actual rows.
8. High selectivity: the condition narrows the table to a small fraction of rows (such as a unique email), and the column is used in filters, joins, or sorts.
9. A clustered index determines the table's physical row order (one per table). A secondary index stores keys plus a pointer to the row, which can cost an extra lookup.

</details>
