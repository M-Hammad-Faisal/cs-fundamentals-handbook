# Indexes Lab: Speed, Query Plans and Trade-offs

**Prerequisites:** [SQL first steps](../relational-sql/01-sql-first-steps.md), [binary search](../../03-algorithms/searching/01-linear-and-binary-search.md), [B-trees](../../02-data-structures/trees/03-balanced-trees-avl.md). **You will learn (by measuring 200 000 rows):** what an **index** is and why it turns a full scan into a lookup, how to read a **query plan** (`EXPLAIN QUERY PLAN`), how **composite indexes** and the **leftmost-prefix rule** work, what makes the database **ignore** an index (functions on columns, leading wildcards, low selectivity), **covering** and **partial** indexes, and the **cost** of indexes on writes and space.

## 1. In plain words

A textbook's **index** lets you find "binary search" without reading every page: it lists terms in sorted order with page numbers. A database index is the same: a **separate, sorted structure** (usually a **B-tree**) of a column's values, each pointing to the row.

- **Without an index:** to find one email among 200 000 rows the database must read **every row** (a *full table scan*, `O(n)`).
- **With an index:** it descends a tree about 3 to 4 levels deep (`O(log n)`) and jumps straight to the row.

```text
index on email (a B-tree, sorted)                 table (heap)
 [user1000..]  ->  row at position 17
 [user1001..]  ->  row at position 912            lookups: root -> branch -> leaf -> row
 ...
```

## 2. A table big enough to feel it

```python
import sqlite3, random, time

random.seed(42)
db = sqlite3.connect(":memory:")
db.execute("""CREATE TABLE users (
    id         INTEGER PRIMARY KEY,
    email      TEXT NOT NULL,
    country    TEXT NOT NULL,
    age        INTEGER NOT NULL,
    created_on TEXT NOT NULL,
    status     TEXT NOT NULL)""")

countries = ["PK", "US", "UK", "DE", "IN", "FR", "BR", "JP"]
db.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", (
    (i, f"user{i}@example.com", random.choice(countries), random.randint(18, 80),
     f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}", random.choice(["active"] * 9 + ["banned"]))
    for i in range(1, 200_001)))
db.commit()
print(db.execute("SELECT COUNT(*) FROM users").fetchone())                   # (200000,)

def plan(sql, *params):
    return [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + sql, params)]

def milliseconds(sql, *params, repeat=20):
    start = time.perf_counter()
    for _ in range(repeat):
        db.execute(sql, params).fetchall()
    return (time.perf_counter() - start) / repeat * 1000
```

## 3. Reading a query plan

`EXPLAIN QUERY PLAN` shows **how** the database will run a query without running it. (PostgreSQL/MySQL: `EXPLAIN` and `EXPLAIN ANALYZE`.) The words to know:

| Plan wording (SQLite) | Meaning |
|-----------------------|---------|
| `SCAN users` | read the **whole table** (slow on big tables) |
| `SEARCH users USING INDEX idx (col=?)` | use an index to jump to matching rows |
| `SEARCH ... USING INTEGER PRIMARY KEY (rowid=?)` | direct lookup by primary key |
| `SEARCH ... USING COVERING INDEX` | answered entirely from the index, never touching the table |
| `USE TEMP B-TREE FOR ORDER BY` | a separate sort step because no index gives the order |

### Before: a full scan

```python
QUERY = "SELECT id, country FROM users WHERE email = ?"
target = "user150000@example.com"
print(plan(QUERY, target))                                                    # ['SCAN users']
scan_ms = milliseconds(QUERY, target)
print(f"{scan_ms:.2f} ms per lookup")                                         # about 7 ms (varies by machine)
```

### After: create an index

```python
db.execute("CREATE INDEX idx_users_email ON users(email)")
print(plan(QUERY, target))                                                    # ['SEARCH users USING INDEX idx_users_email (email=?)']
index_ms = milliseconds(QUERY, target, repeat=2000)
print(f"{index_ms:.4f} ms per lookup, about {scan_ms / index_ms:,.0f}x faster")      # e.g. 0.0015 ms, about 4,000x faster
print(scan_ms > 100 * index_ms)                                               # True
```

One statement, a few-thousand-fold speedup. That is why indexing is the first thing to check for a slow query. (The primary key already has an index automatically:)

