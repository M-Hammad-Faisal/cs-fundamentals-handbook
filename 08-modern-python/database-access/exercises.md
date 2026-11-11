# Database Access: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## Database Access from Python

1. Add a `Review` model (book, rating 1 to 5, text) with a relationship from `Book`. Write a query returning each book's average rating, ordered best first.
2. Write a function `titles_by_author(session)` returning `{author: [titles]}` in exactly **two** queries, and assert it with the `QueryCounter`.
3. Using `with_for_update`, sketch a `transfer(session, from_id, to_id, amount)` that cannot overdraw an account. Why do you lock accounts in a consistent order?
4. Convert `BookRepository.add` to raise a clear error if `year` is in the future.
5. What SQL does `select(Book).where(Book.year < 1950)` generate? (Print `str(statement)`.)
6. Explain why a session must not be shared between threads.

<details>
<summary>Solutions</summary>

1. ```python no-run
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
2. ```python no-run
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
3. ```python no-run
   def transfer(session, from_id, to_id, amount):
       first, second = sorted([from_id, to_id])                  # consistent lock order avoids deadlocks between opposite transfers
       accounts = {a.id: a for a in session.scalars(select(Account).where(Account.id.in_([first, second])).order_by(Account.id).with_for_update())}
       if accounts[from_id].balance < amount:
           raise ValueError("insufficient funds")
       accounts[from_id].balance -= amount
       accounts[to_id].balance += amount
   ```
   (`Account` is a model with `id` and `balance`; SQLite ignores `FOR UPDATE`, PostgreSQL and MySQL honour it.) Two transfers in opposite directions would otherwise each hold one lock and wait for the other: a deadlock.
4. ```python no-run
   import datetime
   def add_checked(self, author_name, title, year):
       if year > datetime.date.today().year:
           raise ValueError("year cannot be in the future")
       return self.add(author_name, title, year)
   BookRepository.add_checked = add_checked
   ```
5. ```python no-run
   print(str(select(Book).where(Book.year < 1950)).replace("\n", " "))
   # SELECT books.id, books.title, books.year, books.author_id  FROM books  WHERE books.year < :year_1
   ```
   The value is a **bound parameter** (`:year_1`), not text in the SQL.
6. A session holds a connection and an identity map of loaded objects with no internal locking; two threads using it concurrently can corrupt that state or interleave statements on one connection. Create one session per thread or per request.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Database Access from Python](01-sqlalchemy-and-database-access.md)
