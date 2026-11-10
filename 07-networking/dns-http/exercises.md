# DNS and HTTP: Exercises

1. Use `build_query` to make a query for `mail.example.org` and decode the labels back with `parse_name`.
2. Explain the difference between a recursive resolver and an authoritative server.
3. A site sets `Cache-Control: max-age=31536000` on `app.js` and you deploy a fix. Users still see the old file. What went wrong and how do you prevent it?
4. Pick the method and status code: (a) create a user, (b) replace a user's profile, (c) delete a user that does not exist, (d) request needs login, (e) logged-in user touches another user's data, (f) rate limit exceeded.
5. Write a raw HTTP/1.1 `GET` request with the headers needed for a virtual-hosted site and an `If-None-Match`.
6. Design an idempotent `POST /payments` using an idempotency key. What do you store?
7. Why does CORS not protect your API from `curl`?
8. Compare cookies-with-sessions to JWTs for logging out a user everywhere.

<details>
<summary>Solutions</summary>

**1.**
```python
q = build_query("mail.example.org")
print(parse_name(q, 12))      # ('mail.example.org', 30): the name ends at offset 30, just before the 4 type/class bytes
```

**2.** A recursive resolver answers questions *for clients*, walking the hierarchy and caching results. An authoritative server holds the records for its zones and answers only for them.

**3.** The browser cached `app.js` for a year under the same URL. Use **content-hashed filenames** (`app.8c1f2.js`) with long `max-age` and an HTML page (cached briefly) that references the new name; for existing mistakes, change the URL.

**4.** (a) `POST /users`, 201 (with `Location`). (b) `PUT /users/42`, 200 or 204. (c) `DELETE` on a missing user: 404 (or 204 if you treat delete as idempotent success). (d) 401. (e) 403 (or 404 to avoid revealing existence). (f) 429 with `Retry-After`.

**5.**
```text
GET /app.js HTTP/1.1\r\nHost: example.com\r\nIf-None-Match: "8c1f2"\r\nAccept-Encoding: gzip\r\nConnection: close\r\n\r\n
```

**6.** Require `Idempotency-Key`. In one transaction, insert `(key, request_hash, status, response_body)` with a unique constraint on `key`. If the key already exists: return the stored response (or 409/422 if the request hash differs). Otherwise perform the payment and save the response. Expire keys after a day or two.

**7.** CORS is a browser rule: it stops a web page from reading cross-origin responses. `curl` and server code are not browsers and ignore it, so the API still needs authentication and authorization.

**8.** With server-side sessions, delete the session records and every device is logged out immediately. A self-contained JWT stays valid until expiry; you need a revocation list, short lifetimes with refresh tokens, or a per-user "token version" checked on each request.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [HTTP from Scratch](01-http-from-scratch.md) · [DNS in Depth](02-dns-in-depth.md) · [HTTP/2 and HTTP/3 Internals](03-http2-and-http3-internals.md)
