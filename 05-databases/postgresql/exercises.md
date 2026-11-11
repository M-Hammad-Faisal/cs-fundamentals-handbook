# PostgreSQL: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## PostgreSQL-Specific Features

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

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [PostgreSQL-Specific Features](01-postgresql-specific-features.md)
