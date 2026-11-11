# DNS and HTTP

## Detailed lessons

- [HTTP from scratch](01-http-from-scratch.md): raw requests, methods, status codes, headers, keep-alive, caching, cookies, and your own tiny server
- [DNS in depth](02-dns-in-depth.md): the packet format, a toy DNS server over UDP, TTL caching, the resolution hierarchy
- [HTTP/2 and HTTP/3 internals](03-http2-and-http3-internals.md): frames, multiplexing, HPACK (checked against the RFC), flow control, head-of-line blocking, QUIC, ALPN

The rest of this page is the quick reference.

## 1. DNS: the internet's phone book

**DNS** turns names (`www.example.com`) into addresses and other data. It is a distributed, hierarchical, heavily cached database, usually over UDP port 53 (TCP for large answers; also DNS over HTTPS/TLS).

### Resolution

```text
browser cache -> OS cache -> recursive resolver (ISP / 1.1.1.1 / 8.8.8.8)
                                   |  cache miss
                                   v
                          root servers  ->  ".com" TLD servers  ->  example.com authoritative server
                                   <-------- answer + TTL ------------
```

The **recursive resolver** does the walking for you and caches each answer for its **TTL** (time to live). The **authoritative** server owns the zone's records.

| Record | Meaning |
|--------|---------|
| **A / AAAA** | Name to IPv4 / IPv6 address |
| **CNAME** | Alias to another name (not allowed at the zone apex) |
| **MX** | Mail servers (with priority) |
| **TXT** | Free text: SPF, DKIM, domain verification |
| **NS** | Delegates a zone to name servers |
| **SRV** | Host and port for a service |
| **PTR** | Reverse lookup (IP to name) |

### A DNS message by hand

```python
import struct

def build_query(name, qid=0x1234):
    header = struct.pack("!HHHHHH", qid, 0x0100, 1, 0, 0, 0)   # RD flag, 1 question
    qname = b"".join(bytes([len(p)]) + p.encode() for p in name.split(".")) + b"\x00"
    return header + qname + struct.pack("!HH", 1, 1)          # type A, class IN
q = build_query("example.com")
print(len(q), q[:12].hex(), q[12:])
def parse_name(data, off):
    labels = []
    while True:
        n = data[off]
        if n == 0: return ".".join(labels), off + 1
        if n & 0xC0 == 0xC0:
            ptr = ((n & 0x3F) << 8) | data[off + 1]
            return ".".join(labels + [parse_name(data, ptr)[0]]), off + 2
        labels.append(data[off+1:off+1+n].decode()); off += 1 + n
print(parse_name(q, 12))
# fake response with compression pointer
resp = struct.pack("!HHHHHH", 0x1234, 0x8180, 1, 1, 0, 0) + q[12:]
resp += b"\xc0\x0c" + struct.pack("!HHIH", 1, 1, 300, 4) + bytes([93,184,216,34])
off = 12 + len(q[12:])
nm, off = parse_name(resp, off)
typ, cls, ttl, rdlen = struct.unpack("!HHIH", resp[off:off+10])
print(nm, typ, ttl, ".".join(map(str, resp[off+10:off+10+rdlen])))
```

The query is a 12-byte header (id, flags, counts) followed by the name as length-prefixed labels (`7example3com0`), then type `A` and class `IN`. Responses reuse earlier names through **compression pointers** (`0xC0xx`), which `parse_name` follows.

Practical DNS knowledge:
- **TTL trade-off:** low TTL = fast failover but more lookups; high TTL = fewer lookups but slow changes. Lower TTL *before* a migration.
- DNS-based load balancing (several A records, geo-DNS) is coarse because caches ignore your wishes.
- Debug with `dig example.com`, `dig +trace`, `nslookup`.
- Negative answers (NXDOMAIN) are cached too.

## 2. HTTP

**HTTP** is the request/response protocol of the web, carried over TCP+TLS (HTTP/1.1, HTTP/2) or QUIC (HTTP/3). It is **stateless**: each request carries everything the server needs (cookies and tokens provide identity).

```text
GET /hello?x=1 HTTP/1.1          <- request line: method, target, version
Host: example.com                <- headers
Accept: application/json

HTTP/1.1 200 OK                  <- status line
Content-Type: application/json
Content-Length: 18

{"path": "/hello"}
```

### Methods and idempotency

| Method | Use | Safe (no side effect) | Idempotent (repeat = same result) |
|--------|-----|----------------------|-----------------------------------|
| GET | Read | yes | yes |
| HEAD | Headers only | yes | yes |
| POST | Create / action | no | **no** |
| PUT | Replace | no | yes |
| PATCH | Partial update | no | not guaranteed |
| DELETE | Remove | no | yes |

Idempotency tells clients whether a **retry** after a timeout is safe. For POST, use an **idempotency key** header so a retried payment is applied once.

### Status codes

| Range | Meaning | Common |
|-------|---------|--------|
| 1xx | Informational | 101 Switching Protocols (WebSocket) |
| 2xx | Success | 200 OK, 201 Created, 204 No Content |
| 3xx | Redirect | 301 permanent, 302/307 temporary, 304 Not Modified |
| 4xx | Client error | 400, 401 (unauthenticated), 403 (forbidden), 404, 409 conflict, 422, 429 too many requests |
| 5xx | Server error | 500, 502 bad gateway, 503 unavailable, 504 gateway timeout |

