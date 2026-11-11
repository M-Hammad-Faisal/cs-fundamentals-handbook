# APIs and Real-Time Communication: Exercises

These problems go with the [APIs and Real-Time Communication lesson](README.md). Try each one before opening its solution.

## Problems

1. **Cursor pagination.** Write `paginate(items, limit, after_id=None)` for a list of dicts sorted by `id`. It returns `(page, next_cursor)`, where `next_cursor` is the id to pass as `after_id` for the next page, or `None` on the last page. Why is this more reliable than `?page=3` when items are being added?
2. **Validate a request body.** Write `validate_user(body)` returning a list of error strings for a `POST /users` body that must contain `name` (non-empty string, at most 50 characters) and `age` (integer between 0 and 150). An empty list means valid.
3. **ETags.** Write `etag_for(obj)` (a SHA-256 of the canonical JSON) and `respond(obj, if_none_match)` returning `(304, None)` when the client's tag still matches and `(200, obj)` otherwise.
4. **Idempotency keys.** Write a decorator `idempotent` so that calling `create_order(key, ...)` twice with the same key runs the function once and returns the saved result the second time.
5. **WebSocket handshake.** Compute `Sec-WebSocket-Accept` for the client key `dGhlIHNhbXBsZSBub25jZQ==` (the example in RFC 6455) and check it is `s3pPLMBiTxaQ9kYGzzhZRbK+xOo=`.
6. **WebSocket frames.** Decode a masked client text frame (bytes `81 85 37 fa 21 3d 7f 9f 4d 51 58`, also from the RFC) and encode an unmasked server text frame for the word `Hello`.
7. **Server-Sent Events.** Write `format_sse(event, data)` that builds one SSE message and `parse_sse(text)` that turns a stream of such messages back into `(event, data)` pairs.
8. **Choose the transport.** For each scenario choose polling, SSE, WebSocket or a webhook, and say why: (a) a stock ticker in a browser, (b) a multiplayer game's player positions, (c) Stripe telling your server a payment succeeded, (d) a build page showing job progress, (e) a dashboard refreshing once a minute.
9. **Replay protection.** A webhook receiver verifies an HMAC signature. Explain how an attacker could replay a valid captured request and how a timestamp and a tolerance window prevent it. Implement `verify_webhook(secret, timestamp, body, signature, now, tolerance=300)`.

<details>
<summary>Solutions</summary>

**1.**
```python
def paginate(items, limit, after_id=None):
    start = 0
    if after_id is not None:
        start = next((i + 1 for i, item in enumerate(items) if item["id"] == after_id), len(items))
    page = items[start:start + limit]
    has_more = start + limit < len(items)
    return page, (page[-1]["id"] if page and has_more else None)

items = [{"id": i} for i in range(1, 8)]
page1, cursor = paginate(items, 3)
page2, cursor2 = paginate(items, 3, cursor)
page3, cursor3 = paginate(items, 3, cursor2)
print([i["id"] for i in page1], cursor, [i["id"] for i in page2], cursor2, [i["id"] for i in page3], cursor3)
# [1, 2, 3] 3 [4, 5, 6] 6 [7] None
```
A cursor names a *position in the data*, so a new item inserted at the front does not shift later pages (offset pagination would repeat or skip items), and a database can answer it with `WHERE id > :after ORDER BY id LIMIT n` using the index, in constant time even for deep pages.

**2.**
```python
def validate_user(body):
    errors = []
    name, age = body.get("name"), body.get("age")
    if not isinstance(name, str) or not name.strip():
        errors.append("name: required, non-empty string")
    elif len(name) > 50:
        errors.append("name: at most 50 characters")
    if not isinstance(age, int) or isinstance(age, bool):
        errors.append("age: required integer")
    elif not 0 <= age <= 150:
        errors.append("age: must be between 0 and 150")
    return errors

print(validate_user({"name": "Ada", "age": 36}), validate_user({"name": "", "age": 200}), validate_user({"age": True}))
# [] ['name: required, non-empty string', 'age: must be between 0 and 150'] ['name: required, non-empty string', 'age: required integer']
```
(`bool` is a subclass of `int` in Python, so `True` must be rejected explicitly.) Return a `422` with all the errors at once, not just the first.

