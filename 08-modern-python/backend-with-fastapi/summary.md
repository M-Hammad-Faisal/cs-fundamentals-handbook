# Backend with FastAPI: One-Page Summary

## Key facts

- **Routes:** `app = FastAPI()` and `@app.get("/items/{item_id}")`; typed path parameters are validated (`item_id: int` returns `422` for text); function arguments with defaults become query parameters.
- **Bodies and validation:** a Pydantic `BaseModel` argument is parsed from JSON; invalid input gives `422` with a list of errors; `response_model` controls (and filters) what is returned; `status_code=201` for creation; `HTTPException(status_code, detail)` for errors.
- **Dependencies:** `Depends(func)` supplies a database session, the current user or pagination to many routes; tests swap them with `app.dependency_overrides`.
- **Testing without a server:** `TestClient(app)` calls the app in-process.
- **`def` or `async def`:** `def` handlers run in a thread pool; `async def` handlers run on the event loop and must never block.
- **Safe retries:** accept an `Idempotency-Key` header and store the first response against it.
- **Docs for free:** `/docs` (Swagger UI) and `/openapi.json` are generated from your types.
- **Layout:** routers for HTTP, schemas for input and output, services for rules, a repository for storage.

## Pitfalls

- A blocking call (`time.sleep`, a sync database driver, `requests`) inside `async def` freezes every request.
- Returning an ORM object without a `response_model`, which can leak fields such as a password hash.
- Checking that a user is logged in but not that the record is theirs (IDOR).
- Global mutable state shared by all requests; catching an error and returning `200`.
- Running with `--reload` or debug settings in production.

## Self-check

- **What does FastAPI do with type hints?** Uses them to parse and convert request data, validate it, shape responses and generate OpenAPI documentation.
- **What status code does a request with an invalid body get, and who produces it?** `422`; FastAPI/Pydantic produce it automatically before the handler runs, listing each failing field.
- **Why separate input and output models?** The output model is an allow-list that prevents internal fields leaking, and a separate input model prevents clients from setting fields they should not (ids, roles).
- **What is a dependency, and how does it help testing?** A function FastAPI calls and injects into handlers (a repository, the current user); tests can replace it with `app.dependency_overrides`.
- **When do you use `def` and when `async def`?** `def` (run in a thread pool) for blocking code; `async def` only when everything awaited inside is non-blocking.
- **How do you make a `POST` safe to retry?** Require an idempotency key from the client and return the stored result for repeated keys (stored durably, in the same transaction as the work).

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Building a Web API with FastAPI](01-building-a-web-api-with-fastapi.md)