```python
print(plan("SELECT * FROM users WHERE id = 5"))                               # ['SEARCH users USING INTEGER PRIMARY KEY (rowid=?)']
```

## 4. How the lookup works (the B-tree)

A B-tree node holds many sorted keys, so the tree is **short and wide**. With about 100-500 keys per page, 200 000 rows need only 3 levels:

```python
import math
rows, keys_per_page = 200_000, 200
print(math.ceil(math.log(rows, keys_per_page)), "page reads to find any row")      # 3   (a million rows: 3, a billion: 4)
```

Each level is one disk-page read, so even a huge table is found in a handful of reads. Because the keys are **sorted**, an index also supports **range queries** (`BETWEEN`, `>`, `<`) and **`ORDER BY`** without sorting, and prefix matches. A hash index (equality only) is the alternative some databases offer.

## 5. Composite (multi-column) indexes and the leftmost-prefix rule

An index on `(country, age)` is sorted by country, then by age within each country, like a phone book sorted by last name then first name.

```python
q = "SELECT * FROM users WHERE country = 'PK' AND age = 30"
print(plan(q))                                                                # ['SCAN users']      (only the email index exists so far)
db.execute("CREATE INDEX idx_country_age ON users(country, age)")
print(plan(q))                                                                # ['SEARCH users USING INDEX idx_country_age (country=? AND age=?)']
```

You can use the index for the **leftmost columns**, in order, but not for later columns alone (a phone book is useless if you only know the first name):

```python
print(plan("SELECT * FROM users WHERE country = 'PK'"))                       # ['SEARCH users USING INDEX idx_country_age (country=?)']                  leftmost column: fine
print(plan("SELECT * FROM users WHERE age = 30"))                             # ['SCAN users']                                                             skips country: no usable prefix (see the skip-scan note in the solutions)
print(plan("SELECT * FROM users WHERE country = 'PK' AND age BETWEEN 30 AND 40"))
# ['SEARCH users USING INDEX idx_country_age (country=? AND age>? AND age<?)']     equality on country, then a range on age: good
```

**Column order matters.** Rule of thumb: put **equality** columns first, then the **range** or sort column, and (usually) the more selective columns earlier. An index on `(a, b)` makes a separate index on `(a)` redundant but does **not** help queries filtering only on `b`.

### Indexes also give sorted order

```python
print(plan("SELECT * FROM users ORDER BY email LIMIT 5"))                     # ['SCAN users USING INDEX idx_users_email']       reads in index order and stops after 5
print(plan("SELECT * FROM users ORDER BY age LIMIT 5"))                       # ['SCAN users', 'USE TEMP B-TREE FOR ORDER BY']   no index on age alone: scan then sort everything
```

## 6. Covering indexes: never touch the table

If the index contains **every column the query needs**, the database answers from the index alone (an "index-only scan"): fewer reads, since index entries are smaller than rows.

```python
print(plan("SELECT age FROM users WHERE country = 'PK' AND age = 30"))
# ['SEARCH users USING COVERING INDEX idx_country_age (country=? AND age=?)']       all needed columns (country, age) live in the index

db.execute("CREATE INDEX idx_created_country ON users(created_on, country)")
print(plan("SELECT country FROM users WHERE created_on = '2024-05-05'"))
# ['SEARCH users USING COVERING INDEX idx_created_country (created_on=?)']
```

## 7. When the database will NOT use your index

A very common bug: you created the index and the query still scans. The usual reasons:

### 7.1 A function or expression applied to the column

```python
print(plan("SELECT * FROM users WHERE LOWER(email) = 'user5@example.com'"))   # ['SCAN users']           LOWER(email) is not what the index stores
db.execute("CREATE INDEX idx_lower_email ON users(LOWER(email))")             # an expression index fixes it
print(plan("SELECT * FROM users WHERE LOWER(email) = 'user5@example.com'"))   # ['SEARCH users USING INDEX idx_lower_email (<expr>=?)']
```

Same trap: `WHERE strftime('%Y', created_on) = '2024'`, `WHERE age + 1 = 31`, `WHERE CAST(id AS TEXT) = '5'`. **Rewrite the condition so the column stands alone** (`WHERE created_on >= '2024-01-01' AND created_on < '2025-01-01'`), or create an expression index.

