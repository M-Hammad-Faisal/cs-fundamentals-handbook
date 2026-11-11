# Database Access from Python: sqlite3, SQLAlchemy ORM and the N+1 Problem

**Prerequisites:** [relational SQL](../../05-databases/relational-sql/README.md), [transactions and ACID](../../05-databases/transactions-acid/README.md), [type hints](../typing-hints/README.md), [OOP: composition and design](../../04-oop/composition-design/README.md), [building a web API](../backend-with-fastapi/01-building-a-web-api-with-fastapi.md). **You will learn:** how Python talks to a database (the **DB-API** and `sqlite3`), how **SQLAlchemy 2.0** maps tables to classes (the **ORM**), how to query with `select()`, model **relationships**, use **sessions and transactions** correctly, spot and fix the **N+1 query problem** by counting queries, structure data access with a **repository**, and plug a session into **FastAPI**. SQLAlchemy is a third-party package (`pip install sqlalchemy`); all examples run on in-memory SQLite and the outputs shown are real.

## 1. In plain words

A database speaks SQL; your program has objects. Something has to translate between them:

- **Raw driver (DB-API):** you write SQL strings and get back tuples. Total control, lots of repetitive code.
- **Query builder / Core:** you build SQL from Python expressions; results are rows.
- **ORM (object-relational mapper):** you work with **classes and objects**; the library generates SQL and tracks changes (**unit of work**).

An ORM saves boilerplate and prevents injection by always parameterizing, but it can hide expensive queries. The skill is knowing what SQL your Python produces.

## 2. The DB-API in one minute (`sqlite3`)

Every Python database driver (`sqlite3`, `psycopg`, `mysqlclient`) follows the same pattern: **connect, get a cursor, execute with parameters, fetch, commit.**

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT NOT NULL, year INTEGER)")
conn.executemany("INSERT INTO books (title, year) VALUES (?, ?)", [("Dune", 1965), ("Emma", 1815), ("Ulysses", 1922)])
conn.commit()                                              # nothing is permanent until commit

for row in conn.execute("SELECT title, year FROM books WHERE year > ? ORDER BY year", (1900,)):   # ? placeholders: never f-strings
    print(row)
# ('Ulysses', 1922)
# ('Dune', 1965)

conn.row_factory = sqlite3.Row                             # rows that also behave like dicts
print(dict(conn.execute("SELECT * FROM books WHERE id = 1").fetchone()))
# {'id': 1, 'title': 'Dune', 'year': 1965}
conn.close()
```

Always pass values as **parameters** (`?`), never by formatting SQL text: that is the defence against [SQL injection](../../10-security/web-vulnerabilities/01-owasp-top-ten-in-python.md).

## 3. SQLAlchemy 2.0: models, engine and session

Three objects to know:

- **Engine:** the connection pool and database dialect (created once per application).
- **Declarative models:** classes that describe tables, using type annotations (`Mapped[...]`).
- **Session:** a "unit of work": it tracks the objects you load and change, and writes them in a transaction on `commit()`.

```python
from sqlalchemy import ForeignKey, String, create_engine, select, func
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

class Base(DeclarativeBase):
    pass

class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    books: Mapped[list["Book"]] = relationship(back_populates="author", cascade="all, delete-orphan")

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    year: Mapped[int | None]
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped[Author] = relationship(back_populates="books")

engine = create_engine(
    "sqlite://",                                           # in production: "postgresql+psycopg://user:pw@host/db" (from an env var)
    connect_args={"check_same_thread": False},             # an in-memory SQLite database lives in ONE connection; these two lines
    poolclass=StaticPool,                                  # let every thread (such as a web server's) share that same connection
)
Base.metadata.create_all(engine)                           # create the tables (use migrations in real projects, see below)

with Session(engine) as session:
    herbert = Author(name="Frank Herbert", books=[Book(title="Dune", year=1965), Book(title="Dune Messiah", year=1969)])
    austen = Author(name="Jane Austen", books=[Book(title="Emma", year=1815)])
    orwell = Author(name="George Orwell", books=[Book(title="1984", year=1949)])
    session.add_all([herbert, austen, orwell])
    session.commit()                                       # one transaction: all rows or none

with Session(engine) as session:
    print(session.scalar(select(func.count()).select_from(Book)), "books")
# 4 books
```

The `with Session(engine) as session:` block closes the session (returning the connection to the pool) when done. Typical web-app rule: **one session per request**, committed or rolled back at the end.

## 4. Querying with `select()`

```python
with Session(engine) as session:
    old_books = session.scalars(select(Book).where(Book.year < 1950).order_by(Book.year)).all()
    print([(b.title, b.year) for b in old_books])
# [('Emma', 1815), ('1984', 1949)]

    dune = session.scalars(select(Book).where(Book.title.like("Dune%")).order_by(Book.title)).all()
    print([b.title for b in dune])