**3.**
```python
import hashlib, json

def etag_for(obj):
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return '"' + hashlib.sha256(canonical).hexdigest()[:16] + '"'

def respond(obj, if_none_match=None):
    if if_none_match == etag_for(obj):
        return 304, None                                  # the client's cached copy is still valid: send no body
    return 200, obj

doc = {"id": 1, "name": "Ada"}
tag = etag_for(doc)
print(respond(doc)[0], respond(doc, tag)[0], respond({"id": 1, "name": "Ada L."}, tag)[0])
# 200 304 200
```

**4.**
```python
import functools

def idempotent(fn):
    saved = {}
    @functools.wraps(fn)
    def wrapper(key, *args, **kwargs):
        if key not in saved:
            saved[key] = fn(*args, **kwargs)
        return saved[key]
    return wrapper

created = []
@idempotent
def create_order(item):
    created.append(item)
    return {"order_id": len(created), "item": item}

print(create_order("k1", "pen"), create_order("k1", "pen"), len(created))
# {'order_id': 1, 'item': 'pen'} {'order_id': 1, 'item': 'pen'} 1
```
In production the saved results live in a database with a unique constraint on the key, written in the same transaction as the order.

**5.**
```python
import base64, hashlib

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"             # a fixed constant from RFC 6455
def accept_key(client_key):
    return base64.b64encode(hashlib.sha1((client_key + GUID).encode()).digest()).decode()

print(accept_key("dGhlIHNhbXBsZSBub25jZQ=="))
# s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```
(SHA-1 is used here only as a handshake checksum, not for security.)

**6.**
```python
def decode_frame(data):
    opcode = data[0] & 0x0F
    masked = data[1] & 0x80
    length = data[1] & 0x7F                                # lengths above 125 use extra bytes (not handled here)
    pos = 2
    mask = data[pos:pos + 4] if masked else None
    if masked:
        pos += 4
    payload = data[pos:pos + length]
    if masked:
        payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    return opcode, payload.decode()

def encode_text_frame(text):
    payload = text.encode()
    return bytes([0x81, len(payload)]) + payload            # FIN + text opcode, unmasked (servers never mask)

print(decode_frame(bytes.fromhex("81 85 37 fa 21 3d 7f 9f 4d 51 58")), encode_text_frame("Hello").hex(" "))
# (1, 'Hello') 81 05 48 65 6c 6c 6f
```
Clients must mask their frames (to prevent cache poisoning by intermediaries); servers must not.

**7.**
```python
def format_sse(event, data):
    lines = "".join(f"data: {line}\n" for line in str(data).split("\n"))
    return f"event: {event}\n{lines}\n"

def parse_sse(text):
    events = []
    for block in text.strip("\n").split("\n\n"):
        event, data = "message", []
        for line in block.split("\n"):
            if line.startswith("event: "):
                event = line[7:]
            elif line.startswith("data: "):
                data.append(line[6:])
        events.append((event, "\n".join(data)))
    return events

stream = format_sse("price", '{"sym": "ABC", "px": 10.5}') + format_sse("alert", "line one\nline two")
print(parse_sse(stream))
# [('price', '{"sym": "ABC", "px": 10.5}'), ('alert', 'line one\nline two')]
```

**8.** (a) **SSE** (one-way server to browser, auto-reconnect, works through proxies); WebSocket also works but is more than needed. (b) **WebSocket** (two-way, low latency, many small messages). (c) **Webhook** (server-to-server notification; verify the signature). (d) **SSE** (one-way progress updates); polling every few seconds is the simplest fallback. (e) **Polling** (the update rate is low and a held-open connection is not worth it).

**9.**
```python
import hashlib, hmac

def sign(secret, timestamp, body):
    return hmac.new(secret, f"{timestamp}.".encode() + body, hashlib.sha256).hexdigest()

def verify_webhook(secret, timestamp, body, signature, now, tolerance=300):
    if abs(now - timestamp) > tolerance:
        return False                                          # too old (or from the future): possible replay
    return hmac.compare_digest(sign(secret, timestamp, body), signature)

secret, body = b"whsec", b'{"event": "paid"}'
sig = sign(secret, 1000, body)
print(verify_webhook(secret, 1000, body, sig, now=1100), verify_webhook(secret, 1000, body, sig, now=5000), verify_webhook(secret, 1000, b'{"event": "refund"}', sig, now=1100))
# True False False
```
A captured request carries a valid signature forever unless the signature covers a **timestamp** that the receiver checks; the attacker cannot change the timestamp without invalidating the signature. For stricter protection also remember recent **event ids** and reject repeats.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [REST APIs, Server-Sent Events and WebSockets](01-rest-apis-and-websockets-lab.md)
