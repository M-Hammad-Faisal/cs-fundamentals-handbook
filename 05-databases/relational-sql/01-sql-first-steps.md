# SQL First Steps (with Python and SQLite)

**Prerequisites:** [Python basics](../../00-foundations/python-fundamentals/README.md), the idea of a table (rows and columns, like a spreadsheet). **You will learn:** what a **relational database** and **SQL** are, how to **create tables**, **insert, query, update and delete** rows, filter and sort results, handle **`NULL`**, protect data with **constraints**, and use SQLite safely from Python (**parameters**, **commits**, **row access**). Every example runs as written using only Python's built-in `sqlite3`.

## 1. In plain words

A **database** is an organized, durable store of data that many programs can query at once. A **relational database** keeps data in **tables** (like spreadsheet sheets): each **row** is one record, each **column** has a name and a type. **SQL** (Structured Query Language) is the language you use to ask for exactly the data you want. You say **what** you want ("students older than 20, sorted by name"), not **how** to loop through it; the database engine decides how.

**SQLite** is a complete SQL database stored in a single file (or in memory). It is built into Python, needs no server, and is used in phones, browsers and countless apps. The SQL you learn here carries over to PostgreSQL, MySQL, SQL Server and Oracle with small dialect differences.

## 2. Connect and create a table

```python
import sqlite3

db = sqlite3.connect(":memory:")                 # a temporary database in RAM; use "school.db" for a file
db.execute("PRAGMA foreign_keys = ON")           # SQLite only enforces foreign keys if you ask

db.execute("""
CREATE TABLE students (
    id      INTEGER PRIMARY KEY,                 -- unique id for each row (auto-assigned if omitted)
    name    TEXT    NOT NULL,                    -- must have a value
    age     INTEGER CHECK (age >= 0),            -- a rule: no negative ages
    grade   REAL,                                -- may be NULL (unknown)
    city    TEXT    DEFAULT 'Lahore'             -- used when no value is given
)
""")
print(db.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall())      # [('students',)]
```

Common column types (SQLite is flexible; other databases are stricter): `INTEGER`, `REAL` (decimals as floats), `TEXT`, `BLOB` (binary), and in other systems `VARCHAR(n)`, `DECIMAL(p, s)` (exact money), `DATE`, `TIMESTAMP`, `BOOLEAN`. Use `DECIMAL`/integers of cents for **money**, never floats.

## 3. Insert rows

```python
db.execute("INSERT INTO students (name, age, grade, city) VALUES ('Ana', 20, 88.5, 'Lahore')")

# Many rows at once, safely, with placeholders (?) instead of gluing strings together:
db.executemany(
    "INSERT INTO students (name, age, grade, city) VALUES (?, ?, ?, ?)",
    [("Bilal", 22, 71.0, "Karachi"),
     ("Chen", 19, 93.0, "Lahore"),
     ("Dina", 21, None, "Islamabad"),            # None becomes SQL NULL: grade unknown
     ("Eman", 20, 66.5, "Karachi"),
     ("Farid", 23, 79.0, "Lahore")],
)
db.execute("INSERT INTO students (name, age) VALUES ('Gul', 18)")      # grade is NULL, city takes the DEFAULT
db.commit()                                      # make the changes permanent
print(db.execute("SELECT COUNT(*) FROM students").fetchone())          # (7,)
```

**Always use `?` placeholders** for values that come from outside (users, files, other systems). They keep data separate from SQL code, which is the defense against **SQL injection** (see [security](../../07-networking/tls-security/01-cryptography-and-tls-lab.md)).

## 4. Read rows: SELECT

```python
for row in db.execute("SELECT * FROM students"):
    print(row)
# (1, 'Ana', 20, 88.5, 'Lahore')
# (2, 'Bilal', 22, 71.0, 'Karachi')
# (3, 'Chen', 19, 93.0, 'Lahore')
# (4, 'Dina', 21, None, 'Islamabad')
# (5, 'Eman', 20, 66.5, 'Karachi')
# (6, 'Farid', 23, 79.0, 'Lahore')
# (7, 'Gul', 18, None, 'Lahore')
```

The shape of a query:

```sql
SELECT   columns or expressions        -- what to return
FROM     table                         -- where from
WHERE    condition                     -- which rows
ORDER BY column [DESC]                 -- sort
LIMIT    n OFFSET m;                   -- how many
```

### Choosing columns and computing new ones

```python
print(db.execute("SELECT name, age FROM students WHERE id <= 3").fetchall())
# [('Ana', 20), ('Bilal', 22), ('Chen', 19)]

print(db.execute("SELECT name, age * 12 AS age_in_months, UPPER(city) AS city_caps FROM students LIMIT 2").fetchall())
# [('Ana', 240, 'LAHORE'), ('Bilal', 264, 'KARACHI')]
```

`AS` gives a column an **alias**. Avoid `SELECT *` in real code: name the columns you need (less data, and your code survives schema changes).

### Filtering with WHERE

| Operator | Meaning | Example |
|----------|---------|---------|
| `=`, `<>` (or `!=`), `<`, `<=`, `>`, `>=` | comparison | `age >= 21` |
| `AND`, `OR`, `NOT` | combine conditions | `age > 19 AND city = 'Lahore'` |
| `BETWEEN a AND b` | inclusive range | `grade BETWEEN 70 AND 90` |
| `IN (...)` | one of a list | `city IN ('Lahore', 'Karachi')` |
| `LIKE` | pattern: `%` any text, `_` one character | `name LIKE 'A%'` |
| `IS NULL`, `IS NOT NULL` | test for missing values | `grade IS NULL` |

```python
def q(sql, *params):
    return db.execute(sql, params).fetchall()

print(q("SELECT name FROM students WHERE age >= 21"))                          # [('Bilal',), ('Dina',), ('Farid',)]
print(q("SELECT name FROM students WHERE age > 19 AND city = 'Lahore'"))       # [('Ana',), ('Farid',)]
print(q("SELECT name FROM students WHERE grade BETWEEN 70 AND 90"))            # [('Ana',), ('Bilal',), ('Farid',)]
print(q("SELECT name FROM students WHERE city IN ('Karachi', 'Islamabad')"))   # [('Bilal',), ('Dina',), ('Eman',)]
print(q("SELECT name FROM students WHERE name LIKE '%a%'"))                    # [('Ana',), ('Bilal',), ('Dina',), ('Eman',), ('Farid',)]   (LIKE ignores case in SQLite)
print(q("SELECT name FROM students WHERE name LIKE ?", "_a%"))                 # [('Farid',)]    (a second letter 'a')
```

Operator precedence: `AND` binds tighter than `OR`. Use parentheses: `WHERE (a OR b) AND c`.

### Sorting and limiting

```python
print(q("SELECT name, age FROM students ORDER BY age DESC, name ASC LIMIT 3"))
# [('Farid', 23), ('Bilal', 22), ('Dina', 21)]
print(q("SELECT name FROM students ORDER BY name LIMIT 3 OFFSET 3"))           # page 2 of size 3
# [('Dina',), ('Eman',), ('Farid',)]
print(q("SELECT DISTINCT city FROM students ORDER BY city"))
# [('Islamabad',), ('Karachi',), ('Lahore',)]
```

Without `ORDER BY`, the order of rows is **not guaranteed**: never rely on it. For big tables, `OFFSET` paging gets slower as the offset grows; prefer "keyset" paging (`WHERE id > last_seen_id ORDER BY id LIMIT n`).

## 5. NULL: "unknown", not zero

`NULL` means **missing/unknown**. It behaves in surprising ways because comparisons with an unknown value are themselves unknown:

```python
print(q("SELECT NULL = NULL, NULL <> 1, NULL IS NULL, 1 + NULL"))             # [(None, None, 1, None)]
print(q("SELECT name FROM students WHERE grade = NULL"))                       # []                        never matches!
print(q("SELECT name FROM students WHERE grade IS NULL"))                      # [('Dina',), ('Gul',)]
print(q("SELECT name FROM students WHERE grade < 80"))                         # [('Bilal',), ('Eman',), ('Farid',)]   (NULL grades are in neither < 80 nor >= 80)
print(q("SELECT name, COALESCE(grade, 0) FROM students WHERE id IN (4, 5)"))   # [('Dina', 0), ('Eman', 66.5)]       COALESCE gives a default for NULL
```

