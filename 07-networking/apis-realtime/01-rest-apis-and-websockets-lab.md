# REST APIs, Server-Sent Events and WebSockets: A Hands-On Lab

**Prerequisites:** [HTTP from scratch](../dns-http/01-http-from-scratch.md), [sockets lab](../tcp-ip-osi/02-sockets-tcp-udp-lab.md), [cryptography lab](../tls-security/01-cryptography-and-tls-lab.md) (hashing). **You will learn (by building them on localhost):** the principles of **REST API design** (resources, methods, status codes, pagination, filtering, errors, versioning, idempotency, caching), a complete small **CRUD API** you can test, and the three ways a server can push data to a browser: **polling**, **Server-Sent Events (SSE)** and **WebSockets**, including the **WebSocket handshake and frame format implemented by hand**.

## 1. In plain words

An **API** (application programming interface) is how programs talk to each other. A **web API** exposes your data and operations over HTTP so a mobile app, a website or another service can use them. **REST** (Representational State Transfer) is the dominant *style* for designing them: model your data as **resources** with URLs, act on them with the standard HTTP **methods**, and let **status codes** and **headers** carry the meaning. Because it reuses what HTTP already gives you (caching, proxies, retries, auth), generic tools work with your API without custom knowledge.

## 2. REST principles in a table

| Principle | Meaning | Example |
|-----------|---------|---------|
| **Resources, not actions, in URLs** | nouns identify things | `/books/42`, not `/getBook?id=42` |
| **Methods carry the verb** | `GET` read, `POST` create, `PUT`/`PATCH` update, `DELETE` remove | `DELETE /books/42` |
| **Stateless** | each request has everything needed (auth token, ids); the server keeps no session between calls | scales by adding servers behind a [load balancer](../load-balancing-cdn/01-load-balancing-and-resilience-lab.md) |
| **Representations** | the same resource can be JSON, XML, ... chosen with `Accept` / `Content-Type` | `Accept: application/json` |
| **Standard status codes** | the number tells the outcome | `201 Created`, `404 Not Found`, `409 Conflict` |
| **Cacheable** | `GET` responses can carry `ETag` / `Cache-Control` | [HTTP lab](../dns-http/01-http-from-scratch.md) |
| **Uniform, predictable shape** | collections plural, nested for ownership, consistent errors | `/authors/7/books` |

### URL design cheat sheet

```text
GET    /books               list (supports ?page=2&limit=20&sort=-year&author=7)
POST   /books               create one          -> 201 Created + Location: /books/43
GET    /books/42            read one            -> 200 or 404
PUT    /books/42            replace the whole resource (idempotent)
PATCH  /books/42            change some fields
DELETE /books/42            remove              -> 204 No Content
GET    /authors/7/books     the books of author 7 (a sub-collection)
POST   /books/42/checkout   an action that is not CRUD: a verb sub-resource is acceptable when needed
```

Rules: **plural nouns**, lowercase, hyphens not underscores in paths, no verbs in the path for CRUD, no deep nesting beyond two levels, never put secrets in URLs (they land in logs).

## 3. A complete small API

Let us build a books API with `http.server` (no frameworks: the HTTP details stay visible). Real projects use FastAPI, Flask or Django REST framework, which handle the same things with less code.

