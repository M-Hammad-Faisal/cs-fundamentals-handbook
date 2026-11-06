# Transactions, ACID and Isolation: Exercises

## Concepts
1. Write the transaction for transferring 100 from account A to B. What should happen if the second update fails?
2. Match each property to its mechanism: Atomicity, Consistency, Isolation, Durability vs undo log, constraints, locks/MVCC, write-ahead log.
3. For each scenario, name the anomaly:
   - a) You read a balance of 500, another transaction commits a change, and your second read shows 400.
   - b) You read another transaction's value that is later rolled back.
   - c) Two clients add 10 to a counter and the result is only +10.
   - d) Re-running `SELECT COUNT(*) ... WHERE status='open'` in one transaction returns a different count.
   - e) Two doctors both see "2 on call", each takes themselves off, leaving 0.
4. A database uses MVCC. A long report runs for 10 minutes while orders are inserted. Does the report block the inserts? Will it see them?

## Hands-on
5. Run `demo_transactions.py`. Change fix B so that both clients use `BEGIN IMMEDIATE` and observe the "database is locked" error. How would you handle it in production (hint: timeout and retry)?
6. Add a `CHECK` constraint to prevent a negative stock count, then write the safe "buy one item" statement and how you verify success from Python.
7. Implement **optimistic locking** with a `version` column in Python and show that a stale update is rejected.
8. Write an **idempotent** payment function that can be retried safely using an idempotency key.

## Design
9. Two services each own a database: `orders` and `payments`. Sketch a saga for "place order" with compensating actions for each failure point.
10. Describe a deadlock between two transfers (A to B and B to A) and give two ways to prevent it.

<details>
<summary>Solutions</summary>

**1.**
```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE name = 'A';
UPDATE accounts SET balance = balance + 100 WHERE name = 'B';
COMMIT;
```
If the second update fails (constraint, crash, error) execute `ROLLBACK`, which undoes the first update too; the database returns to its prior state.

**2.** Atomicity: undo log. Consistency: constraints (and application rules). Isolation: locks / MVCC. Durability: write-ahead log.

**3.** a) non-repeatable read; b) dirty read; c) lost update; d) phantom read; e) write skew.

**4.** No, it does not block inserts: MVCC readers use a snapshot and writers create new row versions. Under snapshot-style isolation the report does **not** see rows committed after its snapshot (under plain read committed each *statement* gets a fresh snapshot, so later statements can see newer data).

**5.** With both connections using `BEGIN IMMEDIATE` the second raises `sqlite3.OperationalError: database is locked` after its timeout. In production, set a sensible busy timeout (`sqlite3.connect(..., timeout=5)`) and retry the whole transaction on that error with a short backoff.

**6.**
```python
conn.execute("CREATE TABLE stock (id INTEGER PRIMARY KEY, qty INTEGER NOT NULL CHECK (qty >= 0))")
cur = conn.execute("UPDATE stock SET qty = qty - 1 WHERE id = ? AND qty > 0", (item_id,))
if cur.rowcount == 1:
    ...   # purchase succeeded
else:
    ...   # sold out
```

**7.**
```python
def update_price(conn, product_id, new_price, expected_version):
    cur = conn.execute(
        "UPDATE products SET price = ?, version = version + 1 "
        "WHERE id = ? AND version = ?",
        (new_price, product_id, expected_version),
    )
    if cur.rowcount == 0:
        raise RuntimeError("Conflict: row was changed by someone else, re-read and retry")
```
A second writer holding the old `expected_version` matches 0 rows and is rejected.

**8.**
```python
def pay(conn, idempotency_key, order_id, amount):
    try:
        with conn:
            conn.execute(
                "INSERT INTO payments (idempotency_key, order_id, amount) VALUES (?, ?, ?)",
                (idempotency_key, order_id, amount),   # idempotency_key has a UNIQUE constraint
            )
        return "charged"
    except sqlite3.IntegrityError:
        return "already processed"                      # a retry: do nothing, return the same result
```

**9.** Steps: (1) create order as `PENDING` in the orders DB; (2) reserve stock; (3) charge payment; (4) mark order `CONFIRMED`. Compensations: if (3) fails, release the reserved stock and mark the order `CANCELLED`; if (4) fails after charging, issue a refund and release stock. Each step and compensation must be idempotent and retried until it succeeds; publish events through an outbox so messages are not lost.

**10.** T1 transfers A to B and locks A then B; T2 transfers B to A and locks B then A. Each holds one lock and waits for the other. Prevent by (a) always locking accounts in a consistent order (for example, lower id first) regardless of transfer direction, and (b) keeping transactions short, with retry on deadlock errors. Setting a lock timeout also bounds the waiting.

</details>
