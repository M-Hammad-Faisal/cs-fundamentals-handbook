# Backend with FastAPI: One-Page Summary

## Questions worth remembering

- **What does FastAPI do with type hints?** Uses them to parse and convert request data, validate it, shape responses and generate OpenAPI documentation.
- **What status code does a request with an invalid body get, and who produces it?** `422`; FastAPI/Pydantic produce it automatically before the handler runs, listing each failing field.
- **Why separate input and output models?** The output model is an allow-list that prevents internal fields leaking, and a separate input model prevents clients from setting fields they should not (ids, roles).
- **What is a dependency, and how does it help testing?** A function FastAPI calls and injects into handlers (a repository, the current user); tests can replace it with `app.dependency_overrides`.
- **When do you use `def` and when `async def`?** `def` (run in a thread pool) for blocking code; `async def` only when everything awaited inside is non-blocking.
- **How do you make a `POST` safe to retry?** Require an idempotency key from the client and return the stored result for repeated keys (stored durably, in the same transaction as the work).

Practice problems with solutions are in the **Practice** section of each lesson.

[Lesson](README.md) · [Building a Web API with FastAPI](01-building-a-web-api-with-fastapi.md)