# ['Dune', 'Dune Messiah']

    # joins and aggregates: books per author
    rows = session.execute(
        select(Author.name, func.count(Book.id).label("n"))
        .join(Book).group_by(Author.id).order_by(func.count(Book.id).desc(), Author.name)
    ).all()
    print(rows)
# [('Frank Herbert', 2), ('George Orwell', 1), ('Jane Austen', 1)]

    one = session.scalar(select(Author).where(Author.name == "Jane Austen"))
    print(one.name, [b.title for b in one.books])          # following a relationship loads the books
# Jane Austen ['Emma']
```

(Inside the `with` block the print lines are shown at the same level of indentation as the comments above for readability.) `.scalars()` returns model objects, `.execute()` returns rows of columns, `.scalar()` returns the first column of the first row, and `.one()`, `.first()` and `.all()` shape the result. All values in `where(...)` are sent as **bound parameters**, so the ORM is injection-safe unless you build SQL text yourself.

## 5. Changing data: the unit of work

The session tracks every object it loaded. You change Python attributes; on `flush`/`commit` it works out the `UPDATE`s and `INSERT`s itself.

```python
with Session(engine) as session:
    book = session.scalar(select(Book).where(Book.title == "Emma"))
    book.year = 1816                                       # just an attribute change...
    session.add(Book(title="Persuasion", year=1817, author=book.author))
    session.commit()                                       # ...the UPDATE and INSERT are sent here, in one transaction

with Session(engine) as session:
    print(sorted((b.title, b.year) for b in session.scalars(select(Book).join(Author).where(Author.name == "Jane Austen"))))
# [('Emma', 1816), ('Persuasion', 1817)]

# rollback on error: nothing is saved
with Session(engine) as session:
    try:
        session.add(Author(name="Jane Austen"))             # duplicate name violates the UNIQUE constraint
        session.commit()
    except Exception as exc:
        session.rollback()
        print("rolled back:", type(exc).__name__)
# rolled back: IntegrityError
    print(session.scalar(select(func.count()).select_from(Author)), "authors still")
# 3 authors still
```

Cascade rules (`cascade="all, delete-orphan"`) make deleting an author delete their books too. For bulk changes of many rows, prefer one set-based statement (`update(Book).where(...).values(...)`) over loading and changing objects one by one.

## 6. The N+1 query problem

The most common ORM performance bug: you load **N** parents, then touch a relationship in a loop, and the ORM silently issues **one extra query per parent** (**lazy loading**). We can prove it by counting the SQL statements with an event hook:

```python
from sqlalchemy import event
from sqlalchemy.orm import selectinload

class QueryCounter:
    def __init__(self, engine):
        self.count = 0
        event.listen(engine, "before_cursor_execute", self._hit)
    def _hit(self, *args):
        self.count += 1
    def reset(self):
        self.count = 0

counter = QueryCounter(engine)

with Session(engine) as session:
    counter.reset()
    authors = session.scalars(select(Author).order_by(Author.name)).all()       # 1 query for the authors
    summary = {a.name: len(a.books) for a in authors}                           # a.books triggers 1 query PER author
    print("lazy loading:", counter.count, "queries for", len(authors), "authors")
# lazy loading: 4 queries for 3 authors

with Session(engine) as session:
    counter.reset()
    authors = session.scalars(select(Author).options(selectinload(Author.books)).order_by(Author.name)).all()
    summary = {a.name: len(a.books) for a in authors}                           # books already loaded
    print("selectinload:", counter.count, "queries; result:", summary)
# selectinload: 2 queries; result: {'Frank Herbert': 2, 'George Orwell': 1, 'Jane Austen': 2}
```

With 3 authors it is 4 queries versus 2; with 10,000 authors it is 10,001 versus 2. Fixes: **eager loading** (`selectinload` for collections, `joinedload` for many-to-one), a **join** that fetches what you need in one query, or a query that computes the summary **in the database** (the `GROUP BY` in section 4 needs just one query). Make N+1 visible in development by logging queries (`create_engine(..., echo=True)`) and by tests that assert a maximum query count, like the counter above.

## 7. Transactions and concurrency in practice

- **A session is a transaction:** changes are invisible to others until `commit()`. Use `with Session(engine) as s, s.begin():` to commit on success and roll back on an exception automatically.
- **Keep transactions short:** do not hold one open while calling a slow external service.
- **Lost updates:** two requests read a balance of 100 and each write 90. Use **row locks** (`select(...).with_for_update()` on databases that support it, see [PostgreSQL](../../05-databases/postgresql/01-postgresql-specific-features.md)), **atomic SQL** (`UPDATE accounts SET balance = balance - 10 WHERE id = ? AND balance >= 10`) or **optimistic locking** with a version column.
- **Connection pooling:** the engine keeps a pool of connections (default 5, plus overflow); size it against the database's connection limit across all app processes.
- **Isolation levels** control what concurrent transactions can see ([transactions lesson](../../05-databases/transactions-acid/README.md)).

```python
from sqlalchemy import update

