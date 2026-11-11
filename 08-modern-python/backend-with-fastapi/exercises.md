# Backend with FastAPI: Exercises

These problems go with the [Backend with FastAPI lesson](README.md). Try each one before opening its solution.

<details>
<summary>Setup code the solutions use (copied from the lessons)</summary>

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi import HTTPException
from pydantic import BaseModel, Field
from fastapi import Depends
import hmac
from fastapi import Header

app = FastAPI(title="Shop API", version="1.0")

@app.get("/health")
def health():
    return {"status": "ok"}                         # a dict becomes JSON automatically

client = TestClient(app)                             # calls the app in-process: no network, no server, fast
r = client.get("/health")
print(r.status_code, r.json())
# 200 {'status': 'ok'}


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

</details>

## Problems

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

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Building a Web API with FastAPI](01-building-a-web-api-with-fastapi.md)
