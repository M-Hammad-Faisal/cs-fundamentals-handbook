# Building a Web API with FastAPI

**Prerequisites:** [REST APIs and WebSockets lab](../../07-networking/apis-realtime/01-rest-apis-and-websockets-lab.md), [HTTP](../../07-networking/dns-http/README.md), [type hints](../typing-hints/README.md), [dataclasses](../dataclasses-enums/README.md), [testing in depth](../testing-in-depth/01-pytest-mocking-and-property-testing.md). **You will learn:** how to build a real JSON web API with **FastAPI**: routes and parameters, **Pydantic** models that validate input and shape output, **dependency injection** (`Depends`), authentication with an API key, custom errors, idempotent `POST`, automatic **OpenAPI documentation**, and how to **test the whole API without starting a server** using `TestClient`. Third-party packages are used (`pip install fastapi httpx pydantic`; to serve for real, also `uvicorn`); every example below was run and the outputs are the real ones.

## 1. In plain words

A **web API** lets programs talk to your code over HTTP: a client sends a request (`POST /items` with JSON), your function runs, and the response comes back as JSON with a status code. A framework handles the plumbing: parsing the URL and body, validating data, turning exceptions into proper HTTP errors and producing documentation. **FastAPI** builds on Python **type hints**: you declare what each endpoint accepts and returns, and FastAPI uses the declarations to validate requests, convert types, and generate interactive docs automatically.

Key ideas:

- A **route** maps a method and path (`GET /items/{item_id}`) to a Python function.
- **Pydantic models** describe JSON bodies; invalid input is rejected with a `422` response before your code runs.
- **Dependencies** are functions FastAPI calls for you and passes in (a database session, the current user), which makes code reusable and easy to test.
- **ASGI** is the interface between the web server (uvicorn) and the app; FastAPI supports both normal `def` and `async def` handlers.

## 2. The smallest API, and how to test it without a server

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI(title="Shop API", version="1.0")

@app.get("/health")
def health():
    return {"status": "ok"}                         # a dict becomes JSON automatically

client = TestClient(app)                             # calls the app in-process: no network, no server, fast
r = client.get("/health")
print(r.status_code, r.json())
# 200 {'status': 'ok'}
```

To serve it for real you would save it as `main.py` and run `uvicorn main:app --reload` (then open `http://127.0.0.1:8000/docs`). During development and in tests, `TestClient` is all you need.

## 3. Path and query parameters

Names in `{braces}` are **path parameters**; other function arguments are **query parameters** (`?limit=2`). The type hints do the conversion and validation.

```python
from fastapi import HTTPException

PRODUCTS = {1: "pen", 2: "book", 3: "mug", 4: "lamp"}

@app.get("/products/{product_id}")
def get_product(product_id: int):                    # "7" in the URL is converted to the int 7 (or rejected)
    if product_id not in PRODUCTS:
        raise HTTPException(status_code=404, detail="product not found")
    return {"id": product_id, "name": PRODUCTS[product_id]}

@app.get("/products")
def list_products(limit: int = 2, offset: int = 0):  # defaults make query parameters optional
    ids = sorted(PRODUCTS)[offset:offset + limit]
    return [{"id": i, "name": PRODUCTS[i]} for i in ids]

print(client.get("/products/2").json())
# {'id': 2, 'name': 'book'}
r = client.get("/products/99")
print(r.status_code, r.json())
# 404 {'detail': 'product not found'}
print(client.get("/products?limit=2&offset=2").json())
# [{'id': 3, 'name': 'mug'}, {'id': 4, 'name': 'lamp'}]
r = client.get("/products/abc")                      # not an integer: FastAPI rejects it before our code runs
print(r.status_code, r.json()["detail"][0]["type"], r.json()["detail"][0]["loc"])
# 422 int_parsing ['path', 'product_id']
```

## 4. Request bodies and validation with Pydantic

Declare the shape of a JSON body as a **Pydantic model**. Constraints (`gt`, `min_length`, patterns) are checked automatically; a bad request gets a `422` with a precise list of problems. A separate **response model** controls what goes back, so internal fields never leak.

