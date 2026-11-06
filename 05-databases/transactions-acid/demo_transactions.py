"""Transaction demos with SQLite (standard library only).

Run:  python3 demo_transactions.py

Shows: (1) atomicity and rollback, (2) a lost update caused by read-modify-write
in application code, and how an atomic UPDATE or a locking transaction fixes it,
(3) a constraint stopping bad data, (4) snapshot behaviour between two connections.
"""
import os
import sqlite3
import tempfile

path = os.path.join(tempfile.mkdtemp(), "bank.db")


def connect():
    # isolation_level=None -> we control BEGIN/COMMIT explicitly
    conn = sqlite3.connect(path, isolation_level=None, timeout=1)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def balances(conn):
    return dict(conn.execute("SELECT name, balance FROM accounts ORDER BY name"))


def reset(conn):
    conn.executescript(
        """
        DROP TABLE IF EXISTS accounts;
        CREATE TABLE accounts (
            name    TEXT PRIMARY KEY,
            balance INTEGER NOT NULL CHECK (balance >= 0)
        );
        INSERT INTO accounts VALUES ('alice', 100), ('bob', 50);
        """
    )


db = connect()
reset(db)

print("1. ATOMICITY: transfer 150 from alice (has 100). The CHECK fails, so nothing changes.")
try:
    db.execute("BEGIN")
    db.execute("UPDATE accounts SET balance = balance + 150 WHERE name = 'bob'")    # step 1 succeeds
    db.execute("UPDATE accounts SET balance = balance - 150 WHERE name = 'alice'")  # step 2 violates CHECK
    db.execute("COMMIT")
except sqlite3.IntegrityError as exc:
    db.execute("ROLLBACK")
    print("   error:", exc)
print("   balances after rollback:", balances(db), "(bob did NOT keep the +150)\n")

print("2. A successful transfer of 30 inside one transaction:")
db.execute("BEGIN")
db.execute("UPDATE accounts SET balance = balance - 30 WHERE name = 'alice'")
db.execute("UPDATE accounts SET balance = balance + 30 WHERE name = 'bob'")
db.execute("COMMIT")
print("  ", balances(db), "\n")

reset(db)
print("3. LOST UPDATE: two clients each add 10 to alice using read-then-write in app code.")
a, b = connect(), connect()
read_a = a.execute("SELECT balance FROM accounts WHERE name='alice'").fetchone()[0]  # A reads 100
read_b = b.execute("SELECT balance FROM accounts WHERE name='alice'").fetchone()[0]  # B reads 100
a.execute("UPDATE accounts SET balance = ? WHERE name='alice'", (read_a + 10,))      # A writes 110
b.execute("UPDATE accounts SET balance = ? WHERE name='alice'", (read_b + 10,))      # B writes 110 (A's +10 lost)
print("   expected 120, got:", balances(db)["alice"], "<- one update was lost\n")

reset(db)
print("4. FIX A: let the database do the arithmetic atomically.")
a.execute("UPDATE accounts SET balance = balance + 10 WHERE name='alice'")
b.execute("UPDATE accounts SET balance = balance + 10 WHERE name='alice'")
print("   expected 120, got:", balances(db)["alice"], "\n")

reset(db)
print("5. FIX B: take the write lock before reading (BEGIN IMMEDIATE), so the second writer waits.")
a.execute("BEGIN IMMEDIATE")
try:
    b.execute("BEGIN IMMEDIATE")  # blocked while A holds the write lock
except sqlite3.OperationalError as exc:
    print("   B could not start a write transaction yet:", exc)
value = a.execute("SELECT balance FROM accounts WHERE name='alice'").fetchone()[0]
a.execute("UPDATE accounts SET balance = ? WHERE name='alice'", (value + 10,))
a.execute("COMMIT")
b.execute("BEGIN IMMEDIATE")      # now succeeds, and reads A's committed value
value = b.execute("SELECT balance FROM accounts WHERE name='alice'").fetchone()[0]
b.execute("UPDATE accounts SET balance = ? WHERE name='alice'", (value + 10,))
b.execute("COMMIT")
print("   expected 120, got:", balances(db)["alice"], "\n")

reset(db)
print("6. ISOLATION: a reader does not see uncommitted changes from another connection.")
writer, reader = connect(), connect()
writer.execute("BEGIN")
writer.execute("UPDATE accounts SET balance = 999 WHERE name = 'alice'")
print("   reader sees (writer not committed):", balances(reader)["alice"])
writer.execute("COMMIT")
print("   reader sees (after commit):        ", balances(reader)["alice"])