```python
import http.server, threading, json, re, urllib.parse, hashlib

BOOKS = {
    1: {"id": 1, "title": "Dune", "author": "Herbert", "year": 1965},
    2: {"id": 2, "title": "Emma", "author": "Austen", "year": 1815},
    3: {"id": 3, "title": "Ulysses", "author": "Joyce", "year": 1922},
    4: {"id": 4, "title": "Neuromancer", "author": "Gibson", "year": 1984},
    5: {"id": 5, "title": "Hamlet", "author": "Shakespeare", "year": 1603},
}
STATE = {"next_id": 6, "idempotency": {}}

class Api(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def log_message(self, *args): pass

    # ---------- helpers ----------
    def reply(self, status, payload=None, headers=None):
        body = b"" if payload is None else json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if body and self.command != "HEAD":
            self.wfile.write(body)

    def error(self, status, code, message):
        self.reply(status, {"error": {"code": code, "message": message}})           # one consistent error shape

    def read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return None
        return data if isinstance(data, dict) else None

    def validate(self, data, partial=False):
        problems = {}
        for field, kind in (("title", str), ("author", str), ("year", int)):
            if field not in data:
                if not partial: problems[field] = "required"
            elif not isinstance(data[field], kind) or isinstance(data[field], bool):
                problems[field] = f"must be {kind.__name__}"
        if isinstance(data.get("year"), int) and not (0 < data["year"] < 3000):
            problems["year"] = "must be between 1 and 2999"
        return problems

    # ---------- routing ----------
    def route(self):
        url = urllib.parse.urlparse(self.path)
        match = re.fullmatch(r"/v1/books(?:/(\d+))?", url.path)
        return (match.group(1) and int(match.group(1))), bool(match), urllib.parse.parse_qs(url.query)

    def do_GET(self):
        book_id, ok, query = self.route()
        if not ok:
            return self.error(404, "not_found", "no such route")
        if book_id:
            book = BOOKS.get(book_id)
            if not book:
                return self.error(404, "not_found", f"book {book_id} does not exist")
            etag = '"' + hashlib.md5(json.dumps(book, sort_keys=True).encode()).hexdigest()[:8] + '"'
            if self.headers.get("If-None-Match") == etag:
                return self.reply(304, headers={"ETag": etag})                       # unchanged: send no body
            return self.reply(200, book, {"ETag": etag})
        items = list(BOOKS.values())
        if "author" in query:                                                        # filtering
            items = [b for b in items if b["author"].lower() == query["author"][0].lower()]
        sort = query.get("sort", ["id"])[0]                                          # sorting: ?sort=-year for descending
        key = sort.lstrip("-")
        if key not in ("id", "title", "year", "author"):
            return self.error(400, "bad_request", f"cannot sort by {key}")
        items.sort(key=lambda b: b[key], reverse=sort.startswith("-"))
        try:                                                                         # pagination
            limit = max(1, min(int(query.get("limit", ["2"])[0]), 100))
            page = max(1, int(query.get("page", ["1"])[0]))
        except ValueError:
            return self.error(400, "bad_request", "page and limit must be integers")
        start = (page - 1) * limit
        self.reply(200, {"data": items[start:start + limit], "page": page, "limit": limit, "total": len(items)},
                   {"X-Total-Count": str(len(items))})

    def do_POST(self):
        book_id, ok, _ = self.route()
        if not ok or book_id:
            return self.error(404, "not_found", "no such route")
        key = self.headers.get("Idempotency-Key")
        if key and key in STATE["idempotency"]:                                      # a retried request: replay the first response
            status, payload, headers = STATE["idempotency"][key]
            return self.reply(status, payload, headers)
        data = self.read_json()
        if data is None:
            return self.error(400, "bad_request", "body must be a JSON object")
        problems = self.validate(data)
        if problems:
            return self.reply(422, {"error": {"code": "validation_failed", "message": "invalid fields", "fields": problems}})
        book = {"id": STATE["next_id"], **{k: data[k] for k in ("title", "author", "year")}}
        STATE["next_id"] += 1
        BOOKS[book["id"]] = book
        headers = {"Location": f"/v1/books/{book['id']}"}
        if key:
            STATE["idempotency"][key] = (201, book, headers)
        self.reply(201, book, headers)

    def do_PATCH(self):
        book_id, ok, _ = self.route()
        if not ok or not book_id or book_id not in BOOKS:
            return self.error(404, "not_found", "no such book")
        data = self.read_json()
        if data is None:
            return self.error(400, "bad_request", "body must be a JSON object")
        problems = self.validate(data, partial=True)
        if problems:
            return self.reply(422, {"error": {"code": "validation_failed", "message": "invalid fields", "fields": problems}})
        BOOKS[book_id].update({k: v for k, v in data.items() if k in ("title", "author", "year")})
        self.reply(200, BOOKS[book_id])

    def do_DELETE(self):
        book_id, ok, _ = self.route()
        if not ok or not book_id or book_id not in BOOKS:
            return self.error(404, "not_found", "no such book")
        del BOOKS[book_id]
        self.reply(204)                                                              # success, nothing to return

server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Api)
PORT = server.server_address[1]
threading.Thread(target=server.serve_forever, daemon=True).start()
```

