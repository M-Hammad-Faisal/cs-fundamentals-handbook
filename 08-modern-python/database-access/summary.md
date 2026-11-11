# Database Access: One-Page Summary

## Key facts

- **DB-API (`sqlite3`):** `connect`, `execute(sql, params)` with `?` placeholders, `commit`; `with conn:` commits on success and rolls back on an exception.
- **SQLAlchemy 2.0:** models subclass `DeclarativeBase` with `Mapped[...] = mapped_column(...)`; `create_engine(url)` makes the pool; a `Session` is a unit of work (`add`, `flush`, `commit`, `rollback`).
- **Queries:** `select(Model).where(...)`, then `session.scalars(...)`, `.scalar_one()`, `.all()`; use `func.count`, `group_by` and joins like SQL.
- **Relationships and N+1:** lazy loading runs one extra query per row; fix with `selectinload` or `joinedload`, and count queries in tests.
- **Transactions:** one session per request or job, kept short; use a `version` column for optimistic locking, `FOR UPDATE` when you must lock.
- **Migrations:** version schema changes with Alembic, never edit an applied migration, and change schemas in backward-compatible steps (add, backfill, switch, drop).
- **Structure:** a repository class hides persistence; in FastAPI a dependency yields the session.
- **Choosing:** plain SQL for simple or hot paths, the ORM for rich domain models.

## Pitfalls

- Building SQL with f-strings or `+` (injection): always pass parameters.
- N+1 queries hidden behind attribute access in a loop.
- Sharing one session across threads or requests.
- Forgetting `commit`, or touching lazy attributes after the session closed (`DetachedInstanceError`).
- `Base.metadata.create_all` standing in for migrations in production.

## Self-check

- **What are the DB-API steps, and why use `?` placeholders?** Connect, create a cursor, execute with parameters, fetch, commit. Placeholders send values separately from the SQL text, preventing injection.
- **What are an Engine, a model and a Session?** The engine is the connection pool and dialect; a model is a class mapped to a table; a session is a unit of work that tracks objects and writes changes in a transaction.
- **What is the unit-of-work pattern?** The session records which objects were added, changed or deleted and writes them together on commit.
- **What is the N+1 problem and how do you detect and fix it?** One query for the parents plus one per parent for a lazy-loaded relationship; detect by counting or logging queries; fix with eager loading (`selectinload`, `joinedload`), joins or aggregation in SQL.
- **When would you use a set-based `UPDATE` instead of changing objects?** When changing many rows by a rule: one statement in the database is far faster than loading each object into Python.
- **Why use migrations instead of `create_all`?** `create_all` cannot alter existing tables; migrations are versioned, reviewable, reversible schema changes applied in order.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Database Access from Python](01-sqlalchemy-and-database-access.md)