with Session(engine) as session, session.begin():              # begin(): commit on success, rollback on exception
    session.execute(update(Book).where(Book.year < 1900).values(year=Book.year + 1))   # one set-based UPDATE
with Session(engine) as session:
    print(session.scalar(select(Book.year).where(Book.title == "Emma")))
# 1817
```

## 8. Schema changes: migrations

`create_all` creates tables but never alters them. Real systems change schemas continuously, so use a **migration tool** (**Alembic** for SQLAlchemy, built into Django): each change is a versioned script (`ALTER TABLE ... ADD COLUMN`) applied in order and reversible, committed to git alongside the code. Safe practice for live systems: make changes **backwards compatible** in steps (add a nullable column; deploy code that writes it; backfill; make it required; later drop the old column) so old and new code versions can run together during a deploy.

## 9. Structure: the repository pattern and FastAPI

Keep SQL out of your route handlers. A **repository** is a small class that exposes the operations your application needs and hides how they are stored; the rest of the code (and tests) depend on its interface.

```python
class BookRepository:
    def __init__(self, session: Session):
        self.session = session

    def by_author(self, name: str) -> list[Book]:
        return list(self.session.scalars(select(Book).join(Author).where(Author.name == name).order_by(Book.year)))

    def add(self, author_name: str, title: str, year: int) -> Book:
        author = self.session.scalar(select(Author).where(Author.name == author_name)) or Author(name=author_name)
        book = Book(title=title, year=year, author=author)
        self.session.add(book)
        return book

with Session(engine) as session:
    repo = BookRepository(session)
    repo.add("Ursula K. Le Guin", "A Wizard of Earthsea", 1968)
    session.commit()
    print([b.title for b in repo.by_author("Ursula K. Le Guin")])
# ['A Wizard of Earthsea']
```

In a FastAPI app, give each request its own session through a **dependency with `yield`** (cleanup runs after the response), and override it in tests with an in-memory database:

```python
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

def get_session():
    with Session(engine) as session:                       # one session per request, always closed
        yield session

@app.get("/authors/{name}/books")
def books_of(name: str, session: Session = Depends(get_session)):
    return [{"title": b.title, "year": b.year} for b in BookRepository(session).by_author(name)]