```python
from pydantic import BaseModel, Field

class ItemIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0, description="price in dollars")
    tags: list[str] = []

class ItemOut(BaseModel):
    id: int
    name: str
    price: float
    tags: list[str]

ITEMS: dict[int, dict] = {}

@app.post("/items", response_model=ItemOut, status_code=201)
def create_item(item: ItemIn):                       # FastAPI parses and validates the JSON body into ItemIn
    new_id = len(ITEMS) + 1
    ITEMS[new_id] = {"id": new_id, **item.model_dump(), "internal_cost": 0.4 * item.price}   # an internal field
    return ITEMS[new_id]                             # response_model filters it down to ItemOut

r = client.post("/items", json={"name": "pen", "price": 1.5, "tags": ["office"]})
print(r.status_code, r.json())
# 201 {'id': 1, 'name': 'pen', 'price': 1.5, 'tags': ['office']}

r = client.post("/items", json={"name": "", "price": -3})
print(r.status_code)
for problem in r.json()["detail"]:
    print(problem["loc"], "->", problem["msg"])
# 422
# ['body', 'name'] -> String should have at least 1 character
# ['body', 'price'] -> Input should be greater than 0
```

Note `internal_cost` was stored but **never returned**: the `response_model` is an allow-list of output fields (the [mass assignment](../../10-security/web-vulnerabilities/01-owasp-top-ten-in-python.md) defence in reverse). Two separate models for input and output also stop clients from setting fields such as `id` or `is_admin`.

```python
@app.get("/items/{item_id}", response_model=ItemOut)
def read_item(item_id: int):
    if item_id not in ITEMS:
        raise HTTPException(404, "item not found")
    return ITEMS[item_id]

print(client.get("/items/1").json()["name"], client.get("/items/42").status_code)
# pen 404
```

## 5. Dependency injection with `Depends`

A **dependency** is a function whose result FastAPI injects into your handler. Use them for things shared by many routes: a database session, settings, the current user, pagination parameters. The great benefit: in tests you can **replace** a dependency with a fake.

```python
from fastapi import Depends

class ItemRepo:                                       # stands in for a database layer
    def __init__(self):
        self.data = {}
    def add(self, name):
        self.data[len(self.data) + 1] = name
        return len(self.data)
    def names(self):
        return list(self.data.values())

real_repo = ItemRepo()

def get_repo():
    return real_repo                                   # in production this might open a database session

@app.post("/notes", status_code=201)
def add_note(name: str, repo: ItemRepo = Depends(get_repo)):
    return {"id": repo.add(name)}

@app.get("/notes")
def list_notes(repo: ItemRepo = Depends(get_repo)):
    return repo.names()

client.post("/notes", params={"name": "milk"})
print(client.get("/notes").json())
# ['milk']

fake = ItemRepo()
fake.add("test-only note")
app.dependency_overrides[get_repo] = lambda: fake      # tests swap the dependency: no real database touched
print(client.get("/notes").json())
# ['test-only note']
app.dependency_overrides.clear()
```

Dependencies can depend on other dependencies (a tree is resolved for you), and a dependency using `yield` gets **cleanup** code after the response (close the database session).

## 6. Authentication and authorization as dependencies

A dependency that raises `HTTPException` protects every route that uses it. Here, a simple **API key** in a header (see the [authentication lesson](../../10-security/authentication/01-authn-authz-sessions-jwt.md) for sessions, JWT and OAuth, which you would use for real users):

```python
import hmac
from fastapi import Header

API_KEYS = {"key-ada": {"user": "ada", "role": "admin"}, "key-bob": {"user": "bob", "role": "viewer"}}

def current_user(x_api_key: str = Header(default="")):       # reads the X-API-Key header
    for key, user in API_KEYS.items():
        if hmac.compare_digest(key, x_api_key):               # constant-time comparison
            return user
    raise HTTPException(status_code=401, detail="missing or invalid API key")

def require_admin(user: dict = Depends(current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="admins only")
    return user

@app.get("/me")
def me(user: dict = Depends(current_user)):
    return user

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, admin: dict = Depends(require_admin)):
    ITEMS.pop(item_id, None)

print(client.get("/me").status_code, client.get("/me", headers={"X-API-Key": "key-bob"}).json())
# 401 {'user': 'bob', 'role': 'viewer'}
print(client.delete("/items/1", headers={"X-API-Key": "key-bob"}).status_code, client.delete("/items/1", headers={"X-API-Key": "key-ada"}).status_code)
# 403 204
```

`401` means "I do not know who you are" and `403` means "I know who you are and you may not do that". Always check **object-level** permissions too (does this user own this item?), not just roles.

## 7. Idempotent POST with an `Idempotency-Key`

As the [retries lesson](../../11-distributed-systems/transactions/01-idempotency-retries-and-sagas.md) explains, clients retry on timeouts, so creating things must be safe to repeat. Accept a client-generated key and replay the stored response:

```python
SEEN_KEYS: dict[str, dict] = {}
ORDERS: list[dict] = []

@app.post("/orders", status_code=201)
def create_order(item_id: int, idempotency_key: str = Header()):
    if idempotency_key in SEEN_KEYS:
        return SEEN_KEYS[idempotency_key]                    # a retry: return the original result, create nothing
    order = {"order_id": len(ORDERS) + 1, "item_id": item_id}
    ORDERS.append(order)
    SEEN_KEYS[idempotency_key] = order
    return order

h = {"Idempotency-Key": "abc-123"}
first = client.post("/orders", params={"item_id": 5}, headers=h).json()
retry = client.post("/orders", params={"item_id": 5}, headers=h).json()
print(first == retry, len(ORDERS))
# True 1
```

(In production the key store must be a database table with a unique constraint, written in the same transaction as the order.)

## 8. Custom errors, and consistent error responses

Consistency helps clients. Define your own exception and a handler that always returns the same JSON shape:

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class OutOfStock(Exception):
    def __init__(self, name):
        self.name = name

@app.exception_handler(OutOfStock)
async def out_of_stock_handler(request: Request, exc: OutOfStock):
    return JSONResponse(status_code=409, content={"error": "out_of_stock", "item": exc.name})

app.middleware_stack = None        # DEMO ONLY: this lesson adds handlers after serving requests; a real app registers them all at import time

@app.post("/buy/{name}")
def buy(name: str):
    if name == "mug":
        raise OutOfStock(name)
    return {"bought": name}

r = client.post("/buy/mug")
print(r.status_code, r.json())
# 409 {'error': 'out_of_stock', 'item': 'mug'}
```

Use the right status codes: `200` OK, `201` created, `204` no content, `400` malformed, `401` not authenticated, `403` forbidden, `404` not found, `409` conflict, `422` validation failed, `429` too many requests, `500` server error (never leak stack traces to clients; log them).

## 9. Automatic documentation

FastAPI builds an **OpenAPI** description of every route, model and response from your type hints, and serves interactive docs at `/docs` (Swagger UI) and `/redoc`. The raw document is JSON at `/openapi.json`, which other tools use to generate client libraries.

```python
spec = client.get("/openapi.json").json()
print(spec["info"]["title"], "| some paths:", sorted(spec["paths"])[:4])
print("ItemIn schema fields:", sorted(spec["components"]["schemas"]["ItemIn"]["properties"]))
# Shop API | some paths: ['/buy/{name}', '/health', '/items', '/items/{item_id}']
# ItemIn schema fields: ['name', 'price', 'tags']
```

The documentation can never drift from the code because it is **generated** from it.

## 10. `def` or `async def`?

```python
import asyncio

@app.get("/sync-sleep")
def blocking_handler():                    # runs in a thread pool: fine for blocking libraries
    return {"mode": "def"}

@app.get("/async-sleep")
async def async_handler():                 # runs on the event loop: use only with async libraries (await ...)
    await asyncio.sleep(0)
    return {"mode": "async def"}

print(client.get("/sync-sleep").json(), client.get("/async-sleep").json())
# {'mode': 'def'} {'mode': 'async def'}
```

Rule: if the handler calls **blocking** code (a normal database driver, `requests`, `time.sleep`), use a plain `def` and FastAPI runs it in a thread pool; if you use `async def`, every call inside must be non-blocking (`await`), or the whole server stalls (see [asyncio](../async-concurrency/README.md)).

## 11. A sensible project layout

```text
shop_api/
  pyproject.toml
  src/shop_api/
    main.py            # creates the FastAPI app and includes routers
    config.py          # settings from environment variables (never hard-coded secrets)
    models.py          # Pydantic schemas (request/response)
    db.py              # database engine/session and the get_db dependency
    routers/items.py   # APIRouter with the item routes
    routers/orders.py
    services/          # business logic, no FastAPI imports (easy to test)
  tests/
    conftest.py        # TestClient fixture, dependency overrides, test database
    test_items.py
