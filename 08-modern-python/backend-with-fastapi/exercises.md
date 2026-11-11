# Backend with FastAPI: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## Building a Web API with FastAPI

1. Add `PUT /items/{item_id}` that replaces an item (validate with `ItemIn`, return `ItemOut`, `404` if missing).
2. Add pagination to `GET /items` with `limit` (1 to 100, default 10) and `offset` (0 or more) validated with `Query(ge=..., le=...)`. What happens for `limit=500`?
3. Write a dependency `rate_limit` that allows 3 calls per client per minute (use the fake clock idea from [system design](../../09-interview-playbook/system-design-basics/02-five-more-designs.md)) and returns `429` after that.
4. Override `current_user` in a test so every request acts as admin without sending a key.
5. Why is the response for an unknown path `404` with a JSON body, and how would you change its shape?
6. Explain the difference between `401` and `403` in your own words.

<details>
<summary>Solutions</summary>

1. ```python no-run
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
2. ```python no-run
   from fastapi import Query
   @app.get("/items")
   def list_items(limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0)):
       ids = sorted(ITEMS)[offset:offset + limit]
       return [ITEMS[i]["name"] for i in ids]
   print(client.get("/items?limit=500").status_code, client.get("/items?limit=1").status_code)
   # 422 200
   ```
3. ```python no-run
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
4. ```python no-run
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
