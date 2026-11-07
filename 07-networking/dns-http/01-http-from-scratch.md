# HTTP from Scratch: Requests, Responses, Caching and a Tiny Server

**Prerequisites:** [sockets lab](../tcp-ip-osi/02-sockets-tcp-udp-lab.md), [DNS and HTTP overview](README.md). **You will learn (by running a real local server):** what an **HTTP request and response** look like on the wire, **methods**, **status codes**, **headers**, **keep-alive**, **caching with ETags**, **cookies**, content negotiation, and you will write your own **mini web server** with sockets. Everything runs on `localhost`.

## 1. In plain words

**HTTP** (HyperText Transfer Protocol) is the language browsers and servers speak. It is **text**, **request/response** based, and **stateless** (each request stands alone; the server does not remember you unless you send something like a cookie).

```text
Client                                  Server
  |------- request: "GET /hello" ------->|
  |<------ response: 200 + body ---------|
```

HTTP usually runs on top of **TCP** (port 80), and **HTTPS** is HTTP inside **TLS** (port 443). HTTP/3 runs over QUIC (UDP), but the *meaning* of requests and responses is the same.

## 2. A local server to experiment with

We use Python's built-in `http.server` in a background thread. It serves a few routes we define, including one that counts requests and one that supports caching.

```python
import http.server, threading, json, hashlib, time, socket

hits = {"count": 0}

class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"                      # enables keep-alive (persistent connections)

    def log_message(self, *args):                       # keep the output quiet
        pass

    def _send(self, status, body=b"", headers=None, content_type="text/plain; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_GET(self):
        if self.path == "/hello":
            self._send(200, b"Hello, HTTP!")
        elif self.path == "/count":
            hits["count"] += 1
            self._send(200, str(hits["count"]).encode())
        elif self.path == "/data.json":
            self._send(200, json.dumps({"items": [1, 2, 3]}).encode(), content_type="application/json")
        elif self.path == "/cached":
            body = b"Expensive content that rarely changes"
            etag = '"' + hashlib.md5(body).hexdigest()[:8] + '"'
            if self.headers.get("If-None-Match") == etag:
                self._send(304, headers={"ETag": etag})            # "Not Modified": no body is sent
            else:
                self._send(200, body, headers={"ETag": etag, "Cache-Control": "max-age=60"})
        elif self.path == "/redirect":
            self._send(302, headers={"Location": "/hello"})
        elif self.path == "/login":
            self._send(200, b"logged in", headers={"Set-Cookie": "session=abc123; HttpOnly; Path=/"})
        elif self.path == "/whoami":
            cookie = self.headers.get("Cookie", "")
            self._send(200, ("hello " + ("user 42" if "session=abc123" in cookie else "stranger")).encode())
        else:
            self._send(404, b"Not Found")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        payload = self.rfile.read(length)
        try:
            data = json.loads(payload)
            self._send(201, json.dumps({"received": data, "id": 7}).encode(), content_type="application/json",
                       headers={"Location": "/items/7"})
        except json.JSONDecodeError:
            self._send(400, b"invalid JSON")

    def do_PUT(self):
        self._send(204)                                     # "No Content": success with no body

    def do_DELETE(self):
        self._send(204)

server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
PORT = server.server_address[1]
threading.Thread(target=server.serve_forever, daemon=True).start()
print(PORT > 1023)                                         # True
```

## 3. Speak HTTP by hand over a raw socket

An HTTP/1.1 request is lines of text ending in `\r\n`, with a **blank line** after the headers:

```python
def raw_request(request_text: str) -> bytes:
    with socket.create_connection(("127.0.0.1", PORT), timeout=2) as s:
        s.sendall(request_text.encode())
        chunks = []
        while data := s.recv(4096):
            chunks.append(data)
        return b"".join(chunks)

request = (
    "GET /hello HTTP/1.1\r\n"
    f"Host: 127.0.0.1:{PORT}\r\n"
    "Connection: close\r\n"                                 # ask the server to close after this response so recv() ends
    "\r\n"
)
print(raw_request(request).decode())
# HTTP/1.1 200 OK
# Server: BaseHTTP Python/3.15.1
# Date: Sat, 07 Nov 2026 10:00:00 GMT
# Content-Type: text/plain; charset=utf-8
# Content-Length: 12
#
# Hello, HTTP!
```