A tiny client helper, then the tour:

```python
import http.client

def call(method, path, body=None, headers=None):
    conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=3)
    payload = json.dumps(body) if isinstance(body, (dict, list)) else body
    conn.request(method, path, body=payload, headers={"Content-Type": "application/json", **(headers or {})})
    resp = conn.getresponse()
    raw = resp.read()
    conn.close()
    return resp.status, (json.loads(raw) if raw else None), dict(resp.getheaders())

status, body, _ = call("GET", "/v1/books/1")
print(status, body)                                          # 200 {'id': 1, 'title': 'Dune', 'author': 'Herbert', 'year': 1965}
print(call("GET", "/v1/books/99")[:2])                       # (404, {'error': {'code': 'not_found', 'message': 'book 99 does not exist'}})
```

### Collections: pagination, filtering and sorting

Never return an unbounded list. Use **pagination** and give the client the metadata to continue.

```python
status, body, headers = call("GET", "/v1/books?limit=2&page=1&sort=year")
print(status, [b["title"] for b in body["data"]], body["total"], headers["X-Total-Count"])
# 200 ['Hamlet', 'Emma'] 5 5                                  oldest two books
print([b["title"] for b in call("GET", "/v1/books?limit=2&page=3&sort=year")[1]["data"]])        # ['Neuromancer']       the last page has a single item
print([b["title"] for b in call("GET", "/v1/books?author=joyce")[1]["data"]])                     # ['Ulysses']
print(call("GET", "/v1/books?sort=price")[:2])               # (400, {'error': {'code': 'bad_request', 'message': 'cannot sort by price'}})
```

| Pagination style | How | Good for | Weakness |
|------------------|-----|----------|----------|
| **Offset/page** (`?page=3&limit=20`) | skip `(page-1)*limit` rows | simple UIs, random page access | slow for huge offsets; items shift if data changes while paging |
| **Cursor/keyset** (`?after=<id>&limit=20`) | `WHERE id > :after ORDER BY id LIMIT 20` | feeds, infinite scroll, big tables | no jumping to page N |

### Creating, validating, updating, deleting

```python
new = {"title": "Dracula", "author": "Stoker", "year": 1897}
status, body, headers = call("POST", "/v1/books", new)
print(status, body["id"], headers["Location"])               # 201 6 /v1/books/6          Created, with the new resource's URL in Location

print(call("POST", "/v1/books", {"title": "No year", "author": "X"})[:2])
# (422, {'error': {'code': 'validation_failed', 'message': 'invalid fields', 'fields': {'year': 'required'}}})
print(call("POST", "/v1/books", {"title": "Bad", "author": "X", "year": "1897"})[1]["error"]["fields"])      # {'year': 'must be int'}
print(call("POST", "/v1/books", "not json")[:2])             # (400, {'error': {'code': 'bad_request', 'message': 'body must be a JSON object'}})

print(call("PATCH", "/v1/books/6", {"year": 1898})[:2])      # (200, {'id': 6, 'title': 'Dracula', 'author': 'Stoker', 'year': 1898})
print(call("DELETE", "/v1/books/6")[:2])                     # (204, None)
print(call("GET", "/v1/books/6")[0])                         # 404
```

Status code choices that trip people up:

| Situation | Code |
|-----------|------|
| Created something | `201` + `Location` header |
| Success, nothing to return (delete, some updates) | `204` |
| Malformed request (bad JSON, bad parameter) | `400` |
| Not logged in | `401` (really "unauthenticated") |
| Logged in but not allowed | `403` |
| Not found | `404` |
| Conflicts with current state (duplicate, stale version) | `409` |
| Well-formed but invalid data | `422` (many APIs use `400`; be consistent) |
| Too many requests | `429` + `Retry-After` |
| Your bug | `500`; temporary overload `503` |

### Idempotency: safe retries for POST

`GET`, `PUT` and `DELETE` are naturally idempotent; **`POST` is not**, so a retry after a timeout can create a duplicate. Clients send an **`Idempotency-Key`** header; the server remembers the first result and replays it (the [transactions lab](../../05-databases/transactions-acid/01-transactions-lab.md) shows the database side).

```python
key = {"Idempotency-Key": "order-7f3a"}
first = call("POST", "/v1/books", {"title": "Carmilla", "author": "Le Fanu", "year": 1872}, key)
second = call("POST", "/v1/books", {"title": "Carmilla", "author": "Le Fanu", "year": 1872}, key)       # a retry
print(first[0], second[0], first[1]["id"] == second[1]["id"])                                           # 201 201 True       same book: not created twice
print(len(call("GET", "/v1/books?limit=100")[1]["data"]))                                              # 6                   five originals plus one Carmilla
```

### Conditional requests and caching

`GET /v1/books/1` returns an `ETag`; the client sends it back as `If-None-Match` and gets a body-less `304`:

```python
status, _, headers = call("GET", "/v1/books/1")
etag = headers["ETag"]
print(call("GET", "/v1/books/1", headers={"If-None-Match": etag})[0])                                    # 304
call("PATCH", "/v1/books/1", {"year": 1966})                                                              # the resource changes ...
print(call("GET", "/v1/books/1", headers={"If-None-Match": etag})[0])                                    # 200   ... so the old ETag no longer matches
```

The same `ETag` can protect **updates** (`If-Match` on `PUT`/`PATCH`; mismatch gives `412 Precondition Failed`), the HTTP form of the [optimistic locking](../../05-databases/transactions-acid/01-transactions-lab.md) idea.

## 4. API design checklist

1. **Versioning:** put it in the path (`/v1/...`) or a header; never break existing clients; deprecate with notice.
2. **Consistent errors:** machine-readable `code`, human `message`, field-level details (as above).
3. **Authentication and authorization:** send tokens in the `Authorization: Bearer <token>` header (never in URLs), over HTTPS only; check **permissions per resource** (a user may read only their own orders: otherwise anyone can enumerate `/orders/1`, `/orders/2`... which is the classic **IDOR** bug).
4. **Rate limiting** with `429` and `Retry-After` ([token bucket](../load-balancing-cdn/01-load-balancing-and-resilience-lab.md)).
5. **Input validation** on the server for every field; limits on body size and page size.
6. **Idempotency keys** for payments and other non-idempotent POSTs.
7. **Don't leak internals:** no stack traces, no database ids if they reveal counts, stable public identifiers.
8. **Document it:** OpenAPI (Swagger) describes endpoints and generates docs, clients and tests.
9. **Design for evolution:** adding optional fields is safe; renaming or removing is breaking.
10. **Choose the right style:** REST for resources; **GraphQL** when clients need to choose fields and avoid many round trips; **gRPC** (HTTP/2 plus Protocol Buffers) for fast service-to-service calls; **webhooks** to let servers call *you* when something happens.

## 5. Pushing data to clients: polling, SSE, WebSockets

HTTP is request/response: the **client** speaks first. For live data (chat, notifications, prices) the server needs to push. Options:

| Technique | How it works | Direction | Good for | Cost |
|-----------|--------------|-----------|----------|------|
| **Polling** | client asks every N seconds | client to server | simple, infrequent updates | wasteful; latency up to N seconds |
| **Long polling** | server holds the request open until there is news | client to server | older pushes | many open requests |
| **Server-Sent Events (SSE)** | one long HTTP response the server keeps writing to (`text/event-stream`) | **server to client** | notifications, feeds, progress bars, LLM token streaming | one-way; text only |
| **WebSocket** | after an HTTP **upgrade**, the TCP connection becomes a persistent **two-way** message channel | **both ways** | chat, multiplayer games, collaborative editing, live trading | stateful connections to manage and scale |

### Server-Sent Events

The server answers with `Content-Type: text/event-stream` and never closes; each event is a few text lines ending with a blank line. Browsers reconnect automatically (`EventSource`).

```python
class SSEHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def log_message(self, *args): pass
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()
        for i in range(1, 4):
            self.wfile.write(f"id: {i}\nevent: tick\ndata: {json.dumps({'n': i})}\n\n".encode())       # one event = lines + a blank line
            self.wfile.flush()

sse_server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), SSEHandler)
threading.Thread(target=sse_server.serve_forever, daemon=True).start()

conn = http.client.HTTPConnection("127.0.0.1", sse_server.server_address[1], timeout=3)
conn.request("GET", "/stream")
resp = conn.getresponse()
raw = resp.read().decode()                                    # a real client reads incrementally; here the stream ends after 3 events
events = [dict(line.split(": ", 1) for line in block.splitlines()) for block in raw.strip().split("\n\n")]
print(resp.getheader("Content-Type"), events)
# text/event-stream [{'id': '1', 'event': 'tick', 'data': '{"n": 1}'}, {'id': '2', 'event': 'tick', 'data': '{"n": 2}'}, {'id': '3', 'event': 'tick', 'data': '{"n": 3}'}]
conn.close(); sse_server.shutdown(); sse_server.server_close()
```

Browser side: `new EventSource("/stream").onmessage = e => console.log(e.data)`. If the connection drops, the browser reconnects and sends `Last-Event-ID` so the server can resume. SSE is the simplest choice whenever data flows **only from server to browser**.

## 6. WebSockets: how they really work

A WebSocket starts as an ordinary HTTP request asking to **upgrade**; after the server agrees, the same TCP connection speaks a lightweight **frame protocol** in both directions with very little overhead per message.

### The handshake

```text
Client -> Server:   GET /chat HTTP/1.1
                    Host: example.com
                    Upgrade: websocket
                    Connection: Upgrade
                    Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==     (random 16 bytes, base64)
                    Sec-WebSocket-Version: 13

Server -> Client:   HTTP/1.1 101 Switching Protocols
                    Upgrade: websocket
                    Connection: Upgrade
                    Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=   (proof the server understood)
```

The server proves it is a real WebSocket server by hashing the client's key with a fixed magic string:

```python
import base64

MAGIC = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"                # fixed by the protocol (RFC 6455)

def accept_key(client_key: str) -> str:
    return base64.b64encode(hashlib.sha1((client_key + MAGIC).encode()).digest()).decode()

print(accept_key("dGhlIHNhbXBsZSBub25jZQ=="))                 # s3pPLMBiTxaQ9kYGzzhZRbK+xOo=       the exact value from the RFC's own example
```

### The frame format

After the upgrade, data travels in **frames**:

```text
 byte 0:  FIN (1 bit: last fragment) | RSV (3 bits) | opcode (4 bits)
              opcode: 0x1 text, 0x2 binary, 0x8 close, 0x9 ping, 0xA pong
 byte 1:  MASK (1 bit: client-to-server frames MUST be masked) | payload length (7 bits)
              length 0-125 in these 7 bits; 126 means the next 2 bytes hold the length; 127 means the next 8 bytes do
 [mask key: 4 bytes, only if MASK = 1]
 payload (XORed with the repeating mask key when masked)
```

Clients mask payloads with a random key (a defense against cache-poisoning proxies); servers do not.