SQL uses **three-valued logic**: `TRUE`, `FALSE`, `UNKNOWN`. `WHERE` keeps a row only when the condition is `TRUE`. Rules to remember: use **`IS NULL`**, never `= NULL`; arithmetic with NULL gives NULL; aggregate functions such as `AVG` **ignore** NULLs (see the next lesson); `COALESCE(x, default)` replaces NULL.

## 6. Change and remove data

```python
db.execute("UPDATE students SET grade = 75.0 WHERE name = 'Dina'")           # always include WHERE!
db.execute("UPDATE students SET age = age + 1 WHERE city = 'Karachi'")
db.execute("DELETE FROM students WHERE name = 'Gul'")
db.commit()
print(q("SELECT name, age, grade FROM students WHERE name IN ('Dina', 'Bilal', 'Eman')"))
# [('Bilal', 23, 71.0), ('Dina', 21, 75.0), ('Eman', 21, 66.5)]
print(q("SELECT COUNT(*) FROM students"))                                      # [(6,)]
```

**`UPDATE` or `DELETE` without `WHERE` changes every row.** Habit: write the `WHERE`, run it first as a `SELECT` to see which rows match, then convert. Use a **transaction** so you can undo ([transactions lab](../transactions-acid/01-transactions-lab.md)). Production data is often **soft-deleted** (`deleted_at` column) instead of removed.

`cursor.rowcount` tells you how many rows a statement changed:

```python
cur = db.execute("UPDATE students SET city = 'Multan' WHERE name = 'nobody'")
print(cur.rowcount)                                                            # 0
```

## 7. Constraints: the database defends your data

Constraints are rules the database enforces **no matter which program writes the data**.

| Constraint | Rule |
|------------|------|
| `PRIMARY KEY` | unique, not null identifier |
| `NOT NULL` | a value is required |
| `UNIQUE` | no duplicates |
| `CHECK (...)` | custom rule |
| `DEFAULT x` | value when omitted |
| `FOREIGN KEY ... REFERENCES` | the value must exist in another table |

```python
def attempt(sql, *params):
    try:
        db.execute(sql, params)
        return "ok"
    except sqlite3.IntegrityError as e:
        return f"rejected: {e}"

print(attempt("INSERT INTO students (name, age) VALUES (NULL, 20)"))           # rejected: NOT NULL constraint failed: students.name
print(attempt("INSERT INTO students (name, age) VALUES ('Hira', -5)"))         # rejected: CHECK constraint failed: age >= 0
print(attempt("INSERT INTO students (id, name) VALUES (1, 'Duplicate')"))      # rejected: UNIQUE constraint failed: students.id
db.rollback()
```

Foreign keys connect tables:

```python
db.execute("CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT NOT NULL UNIQUE)")
db.execute("""CREATE TABLE enrollments (
    student_id INTEGER NOT NULL REFERENCES students(id),
    course_id  INTEGER NOT NULL REFERENCES courses(id),
    score      REAL,
    PRIMARY KEY (student_id, course_id)              -- a student takes each course at most once
)""")
db.executemany("INSERT INTO courses VALUES (?, ?)", [(1, "Algorithms"), (2, "Databases")])
print(attempt("INSERT INTO enrollments VALUES (1, 1, 90.0)"))                  # ok
print(attempt("INSERT INTO enrollments VALUES (999, 1, 50.0)"))                # rejected: FOREIGN KEY constraint failed   (no student 999)
print(attempt("INSERT INTO enrollments VALUES (1, 1, 95.0)"))                  # rejected: UNIQUE constraint failed: enrollments.student_id, enrollments.course_id
print(attempt("DELETE FROM students WHERE id = 1"))                            # rejected: FOREIGN KEY constraint failed   (Ana is still enrolled)
db.commit()
```

(Joins across these tables are in the [next lesson](02-aggregation-and-joins-lab.md).)

## 8. Using SQLite well from Python