```

Keep **routes thin** (parse, call a service, return) and put business rules in plain functions that you can unit test without HTTP. The [next lesson](../database-access/01-sqlalchemy-and-database-access.md) adds a real database.

## 12. Common mistakes

- Putting business logic in route functions; it becomes untestable and cannot be reused.
- Returning database objects directly instead of a response model (leaking internal fields).
- Using one model for input and output (clients can set `id` or `is_admin`).
- Calling blocking code inside `async def` handlers.
- Hard-coding secrets and configuration instead of reading environment variables.
- Returning `200` with `{"error": ...}` instead of a real status code.
- Allowing wide-open CORS (`*`) with credentials, or skipping HTTPS, rate limits and input limits (see [security](../../10-security/README.md)).
- Skipping API versioning (`/v1/...`) and breaking clients on change.
- In-memory state (the dictionaries above) in a multi-worker deployment: each worker has its own copy; use a database.

## 13. Two real-world examples

**Example 1: The internal tool.** A team replaced a pile of ad-hoc scripts with a FastAPI service: Pydantic models validated every request, the generated `/docs` page became the API reference for other teams, and the `TestClient` suite (with dependencies overridden) ran in two seconds in CI.

**Example 2: Machine learning behind an endpoint.** A data scientist wrapped a trained model in a `POST /predict` route. A Pydantic model rejected malformed feature vectors, the model was loaded once at startup (not per request), and the heavy computation ran in a process pool so the API stayed responsive ([concurrency](../concurrency/01-threads-processes-and-futures.md)).

## 14. Practice

1. Add `PUT /items/{item_id}` that replaces an item (validate with `ItemIn`, return `ItemOut`, `404` if missing).
2. Add pagination to `GET /items` with `limit` (1 to 100, default 10) and `offset` (0 or more) validated with `Query(ge=..., le=...)`. What happens for `limit=500`?
3. Write a dependency `rate_limit` that allows 3 calls per client per minute (use the fake clock idea from [system design](../../09-interview-playbook/system-design-basics/02-five-more-designs.md)) and returns `429` after that.
4. Override `current_user` in a test so every request acts as admin without sending a key.
5. Why is the response for an unknown path `404` with a JSON body, and how would you change its shape?
6. Explain the difference between `401` and `403` in your own words.

<details>
<summary>Solutions</summary>

1. ```python
   @app.put("/items/{item_id}", response_model=ItemOut)
   def replace_item(item_id: int, item: ItemIn):
       if item_id not in ITEMS:
           raise HTTPException(404, "item not found")
       ITEMS[item_id] = {"id": item_id, **item.model_dump()}
       return ITEMS[item_id]
   client.post("/items", json={"name": "cup", "price": 2.0})
   new_id = max(ITEMS)
   print(client.put(f"/items/{new_id}", json={"name": "big cup", "price": 3.0}).json()["name"], client.put("/items/999", json={"name": "x", "price": 1}).status_code)
   # big cup 404
   ```
2. ```python
   from fastapi import Query
   @app.get("/items")
   def list_items(limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0)):
       ids = sorted(ITEMS)[offset:offset + limit]
       return [ITEMS[i]["name"] for i in ids]
   print(client.get("/items?limit=500").status_code, client.get("/items?limit=1").status_code)
   # 422 200
   ```
3. ```python
   import time
   CALLS: dict[str, list[float]] = {}
   def rate_limit(user: dict = Depends(current_user)):
       now = time.time()
       recent = [t for t in CALLS.get(user["user"], []) if now - t < 60]
       if len(recent) >= 3:
           raise HTTPException(429, "too many requests")
       CALLS[user["user"]] = recent + [now]
   @app.get("/limited")
   def limited(_: None = Depends(rate_limit)):
       return {"ok": True}
   codes = [client.get("/limited", headers={"X-API-Key": "key-ada"}).status_code for _ in range(5)]
   print(codes)
   # [200, 200, 200, 429, 429]
   ```
4. ```python
   app.dependency_overrides[current_user] = lambda: {"user": "test", "role": "admin"}
   print(client.get("/me").json())
   app.dependency_overrides.clear()
   # {'user': 'test', 'role': 'admin'}
   ```
5. FastAPI (via Starlette) has a default handler for `HTTPException` that returns `{"detail": ...}`. Register your own handler with `@app.exception_handler(StarletteHTTPException)` to change the shape (for example `{"error": ..., "request_id": ...}`).
6. `401`: the server does not know who you are (no or invalid credentials). `403`: it knows who you are, but you are not allowed to do this.

</details>

## 15. Check yourself

1. What does FastAPI do with type hints?
2. What status code does a request with an invalid body get, and who produces it?
3. Why separate input and output models?
4. What is a dependency, and how does it help testing?
5. When do you use `def` and when `async def`?
6. How do you make a `POST` safe to retry?
7. Why is `TestClient` useful?

<details>
<summary>Answers</summary>

1. Uses them to parse and convert request data, validate it, shape responses and generate OpenAPI documentation.
2. `422`; FastAPI/Pydantic produce it automatically before the handler runs, listing each failing field.
3. The output model is an allow-list that prevents internal fields leaking, and a separate input model prevents clients from setting fields they should not (ids, roles).
4. A function FastAPI calls and injects into handlers (a repository, the current user); tests can replace it with `app.dependency_overrides`.
5. `def` (run in a thread pool) for blocking code; `async def` only when everything awaited inside is non-blocking.
6. Require an idempotency key from the client and return the stored result for repeated keys (stored durably, in the same transaction as the work).
7. It exercises the whole app (routing, validation, dependencies) in-process without a server or network, so tests are fast and deterministic.

</details>

[Back to Modern Python](../README.md)
