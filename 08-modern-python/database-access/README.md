# Database Access

From sqlite3 to the SQLAlchemy ORM, sessions, relationships and the N+1 problem.

## Detailed lessons

- [Database access from Python](01-sqlalchemy-and-database-access.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Question | Answer |
|----------|--------|
| What are the DB-API steps, and why use `?` placeholders? | Connect, create a cursor, execute with parameters, fetch, commit. Placeholders send values separately from the SQL text, preventing injection. |
| What are an Engine, a model and a Session? | The engine is the connection pool and dialect; a model is a class mapped to a table; a session is a unit of work that tracks objects and writes changes in a transaction. |
| What is the unit-of-work pattern? | The session records which objects were added, changed or deleted and writes them together on commit. |
| What is the N+1 problem and how do you detect and fix it? | One query for the parents plus one per parent for a lazy-loaded relationship; detect by counting or logging queries; fix with eager loading (`selectinload`, `joinedload`), joins or aggregation in SQL. |
| When would you use a set-based `UPDATE` instead of changing objects? | When changing many rows by a rule: one statement in the database is far faster than loading each object into Python. |

Back to [modern Python](../README.md).
