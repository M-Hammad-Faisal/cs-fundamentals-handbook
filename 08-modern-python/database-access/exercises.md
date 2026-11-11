# Database Access: Exercises

These problems go with the [Database Access lesson](README.md). Try each one before opening its solution.

<details>
<summary>Setup code the solutions use (copied from the lessons)</summary>

```python
from sqlalchemy import ForeignKey, String, create_engine, select, func
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from sqlalchemy import event
from sqlalchemy.orm import selectinload

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

</details>

## Problems

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

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Database Access from Python](01-sqlalchemy-and-database-access.md)