### 7.2 A leading wildcard in `LIKE`

```python
print(plan("SELECT * FROM users WHERE email LIKE '%1500@example.com'"))       # ['SCAN users']      '%' first: the sorted order cannot help, every value must be checked
```

A **prefix** search (`'user1500%'`) can use a sorted index, because all matches are adjacent. In SQLite `LIKE` is case-insensitive by default, which a plain (case-sensitive) index cannot serve, so use a range or a `NOCASE` index:

```python
print(plan("SELECT * FROM users WHERE email LIKE 'user1500%'"))               # ['SCAN users']      plain LIKE does not use the case-sensitive index
print(plan("SELECT * FROM users WHERE email >= 'user1500' AND email < 'user1501'"))
# ['SEARCH users USING INDEX idx_users_email (email>? AND email<?)']           the same prefix search as a range: uses the index
db.execute("CREATE INDEX idx_email_nocase ON users(email COLLATE NOCASE)")
print(plan("SELECT * FROM users WHERE email LIKE 'user1500%'"))               # ['SEARCH users USING INDEX idx_email_nocase (email>? AND email<?)']
```

(For real substring and fuzzy search use a **full-text index**: SQLite FTS5, PostgreSQL `tsvector`/trigram, or a search engine such as Elasticsearch.)

### 7.3 Low selectivity: the planner correctly prefers a scan

Selectivity is the fraction of rows a condition matches. If it matches most of the table, bouncing between the index and the table row by row is *slower* than one sequential scan.

```python
db.execute("CREATE INDEX idx_status ON users(status)")
print(db.execute("SELECT status, COUNT(*) FROM users GROUP BY status ORDER BY status").fetchall())      # [('active', 179919), ('banned', 20081)]
db.execute("ANALYZE")                                                         # collect statistics so the planner knows the distribution
print(plan("SELECT * FROM users WHERE status = 'banned'"))                    # ['SEARCH users USING INDEX idx_status (status=?)']      10% of rows: the index pays off
print(plan("SELECT * FROM users WHERE status = 'active'"))                    # ['SCAN users']                                            90% of rows: a full scan is cheaper
```

**Cardinality** (number of distinct values) guides what to index: an index on a boolean or status column rarely helps; an index on email or user id helps enormously. Keep statistics fresh (`ANALYZE`, PostgreSQL `autovacuum`/`ANALYZE`) or the planner makes poor choices.

### 7.4 Other reasons

- A **type mismatch** (comparing a text column to a number forces conversion on every row).
- The index is on `(a, b)` but the query filters only on `b` (leftmost-prefix rule).
- `OR` across different columns, `NOT IN`/`<>` conditions, or `!=` (hard to turn into a narrow range).
- Tiny tables (a scan is cheaper than any index lookup).
- Outdated statistics or an optimizer bug (rare: confirm with the plan, test with a hint or `ANALYZE`).

## 8. Partial indexes: index only the rows you query

```python
db.execute("CREATE INDEX idx_banned_created ON users(created_on) WHERE status = 'banned'")
print(plan("SELECT * FROM users WHERE status = 'banned' AND created_on = '2024-05-05'"))
# ['SEARCH users USING INDEX idx_banned_created (created_on=?)']
```

The index stores only the 10% banned rows: smaller, cheaper to maintain, and faster to search. Typical uses: "only unprocessed jobs", "only non-deleted rows", "only active subscriptions". PostgreSQL and SQLite support them; MySQL does not.

## 9. The cost: indexes are not free

Every index must be **updated on every `INSERT`, `UPDATE` of its columns and `DELETE`**, and it **takes space**.

```python
def insert_seconds(index_count, n=20_000):
    d = sqlite3.connect(":memory:")
    d.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, a TEXT, b INTEGER, c TEXT)")
    for i in range(index_count):
        d.execute(f"CREATE INDEX i{i} ON t({'abc'[i]})")
    data = [(i, f"x{random.random()}", random.randint(0, 10**6), f"y{random.random()}") for i in range(n)]
    start = time.perf_counter()
    d.executemany("INSERT INTO t VALUES (?, ?, ?, ?)", data)
    d.commit()
    return time.perf_counter() - start

times = [insert_seconds(k) for k in range(4)]
print([round(t, 3) for t in times])                                            # e.g. [0.012, 0.022, 0.032, 0.043]     seconds for 20,000 inserts with 0, 1, 2, 3 indexes
print(times[3] > 2 * times[0])                                                 # True    three secondary indexes more than doubled insert time here
print(db.execute("PRAGMA page_count").fetchone()[0] * db.execute("PRAGMA page_size").fetchone()[0] // 1_000_000, "MB database with all these indexes")
```