```python
db.row_factory = sqlite3.Row                                          # rows behave like dicts: access by column name
row = db.execute("SELECT id, name, grade FROM students WHERE name = ?", ("Chen",)).fetchone()
print(row["name"], row["grade"], row.keys())                          # Chen 93.0 ['id', 'name', 'grade']
print(dict(row))                                                      # {'id': 3, 'name': 'Chen', 'grade': 93.0}

# fetch methods: fetchone() (one row or None), fetchmany(n), fetchall() (a list), or iterate the cursor directly (memory friendly)
print(db.execute("SELECT * FROM students WHERE id = 999").fetchone())  # None
db.row_factory = None                                                 # back to plain tuples for the rest of this lesson

# the connection as a context manager commits on success and rolls back on an exception
try:
    with db:
        db.execute("INSERT INTO students (name, age) VALUES ('Ignored', 30)")
        raise RuntimeError("something went wrong before the commit")
except RuntimeError:
    pass
print(db.execute("SELECT COUNT(*) FROM students WHERE name = 'Ignored'").fetchone()[0])      # 0   (the insert was rolled back)
```

Habits: parameterize everything, `commit()` after writes (or use `with db:`), close connections (`db.close()`), enable `PRAGMA foreign_keys = ON` per connection, and store dates as ISO text (`'2026-11-07'`) so they sort correctly.

```python
import datetime
db.execute("CREATE TABLE events (id INTEGER PRIMARY KEY, happened_on TEXT NOT NULL)")
db.executemany("INSERT INTO events (happened_on) VALUES (?)", [(d.isoformat(),) for d in (datetime.date(2026, 3, 9), datetime.date(2025, 12, 31), datetime.date(2026, 1, 15))])
print([r[0] for r in db.execute("SELECT happened_on FROM events ORDER BY happened_on")])      # ['2025-12-31', '2026-01-15', '2026-03-09']
print(db.execute("SELECT strftime('%Y', happened_on) AS year, COUNT(*) FROM events GROUP BY year ORDER BY year").fetchall())      # [('2025', 1), ('2026', 2)]
```

## 9. How a query is evaluated (the mental model)

SQL is written `SELECT ... FROM ... WHERE ... ORDER BY ...` but evaluated in a different order:

```text
1. FROM       which table(s), and joins
2. WHERE      filter individual rows
3. GROUP BY   form groups            (next lesson)
4. HAVING     filter groups          (next lesson)
5. SELECT     compute the output columns and aliases
6. DISTINCT   remove duplicates
7. ORDER BY   sort (can use SELECT aliases)
8. LIMIT      keep the first n rows
```

That is why, in standard SQL, a `WHERE` clause cannot use a column alias defined in `SELECT` (it has not been computed yet), while `ORDER BY` can:

```python
print(q("SELECT name, age * 12 AS months FROM students ORDER BY months DESC LIMIT 2"))     # [('Bilal', 276), ('Farid', 276)]
```

Some databases are lenient: SQLite and MySQL accept `WHERE months > 250` with the alias, but PostgreSQL, SQL Server and Oracle reject it. For portable SQL repeat the expression, or wrap the query in a subquery or CTE:

```python
print(q("SELECT name FROM students WHERE age * 12 > 250 ORDER BY name"))                  # [('Bilal',), ('Dina',), ('Eman',), ('Farid',)]
print(q("SELECT name FROM (SELECT name, age * 12 AS months FROM students) WHERE months > 250 ORDER BY name"))      # same result, portable
```

## 10. Two real-world examples

**Example 1: An app's settings and users.** A mobile app keeps users, preferences and cached content in a local SQLite file; `UPDATE users SET last_login = ? WHERE id = ?` runs on every sign-in, and constraints (`UNIQUE(email)`) stop duplicate accounts even if two code paths race.

**Example 2: Reporting from a spreadsheet.** An analyst loads a CSV of sales into SQLite (`INSERT` via `executemany`) and answers questions with SQL instead of formulas: filter, sort and aggregate millions of rows in milliseconds, then repeat the query next month on fresh data.

## 11. Common mistakes

- Gluing user input into SQL strings (injection) instead of using `?` placeholders.
- `UPDATE`/`DELETE` without `WHERE`.
- Using `= NULL` instead of `IS NULL`.
- Assuming row order without `ORDER BY`.
- Forgetting `commit()` (changes vanish when the connection closes).
- Storing money in floating point, or dates as free-form text.
- `SELECT *` everywhere.
- Forgetting `PRAGMA foreign_keys = ON` in SQLite (constraints silently not enforced).

