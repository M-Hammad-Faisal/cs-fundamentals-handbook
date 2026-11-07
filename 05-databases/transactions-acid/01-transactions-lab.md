# Transactions Lab: ACID, Concurrency and Lost Updates

**Prerequisites:** [SQL first steps](../relational-sql/01-sql-first-steps.md), [race conditions](../../06-operating-systems/concurrency-deadlocks/01-race-conditions-and-synchronization.md), [deadlock](../../06-operating-systems/concurrency-deadlocks/02-deadlock.md). **You will learn (by running two real database connections):** what a **transaction** is, the four **ACID** guarantees, how a failure in the middle is **rolled back**, how **isolation** keeps concurrent users from seeing each other's half-finished work, how a **lost update** really happens and **three ways to prevent it** (atomic `UPDATE`, locking, optimistic versioning), plus **savepoints**, **idempotency**, **isolation levels** and the anomalies they allow. Examples use SQLite files so two connections can interact.

## 1. In plain words

Moving 30 from Ana's account to Bo's is **two** changes: subtract from Ana, add to Bo. If the computer crashes between them, money vanishes. A **transaction** groups statements so they take effect **all together or not at all**.

```text
BEGIN;
  UPDATE accounts SET balance = balance - 30 WHERE owner = 'ana';
  UPDATE accounts SET balance = balance + 30 WHERE owner = 'bo';
COMMIT;        -- both changes become permanent, atomically   (or ROLLBACK to undo both)
```

## 2. ACID

| Letter | Property | Meaning |
|--------|----------|---------|
| **A** | **Atomicity** | all statements of the transaction happen, or none do |
| **C** | **Consistency** | a transaction moves the database from one valid state to another (constraints hold) |
| **I** | **Isolation** | concurrent transactions do not see each other's unfinished work, as if they ran one at a time |
| **D** | **Durability** | once committed, data survives crashes and power loss |

## 3. Setup: a bank in a SQLite file

Two connections need a **file** (an in-memory database is private to one connection). `isolation_level=None` makes Python leave transaction control entirely to our explicit `BEGIN`/`COMMIT`; `timeout=0` makes lock conflicts fail immediately so we can watch them.

```python
import sqlite3, tempfile, os

def make_db():
    path = os.path.join(tempfile.mkdtemp(), "bank.db")
    def connect():
        c = sqlite3.connect(path, isolation_level=None, timeout=0)
        c.execute("PRAGMA foreign_keys = ON")
        return c
    setup = connect()
    setup.execute("PRAGMA journal_mode = WAL")                       # write-ahead log: readers and a writer can work together
    setup.execute("CREATE TABLE accounts (id INTEGER PRIMARY KEY, owner TEXT NOT NULL, balance INTEGER NOT NULL CHECK (balance >= 0))")
    setup.executemany("INSERT INTO accounts VALUES (?, ?, ?)", [(1, "ana", 100), (2, "bo", 50)])
    return connect, setup

connect, a = make_db()
balances = lambda c: c.execute("SELECT owner, balance FROM accounts ORDER BY id").fetchall()
print(balances(a))                                                   # [('ana', 100), ('bo', 50)]
```

## 4. Atomicity: all or nothing

A transfer where the second step breaks a rule (the `CHECK (balance >= 0)` constraint):

```python
def transfer(conn, source, target, amount, debit_extra=0):
    try:
        conn.execute("BEGIN")
        conn.execute("UPDATE accounts SET balance = balance - ? WHERE owner = ?", (amount, source))
        conn.execute("UPDATE accounts SET balance = balance - ? WHERE owner = ?", (debit_extra, target))   # a buggy second step
        conn.execute("UPDATE accounts SET balance = balance + ? WHERE owner = ?", (amount, target))
        conn.execute("COMMIT")
        return "committed"
    except sqlite3.IntegrityError as e:
        conn.execute("ROLLBACK")                                     # undo EVERYTHING since BEGIN, including the first UPDATE
        return f"rolled back: {e}"

print(transfer(a, "ana", "bo", 30, debit_extra=999))                 # rolled back: CHECK constraint failed: balance >= 0
print(balances(a))                                                   # [('ana', 100), ('bo', 50)]    unchanged: Ana's debit was undone too
print(transfer(a, "ana", "bo", 30))                                  # committed
print(balances(a))                                                   # [('ana', 70), ('bo', 80)]
```

