# PostgreSQL-Specific Features

> **Verification status (read this first).** Every other lesson in this handbook was run and its output checked. **The SQL below was written from the PostgreSQL documentation and not executed**, because no PostgreSQL server was available when it was written. Output shown in comments is what the documented behaviour produces, but treat it as **unverified until you run it**. The easiest way is Docker: `docker run --rm -e POSTGRES_PASSWORD=pw -p 5432:5432 postgres:17`, then `psql -h localhost -U postgres`. If a result differs from this page, trust your server and please open an issue.

**Prerequisites:** [relational SQL](../relational-sql/README.md), [indexes and query plans](../indexes-query-plans/README.md), [transactions and ACID](../transactions-acid/README.md). **You will learn:** what makes PostgreSQL ("Postgres") different from the standard SQL you already know and from SQLite: its **richer data types**, `RETURNING` and **upserts**, **index types** for different workloads, how **MVCC** and `VACUUM` work, how to build a **job queue** safely, **`LISTEN/NOTIFY`**, reading **`EXPLAIN ANALYZE`**, and the `psql` client.

## 1. In plain words

PostgreSQL is a free, open-source relational database known for correctness and extensibility. It follows the SQL standard closely, then adds a lot: JSON that can be indexed, arrays, ranges, full-text search, many index types, custom types and extensions (PostGIS for maps, pgvector for embeddings). SQLite is one file inside your program; Postgres is a **server** that many clients connect to at once, with real concurrency, roles and permissions.

## 2. Getting connected: `psql` essentials

```text
psql -h localhost -U postgres          connect
\l            list databases              \c name       switch database
\dt           list tables                 \d table      describe a table (columns, indexes, constraints)
\di           list indexes                \dn           list schemas
\x            toggle expanded output      \timing       show how long each query takes
\i file.sql   run a script                \q            quit
```

## 3. Data types beyond the basics

| Type | Use | Example literal |
|------|-----|-----------------|
| `integer`, `bigint`, `numeric(12,2)` | numbers; use **`numeric` for money**, never `float` | `19.99` |
| `text` | any-length string (no performance penalty versus `varchar(n)`) | `'hello'` |
| `boolean` | true/false | `true` |
| `timestamptz` | an instant in time, stored as UTC and shown in the session's time zone: **prefer it over `timestamp`** | `'2026-03-01 09:00+00'` |
| `date`, `interval` | calendar date; a span of time | `interval '3 days'` |
| `uuid` | globally unique ids | `gen_random_uuid()` |
| `jsonb` | JSON stored in a binary, **indexable** form | `'{"a": 1}'::jsonb` |
| `text[]`, `integer[]` | arrays | `ARRAY['a','b']` |
| `int4range`, `tstzrange` | ranges (with overlap operators) | `'[1,10)'::int4range` |
| `enum` | a closed set of labels | `CREATE TYPE mood AS ENUM ('sad','ok','happy')` |

**Primary keys:** the modern way is an identity column, not the old `SERIAL`:

```sql
CREATE TABLE users (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email      text NOT NULL UNIQUE,
    profile    jsonb NOT NULL DEFAULT '{}',
    tags       text[] NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now()
);
```

### JSONB: documents inside a relational table

```sql
INSERT INTO users (email, profile, tags)
VALUES ('ada@example.com', '{"name": "Ada", "address": {"city": "London"}, "langs": ["en", "fr"]}', ARRAY['admin', 'beta']);

SELECT profile ->> 'name'                AS name,        -- ->> returns text, -> returns jsonb
       profile -> 'address' ->> 'city'   AS city,        -- chain to dig into nested objects
       profile #>> '{address,city}'      AS city_again   -- path form
FROM users;
--  name | city   | city_again
--  Ada  | London | London

SELECT email FROM users WHERE profile @> '{"langs": ["fr"]}';       -- containment: "profile contains this JSON"  -> ada@example.com
SELECT email FROM users WHERE 'admin' = ANY (tags);                 -- array membership
SELECT email FROM users WHERE tags && ARRAY['beta', 'staff'];       -- arrays overlap

UPDATE users SET profile = jsonb_set(profile, '{address,city}', '"Paris"') WHERE email = 'ada@example.com';
```