## 12. Practice

(Use the `students` table above; assume `Gul` was deleted and Dina's grade is 75.0.)

1. List the names and cities of students aged 21 or older, sorted by name.
2. Find students whose name starts with a vowel (A, E, I, O, U).
3. List the three students with the highest grades (ignore NULLs).
4. Add a student `Hira`, age 24, in `Quetta`, grade 82.5, and verify the count.
5. Raise everyone's grade by 2 points who is in Lahore. Why should you test with `SELECT` first?
6. What does `SELECT name FROM students WHERE grade <> 70` return for students with a NULL grade?
7. Write a query to find students **with no grade recorded**.
8. Try to insert a student with age 200 after adding `CHECK (age < 150)`. (Describe how: SQLite cannot add a CHECK to an existing table, so you recreate the table.)

<details>
<summary>Solutions</summary>

1. ```python
   print(q("SELECT name, city FROM students WHERE age >= 21 ORDER BY name"))
   # [('Bilal', 'Karachi'), ('Dina', 'Islamabad'), ('Eman', 'Karachi'), ('Farid', 'Lahore')]
   ```
2. ```python
   print(q("SELECT name FROM students WHERE name LIKE 'A%' OR name LIKE 'E%' OR name LIKE 'I%' OR name LIKE 'O%' OR name LIKE 'U%'"))
   # [('Ana',), ('Eman',)]
   ```
3. ```python
   print(q("SELECT name, grade FROM students WHERE grade IS NOT NULL ORDER BY grade DESC LIMIT 3"))
   # [('Chen', 93.0), ('Ana', 88.5), ('Farid', 79.0)]
   ```
4. ```python
   db.execute("INSERT INTO students (name, age, grade, city) VALUES (?, ?, ?, ?)", ("Hira", 24, 82.5, "Quetta"))
   print(q("SELECT COUNT(*) FROM students"))                      # [(7,)]
   ```
5. ```python
   print(q("SELECT name, grade FROM students WHERE city = 'Lahore'"))      # preview the rows first
   db.execute("UPDATE students SET grade = grade + 2 WHERE city = 'Lahore'")
   ```
   Testing with `SELECT` shows exactly which rows will change, so a wrong `WHERE` is caught before it damages data. (A NULL grade stays NULL: `NULL + 2` is NULL.)
6. Nothing for NULL rows: `NULL <> 70` is unknown, so they are excluded. Use `grade <> 70 OR grade IS NULL` to include them.
7. ```python
   print(q("SELECT name FROM students WHERE grade IS NULL"))      # [] (Dina now has 75.0 and Gul was removed)
   ```
8. Create `students_new` with the extra `CHECK`, copy the rows with `INSERT INTO students_new SELECT ...`, drop the old table and rename the new one (a standard "migration" pattern). Then an insert with age 200 raises `IntegrityError: CHECK constraint failed`.

</details>

## 13. Check yourself

1. What does the database decide, and what do you decide, when you write SQL?
2. Why use `?` placeholders instead of f-strings?
3. Why does `WHERE grade = NULL` return nothing?
4. What is the logical evaluation order of `SELECT ... FROM ... WHERE ... ORDER BY ... LIMIT`?
5. What does a `FOREIGN KEY` protect?
6. When are your changes permanent in Python's `sqlite3`?

<details>
<summary>Answers</summary>

1. You say *what* rows and columns you want; the engine chooses *how* (which indexes, what order of operations).
2. Placeholders keep values separate from the SQL text, so input cannot change the query's meaning (SQL injection defense) and values are quoted correctly.
3. Any comparison with `NULL` is unknown, not true; use `IS NULL`.
4. FROM, WHERE, (GROUP BY, HAVING), SELECT, DISTINCT, ORDER BY, LIMIT.
5. It ensures a value in one table refers to an existing row in another (no orphan references).
6. After `commit()` (or leaving a `with db:` block without an exception).

</details>

[Back to relational model and SQL](README.md) · Next: [aggregation and joins lab](02-aggregation-and-joins-lab.md)