Guidelines:

- Index columns used in **`WHERE`, `JOIN ... ON`, `ORDER BY`, `GROUP BY`**, and **foreign keys** (joins and deletes of parents scan the child table otherwise).
- Do **not** index everything: each index slows writes and consumes memory and disk. A write-heavy table may want few indexes; a read-heavy one many.
- **Drop unused and duplicate indexes** (PostgreSQL: `pg_stat_user_indexes`; MySQL: `sys.schema_unused_indexes`).
- Use `UNIQUE` indexes to enforce rules (`UNIQUE(email)`), not only to speed lookups.
- Add indexes **because a plan shows a scan on a hot query**, not by superstition.

## 10. A tuning workflow

1. **Find the slow query** (slow-query log, `pg_stat_statements`, APM traces).
2. **Read its plan**: look for `SCAN` on big tables, temp sorts, and big difference between estimated and actual rows.
3. **Hypothesize**: missing index? function on a column? wrong column order? too many rows requested?
4. **Change one thing** (create the index, rewrite the condition) and **re-check the plan and the timing**.
5. **Check writes**: does insert/update speed still meet your needs? Does the index fit in memory?
6. **Keep it**: record why the index exists (comment or migration message) so nobody drops it blindly.

Also fix the **query** before adding indexes: select fewer columns, filter earlier, avoid `SELECT *`, paginate with `WHERE id > last_seen` instead of huge `OFFSET`, and avoid the "N+1" pattern (one query per row from application code) by joining or batching.

```python
# N+1: 1 query for the list + one per row (slow). Better: one query with IN or a join.
ids = [r[0] for r in db.execute("SELECT id FROM users LIMIT 500")]
start = time.perf_counter()
for i in ids:
    db.execute("SELECT email FROM users WHERE id = ?", (i,)).fetchone()
n_plus_one = time.perf_counter() - start

start = time.perf_counter()
db.execute(f"SELECT id, email FROM users WHERE id IN ({','.join('?' * len(ids))})", ids).fetchall()
batched = time.perf_counter() - start
print(batched < n_plus_one)                                                    # True   (one round trip instead of 500; over a network the gap is far larger)
```

## 11. Two real-world examples

**Example 1: The login that got slower every month.** `SELECT * FROM users WHERE email = ?` was instant with 10 000 users and takes seconds with 5 million: the plan shows `SCAN users` because nobody created an index on `email`. `CREATE UNIQUE INDEX` on `email` (which also prevents duplicate accounts) restored millisecond logins.

**Example 2: The index that was never used.** A team indexed `LOWER(email)` expecting case-insensitive login to be fast, but the application queried `WHERE email ILIKE ?` instead, so the plan still scanned. Aligning the query with the expression index (`WHERE lower(email) = lower(?)`) fixed it. Moral: **the plan is the truth**; always confirm the index is used.

## 12. Common mistakes

- Creating an index and not checking the plan to confirm it is used.
- Wrapping the indexed column in a function (`LOWER`, `DATE`, arithmetic).
- Leading-wildcard `LIKE '%text'` expecting an index to help.
- Wrong column order in a composite index (violating the leftmost-prefix rule).
- Indexing low-cardinality columns (booleans, statuses) alone.
- Over-indexing write-heavy tables; never dropping unused indexes.
- Forgetting foreign-key columns when joining or deleting parents.
- Testing on tiny development data, where a scan always looks fast.

## 13. Practice

1. Which of these can use `idx_country_age ON users(country, age)`: (a) `country = 'US'`, (b) `age = 25`, (c) `country = 'US' AND age > 40`, (d) `age = 25 AND country = 'US'`?
2. Why is `WHERE created_on >= '2024-01-01' AND created_on < '2025-01-01'` better than `WHERE strftime('%Y', created_on) = '2024'`?
3. A query filters `WHERE status = 'active'` (90% of rows). Should you index `status`? Why?
4. Create the right index so `SELECT id FROM users WHERE country = ? ORDER BY created_on LIMIT 10` needs no temp sort, and show the plan.
5. How many page reads does a B-tree with 500 keys per page need for 100 million rows?
6. Write a query that is answered entirely from `idx_country_age` (a covering query).
7. A table gets 10 000 inserts per second and 5 reads per second. Many indexes or few? Why?