```python
import os, struct

def encode_frame(payload: bytes, opcode=0x1, mask=False) -> bytes:
    header = bytes([0x80 | opcode])                            # FIN = 1: a complete message in one frame
    n = len(payload)
    mask_bit = 0x80 if mask else 0
    if n < 126:
        header += bytes([mask_bit | n])
    elif n < 65536:
        header += bytes([mask_bit | 126]) + struct.pack("!H", n)
    else:
        header += bytes([mask_bit | 127]) + struct.pack("!Q", n)
    if mask:
        key = os.urandom(4)
        payload = bytes(b ^ key[i % 4] for i, b in enumerate(payload))      # XOR each byte with the repeating key
        header += key
    return header + payload

def read_exactly(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("closed")
        data += chunk
    return data

def read_frame(sock):
    b0, b1 = read_exactly(sock, 2)
    opcode, masked, n = b0 & 0x0F, bool(b1 & 0x80), b1 & 0x7F
    if n == 126:
        (n,) = struct.unpack("!H", read_exactly(sock, 2))
    elif n == 127:
        (n,) = struct.unpack("!Q", read_exactly(sock, 8))
    key = read_exactly(sock, 4) if masked else None
    payload = read_exactly(sock, n)
    if masked:
        payload = bytes(b ^ key[i % 4] for i, b in enumerate(payload))
    return opcode, payload

print(encode_frame(b"Hello").hex())                            # 810548656c6c6f      FIN+text, length 5, then "Hello"
print(len(encode_frame(b"x" * 200)), len(encode_frame(b"x" * 70000)))      # 204 70010          2+2 header bytes at 200, 2+8 at 70000
```

Only **2 bytes of overhead** for a short message, versus hundreds of bytes of HTTP headers on every request: that is why WebSockets suit frequent small messages.

### A working echo server and client

```python
import socket

def ws_server(ready, stop):
    with socket.socket() as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", 0)); srv.listen()
        ready.append(srv.getsockname()[1]); srv.settimeout(0.2)
        while not stop.is_set():
            try:
                conn, _ = srv.accept()
            except socket.timeout:
                continue
            with conn:
                request = b""
                while b"\r\n\r\n" not in request:
                    request += conn.recv(1024)
                headers = dict(line.split(": ", 1) for line in request.decode().split("\r\n")[1:] if ": " in line)
                conn.sendall(("HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                              f"Sec-WebSocket-Accept: {accept_key(headers['Sec-WebSocket-Key'])}\r\n\r\n").encode())
                try:
                    while True:
                        opcode, payload = read_frame(conn)
                        if opcode == 0x8:                       # close frame: reply and stop
                            conn.sendall(encode_frame(b"", opcode=0x8)); break
                        if opcode == 0x9:                       # ping: answer with pong carrying the same data
                            conn.sendall(encode_frame(payload, opcode=0xA)); continue
                        conn.sendall(encode_frame(b"echo: " + payload))          # server frames are not masked
                except ConnectionError:
                    pass

ready, stop = [], threading.Event()
ws_thread = threading.Thread(target=ws_server, args=(ready, stop)); ws_thread.start()
while not ready: pass

sock = socket.create_connection(("127.0.0.1", ready[0]))
client_key = base64.b64encode(os.urandom(16)).decode()
sock.sendall((f"GET /chat HTTP/1.1\r\nHost: localhost\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
              f"Sec-WebSocket-Key: {client_key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
response = b""
while b"\r\n\r\n" not in response:
    response += sock.recv(1024)
status_line = response.split(b"\r\n")[0].decode()
accept = [l for l in response.decode().split("\r\n") if l.startswith("Sec-WebSocket-Accept")][0].split(": ")[1]
print(status_line, accept == accept_key(client_key))           # HTTP/1.1 101 Switching Protocols True    the client verifies the server's proof

for text in ("hello", "second message", "x" * 300):
    sock.sendall(encode_frame(text.encode(), mask=True))        # client frames MUST be masked
    opcode, payload = read_frame(sock)
    print(opcode, payload[:30], len(payload))
# 1 b'echo: hello' 11
# 1 b'echo: second message' 20
# 1 b'echo: xxxxxxxxxxxxxxxxxxxxxxxxx' 306

sock.sendall(encode_frame(b"ping!", opcode=0x9, mask=True))
print(read_frame(sock))                                         # (10, b'ping!')       opcode 0xA = pong
sock.sendall(encode_frame(b"", opcode=0x8, mask=True))
print(read_frame(sock)[0])                                      # 8                      the server confirms the close
sock.close(); stop.set(); ws_thread.join()
```

