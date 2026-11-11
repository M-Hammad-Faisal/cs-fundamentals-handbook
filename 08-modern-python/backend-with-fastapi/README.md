# Backend with FastAPI

Build and test a real JSON web API with FastAPI and Pydantic.

## Detailed lessons

- [Building a web API with FastAPI](01-building-a-web-api-with-fastapi.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Question | Answer |
|----------|--------|
| What does FastAPI do with type hints? | Uses them to parse and convert request data, validate it, shape responses and generate OpenAPI documentation. |
| What status code does a request with an invalid body get, and who produces it? | `422`; FastAPI/Pydantic produce it automatically before the handler runs, listing each failing field. |
| Why separate input and output models? | The output model is an allow-list that prevents internal fields leaking, and a separate input model prevents clients from setting fields they should not (ids, roles). |
| What is a dependency, and how does it help testing? | A function FastAPI calls and injects into handlers (a repository, the current user); tests can replace it with `app.dependency_overrides`. |
| When do you use `def` and when `async def`? | `def` (run in a thread pool) for blocking code; `async def` only when everything awaited inside is non-blocking. |

Back to [modern Python](../README.md).
