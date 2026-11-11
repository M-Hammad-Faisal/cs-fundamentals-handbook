# Transactions, ACID and Isolation: One-Page Summary

## Key facts

### Transaction

A group of operations that is **all-or-nothing**: `BEGIN … COMMIT` (or `ROLLBACK`). Use `with conn:` in Python so success commits and an exception rolls back.

### ACID

| | Meaning | Mechanism |
|---|---------|-----------|
| **A**tomicity | All or nothing | Undo log |
| **C**onsistency | Valid state → valid state | Constraints |
| **I**solation | Concurrent transactions don't interfere | Locks / MVCC |
| **D**urability | Committed data survives crashes | Write-ahead log |

### Anomalies

Dirty read · non-repeatable read · phantom read · **lost update** · **write skew**.

### Isolation levels (anomalies prevented)

| Level | Dirty | Non-repeatable | Phantom |
|-------|:-----:|:--------------:|:-------:|
| Read uncommitted | no | no | no |
| Read committed | yes | no | no |
| Repeatable read | yes | yes | engine-dependent |
| Serializable | yes | yes | yes |

Defaults: PostgreSQL / Oracle / SQL Server = read committed; MySQL InnoDB = repeatable read; SQLite = effectively serializable.

### Concurrency control

- **Locks** (shared/exclusive, 2PL) vs **MVCC** (versions + snapshots; readers don't block writers).
- **Pessimistic** (`SELECT … FOR UPDATE`) vs **optimistic** (version column, retry on conflict).

### Deadlocks

Cyclic waiting; the DB aborts a victim. Prevent with consistent lock order and short transactions; always **retry**.

### Distributed

2PC (strong, blocking) · **saga** (compensating actions, eventual consistency) · outbox pattern · idempotency keys.

### Rules of thumb

- Do arithmetic in SQL (`qty = qty - 1 WHERE qty > 0`), then check `rowcount`.
- Keep transactions short; no network or user waits inside.
- Constraints are the last line of defence.
- Retry serialization failures and deadlocks with idempotent code.

## Pitfalls

- Assuming the default isolation level prevents everything: read committed still allows non-repeatable reads, lost updates and write skew.
- Long transactions, or waiting for a user inside one: locks are held the whole time.
- Read-modify-write in application code without an atomic `UPDATE`, `FOR UPDATE` or a version column.
- Not retrying deadlocks and serialisation failures.
- Trying a distributed transaction across services instead of a saga and an outbox.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Transactions Lab](01-transactions-lab.md)