### Important headers

`Host`, `Content-Type`/`Accept`, `Authorization`, `Cookie`/`Set-Cookie`, `Cache-Control`, `ETag`/`If-None-Match`, `User-Agent`, `Location`, `Retry-After`, CORS headers (`Origin`, `Access-Control-Allow-Origin`).

### Talking HTTP by hand

```python
import socket, threading, http.server, json

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({"path": self.path}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, *a): pass
httpd = http.server.HTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
with socket.create_connection(httpd.server_address) as s:
    s.sendall(b"GET /hello?x=1 HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
    raw = b""
    while chunk := s.recv(4096): raw += chunk
head, body = raw.split(b"\r\n\r\n", 1)
print(head.split(b"\r\n")[0], body)
httpd.shutdown()
```

(The standard-library server answers with HTTP/1.0 semantics; the wire format is the same.)

### Versions

| Version | Key idea |
|---------|----------|
| HTTP/1.1 | Text, keep-alive, one request at a time per connection (browsers open ~6) |
| HTTP/2 | Binary framing, **multiplexed** streams on one connection, header compression; TCP head-of-line blocking remains |
| HTTP/3 | Over **QUIC** (UDP): per-stream loss recovery, faster handshakes, connection migration |

### Caching

`Cache-Control: max-age=3600` lets caches reuse a response for an hour. After that a client can **revalidate**: send `If-None-Match: <etag>` and get `304 Not Modified` with no body. `no-store` forbids storing; `private` forbids shared caches (CDNs); versioned asset URLs (`app.3f9c.js`) with a year-long `max-age` are the standard trick.

### Cookies, sessions and REST

- A **cookie** is set by `Set-Cookie` and returned on later requests. Flags: `HttpOnly` (hidden from JavaScript), `Secure` (HTTPS only), `SameSite` (limits cross-site sending: CSRF defense), `Max-Age`.
- **Sessions:** server stores state keyed by a random session id in a cookie. **Tokens (JWT):** the client holds signed claims; revocation is harder.
- **REST** models resources as URLs and uses methods and status codes: `GET /users/42`, `PUT /users/42`, `DELETE /users/42`. Good APIs also paginate, version, validate input and return consistent errors.
- **WebSockets** upgrade a connection for two-way messages; **Server-Sent Events** stream one way over plain HTTP.

## 3. Two real-world examples

### Example 1: A DNS TTL mistake during a migration
A team moves a service to new servers and changes the A record, but the old TTL is 24 hours: many users keep reaching the old IP for a day. The playbook is to lower the TTL to 60 s a day *before* the cutover, change the record, watch traffic drain, then raise the TTL again.

### Example 2: Safe retries for payments
A mobile app POSTs a payment and the connection drops before the response arrives. Blindly retrying could charge twice. The client sends an `Idempotency-Key: <uuid>` header; the server stores the first result under that key and returns it for retries. GET, PUT and DELETE are naturally safe to retry; POST needs the key.

## 4. Tips, tricks and pitfalls

- Name the right status: `401` means "who are you?", `403` means "I know you, no"; do not return 200 with an error body.
- Never put secrets in URLs (logged everywhere); use headers or bodies.
- Set timeouts and retry only idempotent requests, with exponential backoff and jitter.
- Cache static assets aggressively with content hashes; never cache personalized responses in shared caches.
- A cookie without `HttpOnly`, `Secure` and `SameSite` is a security smell.
- CORS is enforced by the **browser**; it does not protect your API from other clients.
- `curl -v`, browser devtools Network tab, and `dig` answer most "what is on the wire" questions.

## 5. Check yourself

1. Walk through what happens when you type `www.example.com` into a browser, DNS-wise.
2. What do A, CNAME, MX and TXT records do?
3. Why lower a DNS TTL before a migration?
4. Safe vs idempotent methods: which is POST?
5. 401 versus 403? 502 versus 504?
6. How does ETag revalidation save bandwidth?
7. What do HTTP/2 and HTTP/3 improve over HTTP/1.1?
8. What are `HttpOnly`, `Secure` and `SameSite`?

<details>
<summary>Answers</summary>

1. Check browser and OS caches, then ask the recursive resolver, which (on a miss) asks a root server, then the `.com` TLD server, then example.com's authoritative server; the answer is cached for its TTL, and the browser connects to the returned IP.
2. A maps a name to IPv4; CNAME aliases one name to another; MX lists mail servers; TXT stores text (SPF, verification).
3. Cached answers live for the old TTL; a short TTL makes the change visible quickly and allows quick rollback.
4. POST is neither safe nor idempotent (use idempotency keys to make retries safe).
5. 401: not authenticated; 403: authenticated but not allowed. 502: a gateway got an invalid response from upstream; 504: the upstream timed out.
6. The client sends the cached ETag; if unchanged the server replies 304 with no body, so only headers travel.
7. HTTP/2 multiplexes many requests on one connection and compresses headers; HTTP/3 runs on QUIC, removing TCP head-of-line blocking and shortening handshakes.
8. `HttpOnly`: not readable by JavaScript; `Secure`: only sent over HTTPS; `SameSite`: restricts cross-site sending (CSRF protection).

</details>

[Exercises](exercises.md) · [Summary](summary.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

Back to the [part overview](../README.md).