Without the transaction, Ana's 30 would have been debited and the error would have left the money gone. **Consistency** is the constraints doing their job: the database refuses to end up in a state that breaks the rules.

In Python's default mode (`isolation_level=""`), `sqlite3` opens a transaction automatically before a write and you call `commit()`/`rollback()`; the `with conn:` block commits on success and rolls back on an exception (shown in the [first lesson](../relational-sql/01-sql-first-steps.md)).

## 5. Isolation: you cannot see my unfinished work

Two connections, Ana's session `a` and an auditor `b`:

```python
b = connect()
a.execute("BEGIN")
a.execute("UPDATE accounts SET balance = 0 WHERE owner = 'ana'")      # not committed yet
print(b.execute("SELECT balance FROM accounts WHERE owner = 'ana'").fetchone())      # (70,)   b still sees the old value: no "dirty read"
a.execute("ROLLBACK")
print(b.execute("SELECT balance FROM accounts WHERE owner = 'ana'").fetchone())      # (70,)   and the zero never existed for anyone else
```

A **dirty read** (seeing uncommitted data that later vanishes) is the first of several **anomalies** isolation prevents (section 9).

### Snapshots: a consistent view while others write

In WAL mode a reader keeps seeing the database as it was when its transaction began, even while others commit:

```python
b.execute("BEGIN")
print(b.execute("SELECT balance FROM accounts WHERE owner = 'ana'").fetchone())      # (70,)
a.execute("UPDATE accounts SET balance = balance + 5 WHERE owner = 'ana'")           # autocommitted by a
print(b.execute("SELECT balance FROM accounts WHERE owner = 'ana'").fetchone())      # (70,)   same snapshot inside b's transaction: a repeatable read
b.execute("COMMIT")
print(b.execute("SELECT balance FROM accounts WHERE owner = 'ana'").fetchone())      # (75,)   a fresh transaction sees the new value
```

This is **snapshot isolation** (also called MVCC, multi-version concurrency control, used by PostgreSQL, MySQL/InnoDB and Oracle): readers never block writers and writers never block readers, because each sees its own version of the data.

### Writers take turns

Only one connection can write at a time in SQLite. A second writer is refused (or waits, if you set a timeout):

```python
a.execute("BEGIN IMMEDIATE")                                         # a takes the write lock now
try:
    b.execute("BEGIN IMMEDIATE")
except sqlite3.OperationalError as e:
    print("b:", e)                                                   # b: database is locked
a.execute("ROLLBACK")
```

