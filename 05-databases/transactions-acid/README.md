# Transactions, ACID and Isolation

## Detailed lesson (start here if you are new)

- [Transactions lab](01-transactions-lab.md): ACID with two real connections, isolation and snapshots, lost updates and three fixes, savepoints, durability, idempotency, isolation levels

The rest of this page is the quick reference.

A runnable companion, [`demo_transactions.py`](demo_transactions.py), demonstrates rollback, a lost update, and two fixes using SQLite. Run it with `python3 demo_transactions.py`.

## 1. The concept

A **transaction** is a group of operations that the database treats as **one indivisible unit**: either all of them take effect, or none do. The classic example is a bank transfer:

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE name = 'alice';
UPDATE accounts SET balance = balance + 100 WHERE name = 'bob';
COMMIT;       -- both changes become permanent together
-- or ROLLBACK;  -- undo everything since BEGIN
```

If the system crashes between the two updates, you must not end up with money removed from Alice but never added to Bob. Transactions prevent that.

## 2. ACID

| Property | Meaning | Mechanism |
|----------|---------|-----------|
| **Atomicity** | All or nothing | Undo log / rollback |
| **Consistency** | A transaction moves the database from one valid state to another; constraints always hold | Constraints (`CHECK`, `FOREIGN KEY`, `UNIQUE`), application rules |
| **Isolation** | Concurrent transactions do not interfere; each behaves as if it ran alone (to a configurable degree) | Locks, MVCC |
| **Durability** | Once committed, data survives crashes and power loss | Write-ahead log (WAL) flushed to disk |

The demo's first scenario shows atomicity and consistency together: the `CHECK (balance >= 0)` constraint fails on the second `UPDATE`, we `ROLLBACK`, and Bob's earlier `+150` is undone.

### Durability and the write-ahead log

A database does not rewrite data pages on every commit. It first appends the change to a **write-ahead log (WAL)** and flushes that sequential log to disk, then applies the change to data pages later. After a crash it **replays** the log to recover committed work and **undoes** uncommitted work. Sequential log writes are fast, which makes durability affordable.

## 3. Concurrency problems (anomalies)

When many transactions run at once, these can occur:

| Anomaly | What happens | Example |
|---------|--------------|---------|
| **Dirty read** | You read another transaction's *uncommitted* change, which may be rolled back | See a balance that never officially existed |
| **Non-repeatable read** | You read the same row twice in one transaction and get different values (someone committed in between) | A price changes mid-calculation |
| **Phantom read** | You re-run a range query and new rows appear (or vanish) | A report counts 10 orders, then 11 |
| **Lost update** | Two transactions read the same value, then both write, and one overwrites the other | Two clients each add 10 to a counter, final value only +10 |
| **Write skew** | Two transactions read overlapping data and write different rows, jointly breaking an invariant | Two on-call doctors both go off duty, leaving nobody on call |

### The lost update, live

The demo reproduces it with read-modify-write in application code:

```python
read_a = a.execute("SELECT balance FROM accounts WHERE name='alice'").fetchone()[0]   # 100
read_b = b.execute("SELECT balance FROM accounts WHERE name='alice'").fetchone()[0]   # 100
a.execute("UPDATE accounts SET balance = ? WHERE name='alice'", (read_a + 10,))        # 110
b.execute("UPDATE accounts SET balance = ? WHERE name='alice'", (read_b + 10,))        # 110, not 120
```

Result: `expected 120, got: 110`. Two fixes:

1. **Let the database do it atomically:** `UPDATE accounts SET balance = balance + 10 WHERE name = 'alice'`. No read in application code, no race.
2. **Lock before reading:** read inside a transaction that holds a write lock (`BEGIN IMMEDIATE` in SQLite, `SELECT ... FOR UPDATE` in PostgreSQL/MySQL), so the second writer waits.

## 4. Isolation levels

Isolation is a trade-off between **correctness** and **concurrency**. SQL defines four levels:

| Level | Dirty read | Non-repeatable read | Phantom read |
|-------|:----------:|:-------------------:|:------------:|
| **Read uncommitted** | Possible | Possible | Possible |
| **Read committed** | Prevented | Possible | Possible |
| **Repeatable read** | Prevented | Prevented | Possible* |
| **Serializable** | Prevented | Prevented | Prevented |

*Exact behavior varies by engine. For example, PostgreSQL's repeatable read also prevents phantoms (it uses snapshot isolation), and MySQL InnoDB's repeatable read prevents most phantoms with gap locks. Snapshot isolation still allows **write skew**; only **serializable** prevents it.

**Defaults:** PostgreSQL uses *read committed*; MySQL (InnoDB) uses *repeatable read*; SQLite behaves as *serializable* (one writer at a time); Oracle uses *read committed*; SQL Server uses *read committed*.

```postgresql
BEGIN ISOLATION LEVEL SERIALIZABLE;
-- ... statements ...
COMMIT;
```

Higher isolation means fewer anomalies but more blocking or more transaction **retries** (serialization failures that the application must retry).

## 5. How isolation is implemented

### Locks (pessimistic concurrency)

- **Shared (read) lock:** many readers at once.
- **Exclusive (write) lock:** one writer, no one else reads or writes the row.
- **Granularity:** row, page, table. Finer locks allow more concurrency but cost more bookkeeping.
- **Two-phase locking (2PL):** acquire locks while working, release them all at commit; guarantees serializability but can block heavily.

### MVCC (multi-version concurrency control)

Used by PostgreSQL, MySQL InnoDB, Oracle and others. The database keeps **multiple versions** of each row. A reader sees a consistent **snapshot** from when its transaction (or statement) began, so **readers do not block writers and writers do not block readers**. Old versions are cleaned up later (PostgreSQL `VACUUM`, InnoDB purge).

The demo's last scenario shows this effect: a reader does not see the writer's uncommitted `999`, and sees it only after the commit.

### Optimistic vs pessimistic

| Approach | Idea | Use when |
|----------|------|----------|
| **Pessimistic** | Lock first (`SELECT ... FOR UPDATE`) and assume conflicts | Conflicts are common; the work is short |
| **Optimistic** | No lock; detect conflicts at write time and retry | Conflicts are rare; long user "think time" |

Optimistic locking uses a **version column**:

```sql
UPDATE products
SET stock = stock - 1, version = version + 1
WHERE id = 7 AND version = 3;        -- 0 rows updated means someone else changed it: re-read and retry
```

## 6. Deadlocks

A **deadlock** occurs when transactions wait for each other in a cycle:

```
T1: locks row A, then wants row B
T2: locks row B, then wants row A      -> both wait forever
```

Databases detect cycles and abort one transaction (the "victim") with an error, which your code must catch and **retry**.

**Prevention:**

- Access rows in a **consistent order** everywhere (always lower id first).
- Keep transactions **short**; never wait on a user or network call inside one.
- Use the lowest isolation level that is correct, and take locks only when needed.

## 7. Savepoints, autocommit, and practical usage

```sql
BEGIN;
INSERT INTO orders ...;
SAVEPOINT before_items;
INSERT INTO order_items ...;          -- suppose this fails
ROLLBACK TO before_items;             -- undo only the items, keep the order
COMMIT;
```

- **Autocommit:** most drivers commit each statement automatically unless you start a transaction.
- **Python (`sqlite3`, `psycopg`):** use the connection as a context manager (`with conn:`) so success commits and an exception rolls back.
- **ORMs:** Django `transaction.atomic()`, SQLAlchemy `session.begin()`.

```python
import sqlite3
conn = sqlite3.connect("bank.db")
with conn:                                # commits on success, rolls back on exception
    conn.execute("UPDATE accounts SET balance = balance - 100 WHERE name = 'alice'")
    conn.execute("UPDATE accounts SET balance = balance + 100 WHERE name = 'bob'")