Use `jsonb` for genuinely **variable or sparse attributes**; keep core fields you filter, join and constrain on (ids, email, status, amounts) as **real columns**. See the trade-off in the [NoSQL lesson](../nosql/README.md).

### Ranges and exclusion constraints

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE TABLE bookings (
    room   int,
    during tstzrange,
    EXCLUDE USING gist (room WITH =, during WITH &&)       -- no two rows may have the same room and overlapping times
);
```

The database itself then **refuses double bookings**, with no application race to get wrong: a feature few databases offer.

## 4. `RETURNING`, upserts and CTEs

**`RETURNING`** gives back the rows you just changed, saving a second query (and avoiding races to read the generated id):

```sql
INSERT INTO users (email) VALUES ('bob@example.com') RETURNING id, created_at;
UPDATE users SET tags = tags || 'vip' WHERE email = 'bob@example.com' RETURNING *;
DELETE FROM users WHERE email = 'bob@example.com' RETURNING id;
```

**Upsert** (insert or update) in one atomic statement with `ON CONFLICT`:

```sql
CREATE TABLE page_views (page text PRIMARY KEY, views bigint NOT NULL);

INSERT INTO page_views (page, views) VALUES ('/home', 1)
ON CONFLICT (page) DO UPDATE SET views = page_views.views + 1;     -- first call inserts 1; later calls add 1, safely under concurrency

INSERT INTO users (email) VALUES ('ada@example.com') ON CONFLICT (email) DO NOTHING;   -- ignore duplicates
```

(`EXCLUDED` refers to the row you tried to insert: `SET name = EXCLUDED.name`.)

**CTEs** (`WITH`) name a sub-query, and Postgres supports **data-modifying CTEs** and **recursive** ones:

```sql
-- move rows between tables atomically
WITH moved AS (DELETE FROM jobs WHERE done RETURNING *)
INSERT INTO jobs_archive SELECT * FROM moved;

-- walk a tree (employees and their managers)
WITH RECURSIVE chain AS (
    SELECT id, name, manager_id, 1 AS depth FROM employees WHERE id = 7
    UNION ALL
    SELECT e.id, e.name, e.manager_id, c.depth + 1 FROM employees e JOIN chain c ON e.id = c.manager_id
)
SELECT * FROM chain;
```

Other conveniences: `DISTINCT ON (col)` (first row per group), `FILTER` on aggregates (`count(*) FILTER (WHERE active)`), `generate_series`, `string_agg`, `array_agg`, `LATERAL` joins, and the window functions from the [window-functions lab](../relational-sql/README.md).

## 5. Index types: pick by the question you ask

You know the B-tree from the [indexes lesson](../indexes-query-plans/README.md). Postgres has several more:

| Index | Best for | Example |
|-------|----------|---------|
| **B-tree** (default) | equality, ranges, sorting (`=`, `<`, `BETWEEN`, `ORDER BY`) | `CREATE INDEX ON users (email);` |
| **Hash** | equality only (rarely better than B-tree) | `CREATE INDEX ON t USING hash (col);` |
| **GIN** | "contains" on composite values: **jsonb, arrays, full-text** | `CREATE INDEX ON users USING gin (profile);` |
| **GiST** | geometry, ranges, nearest-neighbor, exclusion constraints | `CREATE INDEX ON places USING gist (location);` |
| **BRIN** | huge tables whose values correlate with physical order (time series, append-only): tiny index | `CREATE INDEX ON events USING brin (created_at);` |
| **Partial** | index only the rows you query | `CREATE INDEX ON orders (customer_id) WHERE status = 'open';` |
| **Expression** | queries on a computed value | `CREATE INDEX ON users (lower(email));` |
| **Covering** (`INCLUDE`) | enable index-only scans | `CREATE INDEX ON orders (customer_id) INCLUDE (total);` |

Two practical rules: a query must use the **same expression** to benefit from an expression index (`WHERE lower(email) = 'x'`), and a **partial index** is small and fast when most rows are irrelevant (the 5 percent of "open" orders). Build on a live table without blocking writes using `CREATE INDEX CONCURRENTLY`.

Full-text search uses GIN on a `tsvector`:

```sql
CREATE INDEX docs_fts ON docs USING gin (to_tsvector('english', body));
SELECT id FROM docs WHERE to_tsvector('english', body) @@ websearch_to_tsquery('english', 'quick fox');
```

## 6. MVCC, VACUUM and why Postgres behaves as it does

Postgres uses **multi-version concurrency control** (MVCC): an `UPDATE` does not overwrite a row, it writes a **new version** and marks the old one as expired, and each transaction sees the versions that were valid when its **snapshot** was taken. The payoffs:

- **Readers never block writers and writers never block readers.**
- Consistent snapshots with no read locks (the "I" in ACID, see [transactions](../transactions-acid/README.md)).

The costs:

- **Dead row versions pile up** ("bloat"). **`VACUUM`** reclaims them and **autovacuum** runs it for you in the background; if it falls behind (long-running transactions hold old snapshots open!), tables and indexes grow and queries slow down.
- **`ANALYZE`** refreshes the statistics the planner uses to choose plans (autovacuum does this too). After a big load, run it by hand.
- `UPDATE`-heavy tables benefit from leaving free space (`fillfactor`) so updates can stay on the same page (HOT updates).

```sql
SELECT relname, n_live_tup, n_dead_tup, last_autovacuum FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 5;     -- who has the most dead rows?
SELECT pid, now() - xact_start AS open_for, state, query FROM pg_stat_activity WHERE state <> 'idle' ORDER BY xact_start;   -- find long transactions
```

**Isolation levels.** The default is `READ COMMITTED` (each statement sees the data committed before it started). `REPEATABLE READ` gives one snapshot for the whole transaction. `SERIALIZABLE` detects conflicts and may abort a transaction with error `40001`, which your application **must retry**.

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
-- all reads here see the same snapshot
COMMIT;
```