### Anatomy

```text
REQUEST                                   RESPONSE
GET /hello HTTP/1.1          <- request line    HTTP/1.1 200 OK            <- status line
Host: example.com            <- headers         Content-Type: text/plain   <- headers
Accept: text/html                               Content-Length: 12
(blank line)                                    (blank line)
(optional body)                                 Hello, HTTP!               <- body
```

- **Request line:** method, path (and query), HTTP version.
- **`Host` header** is mandatory in HTTP/1.1: one IP can serve many sites, and the server needs the name to choose.
- **`Content-Length`** (or chunked encoding) tells the receiver where the body ends: the framing problem from the socket lab.
- Lines end with `\r\n`; the blank line ends the headers.

A small parser shows how simple the format is:

```python
def parse_response(raw: bytes):
    head, _, body = raw.partition(b"\r\n\r\n")
    lines = head.decode().split("\r\n")
    version, status, reason = lines[0].split(" ", 2)
    headers = {k.lower(): v for k, v in (line.split(": ", 1) for line in lines[1:])}
    return int(status), reason, headers, body

status, reason, headers, body = parse_response(raw_request(request))
print(status, reason, headers["content-type"], headers["content-length"], body)
# 200 OK text/plain; charset=utf-8 12 b'Hello, HTTP!'
```

## 4. Using a real client library

You rarely write raw requests; the standard library's `http.client` (and third-party `requests`/`httpx`) do it:

```python
import http.client

conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=2)
conn.request("GET", "/data.json")
resp = conn.getresponse()
print(resp.status, resp.reason, resp.getheader("Content-Type"))     # 200 OK application/json
print(json.loads(resp.read()))                                      # {'items': [1, 2, 3]}
conn.close()
```

## 5. Methods

| Method | Meaning | Safe? | Idempotent? | Has body? |
|--------|---------|-------|-------------|-----------|
| **GET** | read a resource | yes | yes | no |
| **HEAD** | like GET but headers only | yes | yes | no |
| **POST** | create / perform an action | no | **no** | yes |
| **PUT** | replace a resource entirely | no | yes | yes |
| **PATCH** | modify part of a resource | no | not necessarily | yes |
| **DELETE** | remove a resource | no | yes | rarely |
| **OPTIONS** | what is allowed (CORS preflight) | yes | yes | no |

- **Safe** = does not change server state (so crawlers and prefetchers may call it). Never delete data on a GET.
- **Idempotent** = repeating the request has the same effect as doing it once (so it is safe to retry after a timeout). PUT and DELETE are; **POST is not** (a retry can create a duplicate: use idempotency keys).

```python
def request(method, path, body=None, headers=None):
    conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=2)
    conn.request(method, path, body=body, headers=headers or {})
    resp = conn.getresponse()
    data = resp.read()
    conn.close()
    return resp.status, resp.getheader("Location"), data

print(request("POST", "/items", body=json.dumps({"name": "pen"}), headers={"Content-Type": "application/json"}))
# (201, '/items/7', b'{"received": {"name": "pen"}, "id": 7}')
print(request("POST", "/items", body="not json"))           # (400, None, b'invalid JSON')
print(request("PUT", "/items/7", body="x"))                 # (204, None, b'')
print(request("DELETE", "/items/7"))                        # (204, None, b'')
print(request("GET", "/nothing-here"))                      # (404, None, b'Not Found')
```

## 6. Status codes

The first digit is the class:

| Class | Meaning | Common codes |
|-------|---------|--------------|
| **1xx** | informational | 101 Switching Protocols (WebSocket upgrade) |
| **2xx** | success | **200** OK, **201** Created, **204** No Content |
| **3xx** | redirection | **301** Moved Permanently, **302** Found, **304** Not Modified |
| **4xx** | **client** error | **400** Bad Request, **401** Unauthorized (really "unauthenticated"), **403** Forbidden, **404** Not Found, **409** Conflict, **422** Unprocessable, **429** Too Many Requests |
| **5xx** | **server** error | **500** Internal Server Error, **502** Bad Gateway, **503** Service Unavailable, **504** Gateway Timeout |

Rule of thumb: **4xx means "you did something wrong, do not retry unchanged"**; **5xx means "I failed, retrying later may work"**.

```python
import http

for code in (200, 301, 404, 429, 503):
    print(code, http.HTTPStatus(code).phrase)
# 200 OK
# 301 Moved Permanently
# 404 Not Found
# 429 Too Many Requests
# 503 Service Unavailable
```

**Redirects:** a 3xx response carries a `Location` header; clients follow it automatically (`curl -L`, browsers):

```python
print(request("GET", "/redirect"))                          # (302, '/hello', b'')    (a client would now request /hello)
```

## 7. Headers worth knowing

| Header | Direction | Purpose |
|--------|-----------|---------|
| `Host` | request | which site (virtual hosting) |
| `User-Agent` | request | who is asking |
| `Accept`, `Accept-Language`, `Accept-Encoding` | request | **content negotiation**: preferred types, languages, `gzip` |
| `Authorization` | request | credentials (`Bearer <token>`) |
| `Content-Type`, `Content-Length` | both | what the body is and how long it is |
| `Cache-Control`, `ETag`, `Last-Modified` | response | caching rules and validators |
| `If-None-Match`, `If-Modified-Since` | request | conditional requests |
| `Set-Cookie` / `Cookie` | response / request | state across stateless requests |
| `Location` | response | where to go next (redirects, created resources) |
| `Retry-After` | response | when to try again (429/503) |

## 8. Keep-alive: reuse the connection

Opening a TCP connection costs a handshake (and TLS adds more). **HTTP/1.1 keeps connections open by default**, so several requests share one connection; HTTP/2 additionally multiplexes many requests at once over one connection.

```python
conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=2)
for _ in range(3):
    conn.request("GET", "/hello")
    conn.getresponse().read()                               # you must read the full body before reusing the connection
print(conn.sock is not None)                                # True   (the same TCP connection served all three requests)
conn.close()

def time_requests(reuse, n=200):
    start = time.perf_counter()
    if reuse:
        c = http.client.HTTPConnection("127.0.0.1", PORT)
        for _ in range(n):
            c.request("GET", "/hello"); c.getresponse().read()
        c.close()
    else:
        for _ in range(n):
            c = http.client.HTTPConnection("127.0.0.1", PORT)
            c.request("GET", "/hello"); c.getresponse().read(); c.close()
    return time.perf_counter() - start

print(time_requests(True) < time_requests(False))           # True   (even on loopback, avoiding new connections is faster; on the real internet far more so)
```

Libraries expose this as sessions or connection pools (`requests.Session()`, `httpx.Client()`): create **one client** and reuse it.

## 9. Caching: the fastest request is the one never made

Two mechanisms:

1. **Freshness:** `Cache-Control: max-age=60` lets the client reuse its copy for 60 seconds with **no request at all**.
2. **Validation:** after it expires, the client asks "has it changed?" with `If-None-Match: <etag>`. If not, the server replies **304 Not Modified** with **no body**, saving bandwidth.

```python
status, _, headers, body = parse_response(raw_request(
    f"GET /cached HTTP/1.1\r\nHost: x\r\nConnection: close\r\n\r\n"))
etag = headers["etag"]
print(status, etag, headers["cache-control"], len(body))
# 200 "<8 hex chars>" max-age=60 37

status2, _, headers2, body2 = parse_response(raw_request(
    f"GET /cached HTTP/1.1\r\nHost: x\r\nIf-None-Match: {etag}\r\nConnection: close\r\n\r\n"))
print(status2, len(body2))                                  # 304 0     (the server confirms the copy is current and sends no body)
```

