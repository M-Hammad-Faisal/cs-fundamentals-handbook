"""Index demo: see the effect of indexes on query plans and speed.

Run:  python3 demo_indexes.py
Uses only the standard library (sqlite3). Timings vary by machine; the *plans*
and the rough ratio between scan and index lookup are what matter.
"""
import random
import sqlite3
import time

ROWS = 200_000

conn = sqlite3.connect(":memory:")
conn.executescript(
    "CREATE TABLE users ("
    " id INTEGER PRIMARY KEY, email TEXT, country TEXT, age INTEGER, created_on TEXT);"
)
random.seed(1)
conn.executemany(
    "INSERT INTO users VALUES (?, ?, ?, ?, ?)",
    (
        (
            i,
            f"user{i}@example.com",
            random.choice(["PK", "US", "UK", "DE", "IN"]),
            random.randint(18, 80),
            f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
        )
        for i in range(1, ROWS + 1)
    ),
)


def plan(sql):
    return [row[3] for row in conn.execute("EXPLAIN QUERY PLAN " + sql)]


def timed(sql, repeat=20):
    start = time.perf_counter()
    for _ in range(repeat):
        conn.execute(sql).fetchall()
    return (time.perf_counter() - start) / repeat * 1000  # milliseconds


def show(label, sql):
    print(f"{label}\n  SQL : {sql}\n  PLAN: {plan(sql)}\n  TIME: {timed(sql):.3f} ms\n")


lookup = "SELECT * FROM users WHERE email = 'user150000@example.com'"
show("1. Lookup WITHOUT an index (full table scan)", lookup)

conn.execute("CREATE INDEX idx_users_email ON users(email)")
show("2. Same lookup WITH an index on email", lookup)

multi = "SELECT * FROM users WHERE country = 'PK' AND age > 70"
conn.execute("CREATE INDEX idx_country_age ON users(country, age)")
show("3. Composite index (country, age) serves both conditions", multi)

show(
    "4. Leftmost-prefix rule: a filter on age alone cannot use (country, age)",
    "SELECT * FROM users WHERE age > 70",
)

show(
    "5. Covering index: the index holds every selected column",
    "SELECT country, age FROM users WHERE country = 'PK' AND age > 70",
)

show(
    "6. A function on the column defeats the index",
    "SELECT * FROM users WHERE lower(email) = 'user5@example.com'",
)

show(
    "7. A leading wildcard defeats the index",
    "SELECT * FROM users WHERE email LIKE '%5@example.com'",
)

order = "SELECT * FROM users ORDER BY created_on LIMIT 5"
show("8. ORDER BY without an index needs a sort", order)
conn.execute("CREATE INDEX idx_created ON users(created_on)")
show("9. ORDER BY with an index reads rows already in order", order)