## 7. Locking: queues with `FOR UPDATE SKIP LOCKED`

To let many workers pull jobs from a table without two of them taking the same job (and without waiting on each other):

```sql
-- each worker runs this in a transaction
BEGIN;
SELECT id, payload FROM jobs
WHERE status = 'queued'
ORDER BY id
LIMIT 1
FOR UPDATE SKIP LOCKED;        -- lock the row for me; skip rows another worker already locked
-- ... do the work ...
UPDATE jobs SET status = 'done' WHERE id = :id;
COMMIT;
```

`FOR UPDATE` locks the selected rows until the transaction ends; `SKIP LOCKED` makes other workers pass over them instead of waiting. This pattern turns a table into a simple, reliable queue (until you outgrow it and need a broker).

Other locks you will meet: `SELECT ... FOR SHARE`, **advisory locks** (`pg_advisory_lock(key)`) for application-level mutual exclusion, and **deadlocks** (Postgres detects them and aborts one transaction: always take locks in a consistent order, see [deadlocks](../../06-operating-systems/concurrency-deadlocks/README.md)).

## 8. `LISTEN` / `NOTIFY`: simple pub/sub

```sql
LISTEN new_order;                                  -- connection A subscribes
NOTIFY new_order, 'order 42';                      -- connection B publishes (delivered to A when B commits)
SELECT pg_notify('new_order', json_build_object('id', 42)::text);      -- the function form, usable inside triggers
```

It is perfect for waking workers or invalidating caches, but messages are **not persisted** (a disconnected listener misses them) and payloads are small (about 8 KB), so treat it as a *nudge* and keep the data in a table.

## 9. Reading `EXPLAIN (ANALYZE, BUFFERS)`

`EXPLAIN` shows the plan the optimizer chose; **`EXPLAIN ANALYZE` actually runs the query** and adds real timings and row counts (so wrap writes in a transaction you roll back).

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE customer_id = 42 AND status = 'open';
```

A trimmed, illustrative plan (your numbers will differ):

```text
Index Scan using orders_customer_open_idx on orders  (cost=0.29..8.31 rows=1 width=64) (actual time=0.021..0.022 rows=1 loops=1)
  Index Cond: (customer_id = 42)
  Buffers: shared hit=3