Directives: `no-store` (never cache: sensitive data), `no-cache` (cache but always revalidate), `private` (only the browser, not shared caches), `public`, `immutable` (never changes: use with hashed filenames such as `app.3f9c1.js`).

## 10. Cookies: remembering you

HTTP is stateless; the server gives you a token in `Set-Cookie` and the browser sends it back in `Cookie` on later requests to that site. Login sessions work this way.

```python
status, _, headers, _ = parse_response(raw_request("GET /login HTTP/1.1\r\nHost: x\r\nConnection: close\r\n\r\n"))
cookie = headers["set-cookie"]
print(cookie)                                               # session=abc123; HttpOnly; Path=/
session_cookie = cookie.split(";")[0]

print(parse_response(raw_request("GET /whoami HTTP/1.1\r\nHost: x\r\nConnection: close\r\n\r\n"))[3])         # b'hello stranger'
print(parse_response(raw_request(f"GET /whoami HTTP/1.1\r\nHost: x\r\nCookie: {session_cookie}\r\nConnection: close\r\n\r\n"))[3])      # b'hello user 42'
```

Cookie attributes that matter for security: **`HttpOnly`** (JavaScript cannot read it, limits XSS theft), **`Secure`** (only over HTTPS), **`SameSite=Lax/Strict`** (limits cross-site sending, defends against CSRF), `Max-Age`/`Expires`, `Path`, `Domain`.

## 11. Build your own tiny web server with sockets

To demystify everything: a server in about 40 lines that parses requests and routes them.

```python
def tiny_server(ready, stop):
    routes = {"/": b"<h1>Home</h1>", "/about": b"<p>About us</p>"}
    with socket.socket() as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", 0)); srv.listen()
        ready.append(srv.getsockname()[1])
        srv.settimeout(0.2)
        while not stop.is_set():
            try:
                conn, _ = srv.accept()
            except socket.timeout:
                continue
            with conn:
                data = b""
                while b"\r\n\r\n" not in data:                 # read until the end of the headers
                    chunk = conn.recv(1024)
                    if not chunk:
                        break
                    data += chunk
                request_line = data.split(b"\r\n")[0].decode()
                try:
                    method, path, _version = request_line.split(" ")
                except ValueError:
                    conn.sendall(b"HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
                    continue
                if method != "GET":
                    status, body = "405 Method Not Allowed", b"only GET"
                elif path in routes:
                    status, body = "200 OK", routes[path]
                else:
                    status, body = "404 Not Found", b"no such page"
                conn.sendall((f"HTTP/1.1 {status}\r\nContent-Type: text/html\r\n"
                              f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n").encode() + body)

ready, stop = [], threading.Event()
t = threading.Thread(target=tiny_server, args=(ready, stop)); t.start()
while not ready: pass
tiny_port = ready[0]

def fetch(path, method="GET"):
    conn = http.client.HTTPConnection("127.0.0.1", tiny_port, timeout=2)
    conn.request(method, path)
    r = conn.getresponse()
    out = (r.status, r.read())
    conn.close()
    return out

print(fetch("/"), fetch("/about"))                          # (200, b'<h1>Home</h1>') (200, b'<p>About us</p>')
print(fetch("/missing"), fetch("/", method="DELETE"))       # (404, b'no such page') (405, b'only GET')
stop.set(); t.join()
```

Real servers (nginx, Gunicorn, Uvicorn) do the same job with robust parsing, concurrency, timeouts and security hardening; web frameworks (Flask, FastAPI, Django) sit on top and turn the parsed request into a function call.

## 12. HTTP versions at a glance