client = TestClient(app)
print(client.get("/authors/Frank Herbert/books").json())
# [{'title': 'Dune', 'year': 1965}, {'title': 'Dune Messiah', 'year': 1969}]
```

## 10. Choosing the tool

| Need | Use |
|------|-----|
| Small script, one query | `sqlite3` or the driver directly |
| Complex reporting SQL, full control | SQL strings (parameterized) or SQLAlchemy Core |
| Application with many related entities | the ORM (SQLAlchemy, Django ORM) |
| Async web app | SQLAlchemy's async engine with an async driver (`asyncpg`, `aiosqlite`) |
| Data analysis | `pandas.read_sql` (see [NumPy and pandas](../data-with-numpy-pandas/01-numpy-and-pandas-essentials.md)) |

An ORM is not a substitute for understanding SQL, indexes and query plans ([indexes lesson](../../05-databases/indexes-query-plans/README.md)): check what it generates, and drop to raw SQL for the hard queries.

## 11. Common mistakes

- N+1 queries from lazy-loaded relationships in loops (count your queries).
- Building SQL with f-strings, even "just once" (injection).
- Forgetting `commit()` (changes vanish) or never closing sessions (connection leaks).
- A global session shared by all requests and threads (sessions are **not** thread-safe).
- Loading entire tables into memory (`.all()` on millions of rows) instead of filtering, paginating or streaming.
- Doing work in Python that the database does better (filter in Python after fetching everything).
- Using `create_all` in production instead of migrations.
- Hiding all SQL behind the ORM and never reading the queries it generates.
- Storing money as floats (use integers of cents or `Numeric`).
- Long transactions that hold locks while waiting for network calls.

## 12. Two real-world examples

**Example 1: The slow admin page.** A page listing 500 orders took 9 seconds. Query logging showed 1,501 queries: one for orders, then one each for the customer, items and shipping address of every order. Adding `selectinload` for the relationships and a `joinedload` for the customer reduced it to 4 queries and 120 ms.

**Example 2: The double refund.** Two simultaneous refund requests each read an order with status `paid`, each issued a refund, and each set `refunded`. The fix was a row lock (`with_for_update()`) on the order inside the transaction, plus a unique idempotency key on the refund row ([retries and idempotency](../../11-distributed-systems/transactions/01-idempotency-retries-and-sagas.md)).

## 13. Practice

1. Add a `Review` model (book, rating 1 to 5, text) with a relationship from `Book`. Write a query returning each book's average rating, ordered best first.
2. Write a function `titles_by_author(session)` returning `{author: [titles]}` in exactly **two** queries, and assert it with the `QueryCounter`.
3. Using `with_for_update`, sketch a `transfer(session, from_id, to_id, amount)` that cannot overdraw an account. Why do you lock accounts in a consistent order?
4. Convert `BookRepository.add` to raise a clear error if `year` is in the future.
5. What SQL does `select(Book).where(Book.year < 1950)` generate? (Print `str(statement)`.)
6. Explain why a session must not be shared between threads.

<details>
<summary>Solutions</summary>

1. ```python
   from sqlalchemy import Text
   class Review(Base):
       __tablename__ = "reviews"
       id: Mapped[int] = mapped_column(primary_key=True)
       book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
       rating: Mapped[int]
       text: Mapped[str] = mapped_column(Text, default="")
   Base.metadata.create_all(engine)
   with Session(engine) as s:
       dune = s.scalar(select(Book).where(Book.title == "Dune"))
       emma = s.scalar(select(Book).where(Book.title == "Emma"))
       s.add_all([Review(book_id=dune.id, rating=5), Review(book_id=dune.id, rating=4), Review(book_id=emma.id, rating=3)])
       s.commit()
       best = s.execute(select(Book.title, func.avg(Review.rating).label("avg")).join(Review, Review.book_id == Book.id)
                        .group_by(Book.id).order_by(func.avg(Review.rating).desc())).all()
       print(best)
   # [('Dune', 4.5), ('Emma', 3.0)]
   ```
2. ```python
   def titles_by_author(session):
       authors = session.scalars(select(Author).options(selectinload(Author.books)).order_by(Author.name)).all()
       return {a.name: sorted(b.title for b in a.books) for a in authors}
   with Session(engine) as s:
       counter.reset()
       result = titles_by_author(s)
       assert counter.count == 2, counter.count
       print(result["Frank Herbert"])
   # ['Dune', 'Dune Messiah']
   ```
3. ```python
   def transfer(session, from_id, to_id, amount):
       first, second = sorted([from_id, to_id])                  # consistent lock order avoids deadlocks between opposite transfers
       accounts = {a.id: a for a in session.scalars(select(Account).where(Account.id.in_([first, second])).order_by(Account.id).with_for_update())}
       if accounts[from_id].balance < amount:
           raise ValueError("insufficient funds")
       accounts[from_id].balance -= amount
       accounts[to_id].balance += amount
   ```
   (`Account` is a model with `id` and `balance`; SQLite ignores `FOR UPDATE`, PostgreSQL and MySQL honour it.) Two transfers in opposite directions would otherwise each hold one lock and wait for the other: a deadlock.
4. ```python
   import datetime
   def add_checked(self, author_name, title, year):
       if year > datetime.date.today().year:
           raise ValueError("year cannot be in the future")
       return self.add(author_name, title, year)
   BookRepository.add_checked = add_checked
   ```
5. ```python
   print(str(select(Book).where(Book.year < 1950)).replace("\n", " "))
   # SELECT books.id, books.title, books.year, books.author_id  FROM books  WHERE books.year < :year_1
   ```
   The value is a **bound parameter** (`:year_1`), not text in the SQL.
6. A session holds a connection and an identity map of loaded objects with no internal locking; two threads using it concurrently can corrupt that state or interleave statements on one connection. Create one session per thread or per request.

</details>

## 14. Check yourself

1. What are the DB-API steps, and why use `?` placeholders?
2. What are an Engine, a model and a Session?
3. What is the unit-of-work pattern?
4. What is the N+1 problem and how do you detect and fix it?
5. When would you use a set-based `UPDATE` instead of changing objects?
6. Why use migrations instead of `create_all`?
7. What does a repository give you?

<details>
<summary>Answers</summary>

1. Connect, create a cursor, execute with parameters, fetch, commit. Placeholders send values separately from the SQL text, preventing injection.
2. The engine is the connection pool and dialect; a model is a class mapped to a table; a session is a unit of work that tracks objects and writes changes in a transaction.
3. The session records which objects were added, changed or deleted and writes them together on commit.
4. One query for the parents plus one per parent for a lazy-loaded relationship; detect by counting or logging queries; fix with eager loading (`selectinload`, `joinedload`), joins or aggregation in SQL.
5. When changing many rows by a rule: one statement in the database is far faster than loading each object into Python.
6. `create_all` cannot alter existing tables; migrations are versioned, reviewable, reversible schema changes applied in order.
7. A small interface that hides storage details, keeps SQL out of business and route code, and can be replaced by a fake in tests.

</details>

[Back to Modern Python](../README.md)