Planning Time: 0.110 ms
Execution Time: 0.045 ms
```

What to look for:

| Plan node | Meaning |
|-----------|---------|
| **Seq Scan** | reads the whole table (fine for small tables or when most rows match; suspicious on a big table with a selective filter) |
| **Index Scan / Index Only Scan** | uses an index (index-only avoids touching the table) |
| **Bitmap Heap Scan** | combines several index results, then reads table pages in order |
| **Nested Loop / Hash Join / Merge Join** | the join strategy (hash joins for big unsorted sets; nested loop for few rows with an index) |
| **estimated `rows=` far from `actual rows=`** | stale or poor statistics: run `ANALYZE`, consider extended statistics |
| **Buffers: shared read** | pages fetched from disk (versus `hit` from memory cache) |
| **Sort Method: external merge Disk** | not enough `work_mem`: the sort spilled to disk |

The workflow from the [indexes lesson](../indexes-query-plans/README.md) applies: find the slow query (`pg_stat_statements` extension lists the heaviest), read its plan, add the right index, and compare the plan again.

## 10. Other things worth knowing

- **Schemas** group tables inside a database (`public` by default); **roles** are users and groups; grant least privilege (`GRANT SELECT ON ... TO reporting;`).
- **Transactional DDL:** `CREATE`/`ALTER`/`DROP` run inside transactions and roll back cleanly, so a failed migration leaves no half-changed schema.
- **Partitioning** splits a huge table by range, list or hash (`PARTITION BY RANGE (created_at)`) so old data can be dropped as a whole partition.
- **Replication:** streaming replicas for read scaling and failover; **logical replication** for selective or cross-version copies; **WAL** (the write-ahead log, see [transactions](../transactions-acid/README.md)) underpins both, plus point-in-time recovery.
- **Connection management:** each connection is a process with real memory cost, so use a **pooler** (PgBouncer) instead of thousands of direct connections.
- **Extensions:** `pg_stat_statements`, `pgcrypto`, `PostGIS`, `pgvector`, `pg_trgm` (fuzzy text search).

## 11. Two real-world examples

**Example 1: A queue without a queue server.** A small SaaS needed background emails and reports. Rather than run a broker, it stored jobs in a table and let workers claim them with `FOR UPDATE SKIP LOCKED`. Jobs, their results and the business data changed in **one transaction**, so there was never a state where an email was sent but the order was not saved. At a few hundred jobs per second this was plenty, and a broker could be added later.

**Example 2: A mysteriously growing table.** A table updated millions of times a day kept growing and slowing down. `pg_stat_user_tables` showed millions of dead tuples; `pg_stat_activity` showed a forgotten transaction, open for days, holding an old snapshot so autovacuum could not remove anything. Closing it and adding an idle-transaction timeout let vacuum catch up and the table shrank back to normal speed.

## 12. Common mistakes

- Using `timestamp` instead of `timestamptz`, then getting time-zone bugs.
- Storing money in `float`; use `numeric` (or integer cents).
- Putting everything in `jsonb` and losing constraints, types and cheap queries.
- `SELECT *` in application code and `OFFSET` for deep pagination (use keyset pagination: `WHERE id > :last ORDER BY id LIMIT 50`).
- Forgetting that an index on `email` does not help `WHERE lower(email) = ...`.
- Leaving transactions open (idle in transaction): they block vacuum and hold locks.
- Opening a database connection per request without a pool.
- Ignoring `SERIALIZABLE` failures instead of retrying them.
- Running `EXPLAIN ANALYZE` on a `DELETE` or `UPDATE` in production without a surrounding `BEGIN ... ROLLBACK`.

## 13. Practice

(These need a PostgreSQL server; use the Docker command from the top.)

1. Create a table `products(id, name, attrs jsonb)`, insert two rows with different attributes and query those where `attrs @> '{"color": "red"}'`. Add a GIN index and check with `EXPLAIN` whether it is used (you may need enough rows, or `SET enable_seqscan = off` to see the index choice).
2. Write an upsert that counts logins per user in `logins(user_id primary key, n)`.
3. Create a partial index so that looking up *unshipped* orders for a customer is fast. Why is it smaller than a full index?
4. Using `FOR UPDATE SKIP LOCKED`, write the claim query for a worker; why can two workers not get the same job?
5. Explain how an `UPDATE` works under MVCC and why `VACUUM` is needed.
6. A query shows `rows=1` estimated but `rows=250000` actual. What do you do first?

<details>
<summary>Solutions</summary>

1. ```sql
   CREATE TABLE products (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, name text, attrs jsonb);
   INSERT INTO products (name, attrs) VALUES ('shirt', '{"color": "red", "size": "M"}'), ('mug', '{"material": "clay"}');
   SELECT name FROM products WHERE attrs @> '{"color": "red"}';          -- shirt
   CREATE INDEX products_attrs_gin ON products USING gin (attrs);
   ```
   On two rows the planner will choose a sequential scan anyway; with thousands of rows (or `SET enable_seqscan = off` for the experiment) `EXPLAIN` shows a Bitmap Index Scan on `products_attrs_gin`.
2. ```sql
   INSERT INTO logins (user_id, n) VALUES (42, 1)
   ON CONFLICT (user_id) DO UPDATE SET n = logins.n + 1;
   ```
3. ```sql
   CREATE INDEX orders_unshipped_idx ON orders (customer_id) WHERE shipped_at IS NULL;
   ```
   It contains only rows still unshipped (a small fraction), so it is smaller, cheaper to maintain and faster to scan; queries must include `shipped_at IS NULL` to use it.
4. ```sql
   SELECT id FROM jobs WHERE status = 'queued' ORDER BY id LIMIT 1 FOR UPDATE SKIP LOCKED;
   ```
   The first worker locks the row; a second worker's query skips locked rows and takes the next one, so no job is claimed twice and nobody waits.
5. The `UPDATE` writes a new row version and marks the old one with the transaction id that expired it; transactions with older snapshots still see the old version. Once no snapshot can see the old version it is dead space, which `VACUUM` reclaims for reuse.
6. Run `ANALYZE table_name` to refresh statistics (a bad estimate leads the planner to pick a poor join or scan); if it persists, check for correlated columns (extended statistics: `CREATE STATISTICS`) or skewed data, and look at the query for expressions the planner cannot estimate.

</details>

## 14. Check yourself

1. Why prefer `timestamptz` and `numeric` for time and money?
2. What does `INSERT ... ON CONFLICT DO UPDATE` give you that "select, then insert or update" does not?
3. Which index type for jsonb containment, for a huge append-only time series, and for "only open orders"?
4. What is MVCC, and what problem does it create that `VACUUM` solves?
5. What does `FOR UPDATE SKIP LOCKED` do?
6. What is the difference between `EXPLAIN` and `EXPLAIN ANALYZE`?
7. Why is `NOTIFY` a nudge, not a message queue?

<details>
<summary>Answers</summary>

1. `timestamptz` stores an unambiguous instant (UTC) and avoids time-zone errors; `numeric` is exact decimal arithmetic, unlike binary floating point.
2. One atomic statement that is safe under concurrency; the two-step version races (two clients can both see "missing" and both insert).
3. GIN for jsonb containment; BRIN for the huge append-only series; a partial index (`WHERE status = 'open'`) for open orders.
4. Multi-version concurrency control keeps old row versions so readers and writers do not block each other; the old versions become dead space that `VACUUM` reclaims.
5. It locks the chosen rows and makes other transactions skip rows that are already locked, so workers can claim distinct jobs without waiting.
6. `EXPLAIN` shows the planned strategy and cost estimates without running the query; `EXPLAIN ANALYZE` runs it and reports actual timings and row counts.
7. Notifications are not stored (offline listeners miss them) and carry small payloads, so keep durable data in a table and use `NOTIFY` only to wake consumers.

</details>

[Back to PostgreSQL](README.md)