| Version | Key idea |
|---------|----------|
| **HTTP/1.0** | one request per connection |
| **HTTP/1.1** | keep-alive, `Host` header, chunked transfer; head-of-line blocking (one response at a time per connection) |
| **HTTP/2** | **multiplexing** many requests over one connection, binary framing, header compression (HPACK) |
| **HTTP/3** | HTTP/2 semantics over **QUIC** (UDP): no TCP head-of-line blocking, faster connection setup and migration |

## 13. Two real-world examples

**Example 1: REST APIs.** A mobile app calls `GET /api/orders?status=open`, `POST /api/orders` (201 + `Location`), `PUT /api/orders/7`, `DELETE /api/orders/7`. Correct use of methods and status codes lets generic tools (caches, proxies, retries, monitoring) work without knowing your business.

**Example 2: Static assets and CDNs.** A site serves `logo.9a8b7c.png` with `Cache-Control: public, max-age=31536000, immutable`. The hash in the filename changes whenever the file does, so browsers and CDNs can keep it for a year and the page still updates instantly when you deploy a new version.

## 14. Common mistakes

- Using GET for actions that change data (crawlers and prefetchers will trigger them).
- Returning `200` with an error message in the body instead of a proper 4xx/5xx.
- Retrying POST blindly (duplicates); use idempotency keys or make operations idempotent.
- Forgetting `Content-Length` or `Content-Type` (clients cannot frame or interpret the body).
- Creating a new connection per request instead of reusing one client.
- Caching private data in shared caches (`Cache-Control: private` / `no-store` for user-specific responses).
- Cookies without `HttpOnly`, `Secure` and `SameSite` for sessions.
- Not setting client timeouts.

## 15. Practice

1. What does the blank line in an HTTP message mean?
2. Which of GET, POST, PUT, DELETE are idempotent? Which are safe?
3. A request returns `503` with `Retry-After: 30`. What should a well-behaved client do?
4. Why does the server answer `304` with no body, and what must the client already have?
5. Write the raw request text for `POST /items` with a JSON body `{"a": 1}`.
6. How would you make the tiny server also return `Content-Type: text/plain` for `/about`? (describe the change)
7. What problem does `SameSite` solve?

<details>
<summary>Solutions</summary>

1. It ends the header section; any body follows it.
2. Idempotent: GET, PUT, DELETE. Safe: GET only (among these four).
3. Wait about 30 seconds (with jitter) and retry; do not hammer the server. 5xx means the failure may be temporary.
4. The client's cached copy is still current (its ETag matched), so the server only confirms and sends no body; the client must have the earlier full response stored.
5. ```python
   body = '{"a": 1}'
   raw = (f"POST /items HTTP/1.1\r\nHost: x\r\nContent-Type: application/json\r\n"
          f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n{body}")
   print(parse_response(raw_request(raw))[:2])                 # (201, 'Created')
   ```
6. Store the content type with each route (`routes = {"/about": (b"...", "text/plain")}`) and use it when building the header line.
7. It stops browsers from attaching the cookie to requests initiated by other sites, which blocks most cross-site request forgery (CSRF) attacks.

</details>

## 16. Check yourself

1. What are the three parts of an HTTP request?
2. Why is HTTP called stateless and how do cookies work around it?
3. What does a 4xx versus a 5xx status mean for retries?
4. What is the difference between `max-age` and `ETag` caching?
5. Why reuse connections?
6. What does HTTP/2 add over HTTP/1.1?

<details>
<summary>Answers</summary>

1. Request line (method, path, version), headers, optional body.
2. Each request is independent; the server issues a token in `Set-Cookie` and the client returns it in `Cookie` on later requests.
3. 4xx: the request itself is wrong, do not retry unchanged; 5xx: server-side failure, retry later (with backoff) may succeed.
4. `max-age` lets the client reuse its copy without any request; `ETag` validation sends a conditional request and gets a cheap 304 if unchanged.
5. Each new connection costs a TCP (and TLS) handshake; reuse removes that latency.
6. Multiplexed requests over one connection, binary framing and header compression.

</details>

[Back to DNS and HTTP](README.md)