```

## 8. Beyond one database

A transaction across **several databases or services** cannot use a single local commit.

| Technique | Idea | Trade-off |
|-----------|------|-----------|
| **Two-phase commit (2PC)** | A coordinator asks everyone to *prepare*, then *commit* | Strong consistency, but blocking and fragile if the coordinator dies |
| **Saga** | A chain of local transactions with **compensating actions** (refund, release stock) to undo earlier steps | No global lock, but only *eventual* consistency and more code |
| **Outbox pattern** | Write the business change and an "event to publish" in one local transaction; a relay publishes the event | Reliable messaging without distributed transactions |
| **Idempotency keys** | Retried requests with the same key do not repeat their effect | Required for safe retries |

The **CAP theorem** says that during a network partition a distributed system must choose between consistency and availability, which is why many large systems accept eventual consistency (see [NoSQL](../nosql/README.md)).

## 9. Two real-world examples

### Example 1: Checkout and inventory

When a customer pays, the system must (a) create the order, (b) reduce stock, and (c) record the payment. Wrapped in one transaction, a failure at step (c) rolls back (a) and (b), so you never ship items that were not paid for or lose stock to a failed payment. To prevent **overselling** the last item when two customers click at once, the stock update must be atomic and conditional: `UPDATE stock SET qty = qty - 1 WHERE id = ? AND qty > 0`, then check that exactly one row was changed. That single statement is the difference between a correct shop and one that sells items it does not have.

### Example 2: Ticket booking and seat selection

Two users select the same seat simultaneously. With **pessimistic locking** (`SELECT ... FOR UPDATE` on the seat row), the second user waits and then sees the seat is taken. With **optimistic locking** (a version column), both proceed but only the first `UPDATE ... WHERE version = ?` succeeds and the second retries or is told "seat no longer available". Systems with long holds (the 10 minutes you have to pay) use a **reservation** row with an expiry time rather than holding a database lock the whole time.

## 10. Tips, tricks and pitfalls

- **Do arithmetic in SQL** (`balance = balance + 10`) instead of read, compute, write in the application.
- **Keep transactions short.** Never hold one open across user input, HTTP calls, or sleeps.
- **Always handle serialization failures and deadlocks with retries.** Make the retried code idempotent.
- **Take locks in a consistent order** to avoid deadlocks.
- **Use constraints** as a safety net: `UNIQUE`, `CHECK`, `FOREIGN KEY`. They hold even when application code has a bug.
- **Know your engine's default isolation level** and its quirks; "repeatable read" means different things in PostgreSQL and MySQL.
- **Do not assume `SELECT` then `INSERT` is safe** (check-then-act races). Use `INSERT ... ON CONFLICT` (PostgreSQL/SQLite) or a unique index.
- **Idempotency keys** make payment and webhook handling safe when clients retry.
- **A rolled-back transaction still consumes resources** and may leave gaps in auto-increment values; that is normal.
- **Use `SELECT ... FOR UPDATE`** deliberately; locking more rows than needed hurts concurrency.

## 11. Check yourself

1. What does each letter of ACID mean, and which mechanism provides each?
2. Name three concurrency anomalies and describe one.
3. How does the lost-update problem arise and how do you fix it?
4. What are the four isolation levels, and what does each prevent?
5. How does MVCC let readers and writers avoid blocking each other?
6. What is a deadlock, and how do you reduce them?
7. Compare optimistic and pessimistic locking.
8. How does a write-ahead log provide durability?
9. Why is a single atomic `UPDATE ... WHERE qty > 0` the right way to avoid overselling?
10. What is a saga and when would you use one instead of two-phase commit?

<details>
<summary>Answers</summary>

1. Atomicity (all or nothing; undo log), Consistency (valid state to valid state; constraints), Isolation (concurrent transactions do not interfere; locks/MVCC), Durability (committed data survives crashes; write-ahead log).
2. Dirty read, non-repeatable read, phantom read, lost update, write skew. For example a lost update: two transactions read 100, each writes 110, and one increment disappears.
3. Both read the same old value and write back results based on it, so one overwrites the other. Fix with an atomic SQL update (`x = x + 10`), a row lock (`SELECT ... FOR UPDATE`), or optimistic version checks.
4. Read uncommitted (nothing), read committed (dirty reads), repeatable read (dirty and non-repeatable reads), serializable (all anomalies including phantoms and write skew). Details vary by engine.
5. It keeps several versions of each row; each reader uses a consistent snapshot, so reads need no locks and are not blocked by writers, and writers do not wait for readers.
6. Transactions wait on each other in a cycle; the database aborts a victim. Reduce them with consistent lock ordering, short transactions, and retry logic.
7. Pessimistic locks first and blocks conflicting work (good when conflicts are common). Optimistic proceeds without locks and detects conflicts at write time with a version check, then retries (good when conflicts are rare).
8. Changes are appended to a sequential log and flushed to disk before commit is acknowledged; after a crash the log is replayed to restore committed work.
9. The check and the decrement happen in one atomic statement, so two concurrent buyers cannot both see stock available and both decrement it. You then verify that one row was affected.
10. A saga is a sequence of local transactions with compensating actions to undo them. Use it across services or databases where a blocking, coordinator-dependent 2PC is impractical, accepting eventual consistency.

</details>