Both directions now exchange messages on **one persistent connection**. Notice **ping/pong**: either side can check the other is alive (important through proxies that drop idle connections), and the **close handshake** ends cleanly.

### Using WebSockets in real projects

You will use a library: Python `websockets` or FastAPI/Starlette WebSockets, Node `ws`/Socket.IO, and in the browser the built-in `new WebSocket("wss://example.com/chat")`.

```python
# the server side of a chat room with the `websockets` library (pip install websockets), for reference
#   async def handler(websocket):
#       connected.add(websocket)
#       try:
#           async for message in websocket:
#               for peer in connected:
#                   if peer is not websocket:
#                       await peer.send(message)
#       finally:
#           connected.discard(websocket)
```

**Scaling considerations:** each WebSocket is a long-lived TCP connection holding memory, so a server holds tens of thousands at once (use `asyncio`/an event loop, not a thread per connection); a [load balancer](../load-balancing-cdn/01-load-balancing-and-resilience-lab.md) must support the `Upgrade` and use sticky routing or a shared **pub/sub** backend (Redis) so a message sent to one server reaches clients connected to another; use **heartbeats** (ping/pong), **reconnect with backoff and jitter**, authenticate during the handshake (token in a header or first message, not in a logged URL), use `wss://` (TLS) always, and validate and size-limit every message.

## 7. Which one should I use?

| Need | Choose |
|------|--------|
| Standard create/read/update/delete over resources | **REST** |
| Clients need flexible field selection and fewer round trips | GraphQL |
| Fast typed service-to-service calls | gRPC |
| Notify clients of server events, one direction (live scores, progress, LLM streaming) | **SSE** (simplest) |
| Two-way low-latency messages (chat, games, collaborative editing) | **WebSocket** |
| The server must call another system when something happens | **webhook** (an HTTP POST to a URL the other party registered; verify it with an [HMAC signature](../tls-security/01-cryptography-and-tls-lab.md)) |
| Rare updates, simplest thing that works | polling |

## 8. Two real-world examples

**Example 1: A payments API.** `POST /v1/charges` with an `Idempotency-Key`, `422` with field errors on bad input, `429` with `Retry-After` under load, versioned URLs so old clients keep working for years, and signed webhooks to tell your server the charge succeeded. Every rule of this lesson shows up in a production API.

**Example 2: A collaborative whiteboard.** Each stroke is sent over a WebSocket as a few bytes; the server broadcasts it to the room (via Redis pub/sub so every server instance reaches its clients). When the connection drops, the client reconnects with backoff and asks the server for strokes since its last sequence number: the same "resume from `Last-Event-ID`" idea as SSE.

## 9. Common mistakes

- Verbs in URLs for plain CRUD (`/createBook`), or inconsistent plural/singular naming.
- Returning `200` with an error in the body, or `500` for bad client input.
- Unpaginated collection endpoints (one request can return a million rows).
- Authorization checked only at login, not per resource (**IDOR**: guessing `/orders/1001`).
- Putting tokens or secrets in query strings.
- Retrying `POST` without idempotency keys, or breaking clients by renaming fields without versioning.
- Using WebSockets when SSE or polling would do (more moving parts to scale).
- Forgetting heartbeats, reconnect logic and message size limits on WebSockets.
- Trusting browser `Origin` as authentication (check it, but also authenticate).

## 10. Practice