<details>
<summary>Solutions</summary>

1. (a), (c) and (d) use it directly (the order of conditions in the `WHERE` does not matter; what matters is that the leading column, `country`, is constrained). (b) `age = 25` skips the leftmost column, so a plain index range lookup is impossible. Some optimizers can still do a **skip-scan** (probe each distinct country, then search `age` inside it) when statistics show the leading column has only a few distinct values; SQLite does exactly that after `ANALYZE` here (the plan says `ANY(country)`). It is far slower than a true prefix lookup and should not be relied on: create an index that leads with `age` if that query is hot.
   ```python
   for cond in ("country = 'US'", "age = 25", "country = 'US' AND age > 40", "age = 25 AND country = 'US'"):
       print(f"{cond:30}", plan(f"SELECT * FROM users WHERE {cond}")[0])
   # country = 'US'                 SEARCH users USING INDEX idx_country_age (country=?)
   # age = 25                       SEARCH users USING INDEX idx_country_age (ANY(country) AND age=?)
   # country = 'US' AND age > 40    SEARCH users USING INDEX idx_country_age (country=? AND age>?)
   # age = 25 AND country = 'US'    SEARCH users USING INDEX idx_country_age (country=? AND age=?)
   ```
2. The first compares the bare column to constants (an index range scan); the second computes a function for every row, so no index on `created_on` can be used.
3. No: 90% of rows match, so the planner scans anyway, and the index costs space and write time. (A partial index on the rare value `banned` is the useful one.)
4. ```python
   db.execute("CREATE INDEX idx_country_created ON users(country, created_on)")
   print(plan("SELECT id FROM users WHERE country = 'PK' ORDER BY created_on LIMIT 10"))
   # ['SEARCH users USING COVERING INDEX idx_country_created (country=?)']   rows come out already sorted by created_on
   ```
   Equality on `country` first, then the sort column, lets the index deliver rows in order, so the `LIMIT` can stop early.
5. `ceil(log(100_000_000, 500)) = 3` page reads.
   ```python
   print(math.ceil(math.log(100_000_000, 500)))                                 # 3
   ```
6. A query that selects only `country` and `age` and filters on `country` is covered by `idx_country_age`. With several overlapping indexes the planner chooses by its statistics, so we pin the index to demonstrate:
   ```python
   print(plan("SELECT country, age FROM users INDEXED BY idx_country_age WHERE country = 'DE'"))
   # ['SEARCH users USING COVERING INDEX idx_country_age (country=?)']
   ```
   (`INDEXED BY` is SQLite's hint; PostgreSQL has no hints, so there you would drop redundant indexes instead.)
7. Few: with 10 000 writes per second every extra index multiplies the write work, while 5 reads per second can tolerate scans or a single well-chosen index.

</details>

## 14. Check yourself

1. What data structure underlies most database indexes and why is it fast?
2. What does `SCAN` versus `SEARCH` mean in a plan?
3. State the leftmost-prefix rule.
4. Name three situations where an index is not used.
5. What is a covering index?
6. What does an index cost?
7. What should you do before and after adding an index?

<details>
<summary>Answers</summary>

1. A B-tree: sorted, short and wide, so any lookup takes a few page reads (`O(log n)`), and it also supports ranges and ordering.
2. `SCAN` reads the whole table (or whole index); `SEARCH` uses an index to jump to matching rows.
3. A composite index can be used for queries that filter on its leading columns in order (`a`, then `a,b`), not on later columns alone.
4. A function on the column, a leading-wildcard `LIKE`, low selectivity (matches most rows), a type mismatch, skipping the leftmost column, tiny tables.
5. An index containing every column the query needs, so the table is never read.
6. Slower writes (every insert/update/delete maintains it), extra storage and memory.
7. Check the query plan (and timing) before to find the problem and after to confirm the index is used and writes are still acceptable.

</details>

[Back to indexes and query plans](README.md)