In real servers (`timeout=5`, or PostgreSQL's row locks) the second writer simply **waits** its turn.

## 6. The lost update

The most important concurrency bug in application code: **read, compute in Python, write back**. Two sessions both read 75, one subtracts 10 and the other 20, and the second write overwrites the first:

```python
def reset():
    a.execute("UPDATE accounts SET balance = 100 WHERE owner = 'ana'")

reset()
x = a.execute("SELECT balance FROM accounts WHERE owner = 'ana'").fetchone()[0]       # session a reads 100
y = b.execute("SELECT balance FROM accounts WHERE owner = 'ana'").fetchone()[0]       # session b reads 100 (no transaction around the pair)
a.execute("UPDATE accounts SET balance = ? WHERE owner = 'ana'", (x - 10,))           # a writes 90
b.execute("UPDATE accounts SET balance = ? WHERE owner = 'ana'", (y - 20,))           # b writes 80, silently erasing a's withdrawal
print(a.execute("SELECT balance FROM accounts WHERE owner = 'ana'").fetchone())       # (80,)   expected 70: ten units were LOST
```

The same bug as the thread race in the [OS lesson](../../06-operating-systems/concurrency-deadlocks/01-race-conditions-and-synchronization.md), now across processes and servers. Three fixes:

### Fix 1: let the database do the arithmetic atomically (best when possible)

```python
reset()
a.execute("UPDATE accounts SET balance = balance - 10 WHERE owner = 'ana'")
b.execute("UPDATE accounts SET balance = balance - 20 WHERE owner = 'ana'")
print(a.execute("SELECT balance FROM accounts WHERE owner = 'ana'").fetchone())       # (70,)   correct: each UPDATE reads the current value itself
```

Prefer `SET x = x - ?` over "read x, subtract in Python, write x". A single statement is atomic. Add a guard when the rule needs one: `UPDATE ... SET balance = balance - ? WHERE owner = ? AND balance >= ?` and check `cursor.rowcount == 1`.

### Fix 2: lock before reading (pessimistic locking)

Take the write lock up front so no one can interleave:

```python
reset()
a.execute("BEGIN IMMEDIATE")                                         # a becomes the only writer
try:
    b.execute("BEGIN IMMEDIATE")
except sqlite3.OperationalError:
    print("b has to wait or retry")                                  # b has to wait or retry
x = a.execute("SELECT balance FROM accounts WHERE owner = 'ana'").fetchone()[0]
a.execute("UPDATE accounts SET balance = ? WHERE owner = 'ana'", (x - 10,))
a.execute("COMMIT")
b.execute("BEGIN IMMEDIATE")                                         # now b may proceed and reads the fresh value
y = b.execute("SELECT balance FROM accounts WHERE owner = 'ana'").fetchone()[0]
b.execute("UPDATE accounts SET balance = ? WHERE owner = 'ana'", (y - 20,))
b.execute("COMMIT")
print(a.execute("SELECT balance FROM accounts WHERE owner = 'ana'").fetchone())       # (70,)
```

Other databases use `SELECT ... FOR UPDATE` to lock just the rows you read (PostgreSQL, MySQL, Oracle). Pessimistic locking is simple and safe but makes others wait, and risks **deadlocks** when two transactions lock rows in opposite orders (always lock in a consistent order).

### Fix 3: optimistic concurrency (version numbers)

Do not lock; instead remember the row's **version** and make the write conditional on it. If someone else changed it meanwhile, the update touches **zero rows** and you retry. Ideal when conflicts are rare (web forms, editing records).

```python
a.execute("ALTER TABLE accounts ADD COLUMN version INTEGER NOT NULL DEFAULT 0")
reset()

def withdraw_optimistic(conn, owner, amount, before_write=lambda: None):
    for attempt in range(1, 6):
        balance, version = conn.execute("SELECT balance, version FROM accounts WHERE owner = ?", (owner,)).fetchone()
        before_write()                                               # (a window in which another session may sneak in)
        cur = conn.execute("UPDATE accounts SET balance = ?, version = version + 1 WHERE owner = ? AND version = ?",
                           (balance - amount, owner, version))
        if cur.rowcount == 1:
            return attempt                                           # our write won: the version was still the one we read
        # rowcount 0: somebody changed the row first. Loop to re-read and try again.
    raise RuntimeError("too much contention")

interfered = {"done": False}
def sneak_in():                                                      # session b withdraws 20 right between a's read and write
    if not interfered["done"]:
        interfered["done"] = True
        b.execute("UPDATE accounts SET balance = balance - 20, version = version + 1 WHERE owner = 'ana'")

print(withdraw_optimistic(a, "ana", 10, before_write=sneak_in))      # 2   (the first attempt detected the conflict and retried)
print(a.execute("SELECT balance, version FROM accounts WHERE owner = 'ana'").fetchone())      # (70, 2)   both withdrawals applied
```

Same pattern in web APIs: send an `ETag` or `version` with the edit form and reject stale saves with **HTTP 409 Conflict** or **412 Precondition Failed** ([HTTP lesson](../../07-networking/dns-http/01-http-from-scratch.md)); ORMs offer it as "version columns".

## 7. Savepoints: partial rollback

A **savepoint** marks a point inside a transaction you can roll back to without abandoning the whole transaction:

```python
a.execute("BEGIN")
a.execute("UPDATE accounts SET balance = balance + 1 WHERE owner = 'bo'")
a.execute("SAVEPOINT risky")
a.execute("UPDATE accounts SET balance = balance + 1000 WHERE owner = 'bo'")
a.execute("ROLLBACK TO risky")                                       # undo only the 1000, keep the +1
a.execute("COMMIT")
print(a.execute("SELECT balance FROM accounts WHERE owner = 'bo'").fetchone())        # (81,)   (80 + 1)
```

Use them for "try this optional step; if it fails, carry on" inside a larger unit of work.

## 8. Durability and journaling

How can a commit survive a power cut? The database writes changes to a **log first** (the rollback journal or the **write-ahead log, WAL**) and `fsync`s it to disk **before** reporting `COMMIT`. After a crash, recovery replays committed log entries and discards unfinished ones (the same idea as the journaled file system toy in the [file systems lesson](../../06-operating-systems/file-systems-io/01-file-systems-in-depth.md)).

```python
print(a.execute("PRAGMA journal_mode").fetchone())                   # ('wal',)
print(a.execute("PRAGMA synchronous").fetchone())                    # (2,) or (1,): FULL or NORMAL fsync policy (see below)
```

| Setting | Durability | Speed |
|---------|-----------|-------|
| `synchronous=FULL` | every commit is flushed to disk | slowest, safest |
| `synchronous=NORMAL` (with WAL) | may lose the most recent commits on power loss (but not corrupt) | faster |
| `synchronous=OFF` | OS crash can corrupt | fastest, only for disposable data |

Group commit, batching many writes into one transaction, is the biggest performance lever:

```python
import time

bulk = connect()
bulk.execute("CREATE TABLE log (id INTEGER PRIMARY KEY, message TEXT)")

start = time.perf_counter()
for i in range(300):
    bulk.execute("INSERT INTO log (message) VALUES (?)", (f"row {i}",))      # autocommit: 300 separate commits, 300 fsyncs
one_by_one = time.perf_counter() - start

start = time.perf_counter()
bulk.execute("BEGIN")
for i in range(300):
    bulk.execute("INSERT INTO log (message) VALUES (?)", (f"row {i}",))
bulk.execute("COMMIT")                                                       # one commit, one fsync
batched = time.perf_counter() - start
print(batched < one_by_one)                                                  # True   (batching is typically 10 to 100 times faster)
```

## 9. Isolation levels and the anomalies they allow

Perfect isolation (**serializable**: the result equals running transactions one after another) costs performance, so databases offer weaker levels that allow some anomalies:

| Anomaly | What happens |
|---------|--------------|
| **Dirty read** | you read another transaction's *uncommitted* change that is later rolled back |
| **Non-repeatable read** | you read a row twice in one transaction and get different values (someone committed in between) |
| **Phantom read** | you run the same range query twice and new rows appear |
| **Lost update** | two read-modify-write cycles overwrite each other (section 6) |
| **Write skew** | two transactions each read overlapping data, make *different* writes that together break a rule |

| Isolation level (SQL standard) | Dirty read | Non-repeatable read | Phantom |
|--------------------------------|:---:|:---:|:---:|
| `READ UNCOMMITTED` | possible | possible | possible |
| `READ COMMITTED` (PostgreSQL, Oracle default) | no | possible | possible |
| `REPEATABLE READ` (MySQL default) | no | no | possible* |
| `SERIALIZABLE` | no | no | no |

\*Real implementations differ (PostgreSQL's `REPEATABLE READ` is snapshot isolation and prevents phantoms but still allows write skew). **SQLite** allows only one writer at a time, so writes are effectively serializable.

**Write skew example (cannot be reproduced in single-writer SQLite, but it is the classic bug in snapshot databases):** a hospital rule says at least one doctor must be on call. Alice and Bob are both on call. Each runs `SELECT COUNT(*) FROM on_call` (sees 2), decides it is safe to leave, and executes `UPDATE ... SET on_call = false WHERE doctor = <me>`. Both commit; nobody is on call. Neither wrote the other's row, so no lost update is detected. Fixes: `SERIALIZABLE` isolation (the database aborts one transaction; retry it), or lock the rows you depend on (`SELECT ... FOR UPDATE`), or enforce the rule with a constraint or trigger.

**Practical advice:** know your database's default level; use `SERIALIZABLE` (with retry logic) or explicit locks for invariants spanning several rows; keep transactions **short**; never wait for user input or call external services inside a transaction.

## 10. Deadlocks and retries

In multi-writer databases two transactions can wait for each other's row locks (the [deadlock](../../06-operating-systems/concurrency-deadlocks/02-deadlock.md) cycle). The database detects it within about a second, **aborts one transaction as the victim** with an error (`deadlock detected`) and the application must **retry the whole transaction**. Reduce them by touching rows in a consistent order and keeping transactions short.

```python
def run_with_retries(operation, attempts=5):
    for attempt in range(1, attempts + 1):
        try:
            return operation(), attempt
        except sqlite3.OperationalError:                                     # "database is locked" here; "deadlock detected" / "could not serialize" elsewhere
            if attempt == attempts:
                raise
```

(Add exponential backoff and jitter as in the [resilience lab](../../07-networking/load-balancing-cdn/01-load-balancing-and-resilience-lab.md).)

## 11. Idempotency: safe retries across a network

If a client sends "charge 50" and the connection drops before the reply, did it succeed? Retrying could charge twice. Make operations **idempotent** with a unique **idempotency key** recorded in the same transaction:

```python
a.execute("CREATE TABLE payments (idempotency_key TEXT PRIMARY KEY, owner TEXT, amount INTEGER)")

def charge(conn, key, owner, amount):
    try:
        conn.execute("BEGIN")
        conn.execute("INSERT INTO payments VALUES (?, ?, ?)", (key, owner, amount))      # fails if the key was already used
        conn.execute("UPDATE accounts SET balance = balance - ? WHERE owner = ?", (amount, owner))
        conn.execute("COMMIT")
        return "charged"
    except sqlite3.IntegrityError:
        conn.execute("ROLLBACK")
        return "duplicate request ignored"

print(charge(a, "order-1001", "ana", 20), charge(a, "order-1001", "ana", 20), charge(a, "order-1001", "ana", 20))
# charged duplicate request ignored duplicate request ignored
print(a.execute("SELECT balance FROM accounts WHERE owner = 'ana'").fetchone())      # (50,)   charged exactly once despite three attempts
```

Payment APIs (Stripe's `Idempotency-Key` header) work exactly like this.

## 12. Beyond one database

A transaction covers **one database**. Across services (an order service and a payment service), you cannot simply `COMMIT` both. Options: **two-phase commit** (2PC: coordinator asks all to prepare, then commit; blocking and fragile), or **sagas** (a sequence of local transactions with **compensating actions** to undo earlier steps if a later one fails: cancel the order, refund the payment), or the **outbox pattern** (write the event to an `outbox` table in the same local transaction as the data change, and a separate process publishes it reliably). Eventual consistency, covered in the [NoSQL lesson](../nosql/README.md), is the price of scale.

## 13. Two real-world examples

**Example 1: Ticket booking.** `UPDATE seats SET holder = ? WHERE seat = ? AND holder IS NULL` is atomic: of 1000 simultaneous buyers exactly one gets `rowcount == 1`. No explicit lock, no overselling. The same trick implements inventory counters (`stock = stock - 1 WHERE stock > 0`).

**Example 2: E-commerce checkout.** One transaction inserts the order, its items, decrements stock and records the payment. If the payment gateway fails, everything rolls back and the customer's cart is intact. The (slow, external) gateway call happens **outside** the transaction, using an idempotency key, so locks are never held while waiting for a network.

## 14. Common mistakes

- Read-modify-write in application code without a lock, atomic statement or version check (lost updates).
- Long transactions (holding locks while waiting for users, HTTP calls or slow loops).
- Forgetting to `commit` or to `rollback` on errors (a leaked open transaction blocks others and holds old snapshots).
- Assuming the default isolation level protects multi-row invariants (write skew).
- Retrying non-idempotent operations blindly.
- Autocommit loops for bulk loads (300 fsyncs instead of one).
- Catching a database error and continuing inside an aborted transaction (PostgreSQL requires a rollback first).
- Taking locks in inconsistent orders (deadlocks).

## 15. Practice

1. Name the ACID property each case relies on: (a) a power cut during commit does not corrupt the database; (b) a transfer is all-or-nothing; (c) `CHECK (balance >= 0)` rejects an overdraft; (d) two users editing at once do not see half-done edits.
2. Why is `UPDATE stock SET qty = qty - 1 WHERE id = 7 AND qty > 0` safer than "SELECT qty; if qty > 0: UPDATE stock SET qty = ?"?
3. What does `cursor.rowcount == 0` signal in optimistic locking?
4. List two ways to avoid write skew.
5. Why should you not call a payment API inside an open transaction?
6. Rewrite `withdraw_optimistic` to raise `ValueError("insufficient funds")` instead of letting the balance go negative.
7. What is the difference between `ROLLBACK` and `ROLLBACK TO savepoint`?

<details>
<summary>Solutions</summary>

1. (a) Durability, (b) Atomicity, (c) Consistency, (d) Isolation.
2. The single statement checks and decrements atomically inside the database; the read-then-write version has a gap in which another session can take the last unit, overselling.
3. Another session changed the row (its version differs from the one you read), so your conditional update matched nothing; re-read and retry.
4. Use `SERIALIZABLE` isolation and retry on serialization failures, or lock the rows the decision depends on (`SELECT ... FOR UPDATE`), or express the rule as a constraint/trigger enforced by the database.
5. The call can be slow or hang; the transaction would hold locks (and an old snapshot) for that whole time, blocking others. Call it outside the transaction using an idempotency key.
6. ```python
   def withdraw_checked(conn, owner, amount):
       for _ in range(5):
           balance, version = conn.execute("SELECT balance, version FROM accounts WHERE owner = ?", (owner,)).fetchone()
           if balance < amount:
               raise ValueError("insufficient funds")
           cur = conn.execute("UPDATE accounts SET balance = ?, version = version + 1 WHERE owner = ? AND version = ?",
                              (balance - amount, owner, version))
           if cur.rowcount == 1:
               return balance - amount
       raise RuntimeError("too much contention")
   print(withdraw_checked(a, "ana", 5))                              # 45
   try:
       withdraw_checked(a, "ana", 10_000)
   except ValueError as e:
       print(e)                                                      # insufficient funds
   ```
7. `ROLLBACK` abandons the entire transaction; `ROLLBACK TO savepoint` undoes only the work after that savepoint and the transaction stays open.

</details>

## 16. Check yourself

1. What does each letter of ACID guarantee?
2. How does MVCC let readers and writers avoid blocking each other?
3. How does a lost update happen and what are three fixes?
4. What is the difference between pessimistic and optimistic concurrency control?
5. Why is batching writes into one transaction much faster?
6. What is an idempotency key for?
7. Why must you retry a transaction chosen as a deadlock victim?

<details>
<summary>Answers</summary>

1. Atomicity: all or nothing. Consistency: constraints always hold at commit. Isolation: concurrent transactions do not interfere or see unfinished work. Durability: committed data survives crashes.
2. Each transaction reads its own consistent snapshot (older row versions are kept), so readers do not need locks that block writers.
3. Two sessions read the same value and write back results computed from it, so one write overwrites the other. Fixes: an atomic `UPDATE x = x - n`, locking (`BEGIN IMMEDIATE` / `SELECT FOR UPDATE`), optimistic version checks.
4. Pessimistic locks first and makes others wait; optimistic proceeds without locks and detects conflicts at write time (retry on conflict).
5. A commit forces the log to disk (`fsync`); one commit for many rows replaces many expensive flushes.
6. To make a retried request take effect exactly once, by recording a unique key and rejecting duplicates.
7. The database aborted it to break the deadlock cycle, so none of its changes happened; running the whole transaction again usually succeeds.

</details>

[Back to transactions and ACID](README.md)