1. Design the REST endpoints for a **todo app** with users, lists and tasks (list, create, mark done, delete, tasks of one list).
2. Which status code for each: (a) updating a book that does not exist, (b) creating a duplicate username, (c) missing required field, (d) deleting successfully, (e) wrong password?
3. Use `call` to fetch the second page (size 2) of books sorted by title.
4. Why must `POST /payments` accept an `Idempotency-Key`? What does the server store?
5. Compute the exact bytes of a masked-free text frame carrying `"Hi"`.
6. When would you pick SSE over WebSocket?
7. Why does the WebSocket server hash the key with a magic string, and what does that prove?

<details>
<summary>Solutions</summary>

1. ```text
   GET    /v1/lists                      GET    /v1/lists/{id}/tasks?done=false
   POST   /v1/lists                      POST   /v1/lists/{id}/tasks            -> 201
   PATCH  /v1/tasks/{id}  {"done":true}  DELETE /v1/tasks/{id}                  -> 204
   ```
   (User scoping comes from the auth token, not from the URL: `GET /v1/lists` returns the caller's lists.)
2. (a) `404`, (b) `409` Conflict (or `422`), (c) `422` (or `400`), (d) `204`, (e) `401`.
3. ```python
   print([b["title"] for b in call("GET", "/v1/books?limit=2&page=2&sort=title")[1]["data"]])      # ['Emma', 'Hamlet']   (titles sorted: Carmilla, Dune, Emma, Hamlet, ...)
   ```
   Note: with the 6 books present (including Carmilla) page 1 is `Carmilla, Dune` and page 2 is `Emma, Hamlet`.
4. Because a network failure can make the client retry a request that actually succeeded; the server stores the key with the first response and returns it again instead of charging twice.
5. ```python
   print(encode_frame(b"Hi").hex())                               # 81024869      0x81 = FIN + text opcode, 0x02 = length 2, then 'H' 'i'
   ```
6. When data flows only server to client (notifications, progress, live feed, streamed text): SSE is plain HTTP, reconnects automatically, and works through most proxies, with no custom protocol.
7. It proves the server understood the WebSocket protocol (a plain HTTP server would not know to compute it), guarding against accidentally upgrading a connection to a server that does not speak it; it is *not* authentication or encryption (use `wss://` and tokens for that).

</details>

## 11. Check yourself

1. List five REST design principles.
2. What is the difference between `PUT` and `PATCH`, and which are idempotent?
3. Offset versus cursor pagination: when each?
4. How does SSE differ from WebSocket?
5. What happens during the WebSocket handshake?
6. Why are client-to-server WebSocket frames masked?
7. Name three things a production WebSocket service needs beyond sending messages.

<details>
<summary>Answers</summary>

1. Resources as nouns in URLs, HTTP methods as verbs, stateless requests, standard status codes, consistent representations and errors (also cacheability, versioning, pagination).
2. `PUT` replaces the whole resource; `PATCH` changes some fields. `PUT` is idempotent; `PATCH` may or may not be.
3. Offset for small collections and random page access; cursor (keyset) for large or changing data and infinite scroll.
4. SSE is one-way (server to client) over a plain HTTP response with automatic reconnect; WebSocket is a two-way, upgraded persistent connection with its own frame protocol.
5. The client sends an HTTP `Upgrade: websocket` request with a random `Sec-WebSocket-Key`; the server replies `101 Switching Protocols` with `Sec-WebSocket-Accept` (SHA-1 of key + magic string, base64), after which both sides exchange frames.
6. The mask (a random 4-byte XOR key) stops malicious scripts from crafting bytes that confuse intermediary proxies into caching or misreading them.
7. Heartbeats (ping/pong), reconnect with backoff and resume, authentication, size and rate limits, pub/sub for multi-server fan-out, TLS (`wss://`).

</details>

## 12. Clean up

```python
server.shutdown(); server.server_close()
print("servers stopped")                                          # servers stopped
```

[Back to networking](../README.md)
