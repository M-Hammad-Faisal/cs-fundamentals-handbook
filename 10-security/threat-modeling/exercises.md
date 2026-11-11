# Threat Modeling and Secure Python: Exercises

These problems go with the [Threat Modeling and Secure Python lesson](README.md). Try each one before opening its solution.

<details>
<summary>Setup code the solutions use (copied from the lessons)</summary>

```python
from dataclasses import dataclass

@dataclass
class Threat:
    where: str
    stride: str
    what: str
    likelihood: int     # 1 (rare) to 5 (expected)
    impact: int         # 1 (annoying) to 5 (catastrophic)
    mitigation: str

    @property
    def risk(self) -> int:
        return self.likelihood * self.impact

threats = [
    Threat("browser -> API", "Spoofing", "stolen session cookie used by attacker", 3, 4, "short expiry, HttpOnly+Secure cookies, rotate on login"),
    Threat("browser -> API", "Tampering", "user edits note id in URL to read another user's note (IDOR)", 5, 4, "check owner on every read"),
    Threat("API -> database", "Information disclosure", "SQL injection dumps the users table", 3, 5, "parameterized queries, least-privilege DB user"),
    Threat("API", "Denial of service", "one client floods the login endpoint", 4, 3, "rate limit per IP and per account"),
    Threat("API logs", "Information disclosure", "passwords written to logs on error", 3, 3, "redact fields, never log request bodies for /login"),
    Threat("whole system", "Repudiation", "admin deletes a note and denies it", 2, 3, "append-only audit log"),
]
```

</details>

## Problems

1. Add two threats to the notes-API table (one Elevation of privilege, one Tampering), score them and see where they rank.
2. Write `safe_ping(host)` that validates `host` against an allow-list pattern and calls `subprocess.run(["ping", "-c", "1", host])` without a shell. What happens if `host` is `"x; rm -rf /"`?
3. Generate a 6-digit one-time code securely. Why is `random.randint` wrong here?
4. Sign a cookie value `"user=ada"` with HMAC and write a `load_cookie` that returns the value only if the signature is valid.
5. Why is `ast.literal_eval` safer than the `eval` built-in, and what can it *not* do?

<details>
<summary>Solutions</summary>

1. ```python
   threats += [
       Threat("API", "Elevation of privilege", "normal user calls an /admin endpoint", 3, 5, "role check on every route"),
       Threat("browser -> API", "Tampering", "client sets price in the order request", 4, 4, "ignore client prices; look them up server-side"),
   ]
   print(sorted(t.risk for t in threats))
   # [6, 9, 12, 12, 15, 15, 16, 20]
   ```
2. ```python
   import re, subprocess
   HOST = re.compile(r"[A-Za-z0-9.-]{1,253}")
   def safe_ping(host: str):
       if not HOST.fullmatch(host):
           raise ValueError("invalid host")
       return subprocess.run(["ping", "-c", "1", host])
   # safe_ping("x; rm -rf /") raises ValueError: the ';' and spaces are not in the allow-list
   ```
3. ```python
   import secrets
   code = f"{secrets.randbelow(1_000_000):06d}"
   print(len(code), code.isdigit())
   # 6 True
   ```
   `random.randint` is predictable, so an attacker who observes outputs could predict future codes.
4. ```python
   import hmac, hashlib
   KEY = b"k"
   def dump_cookie(value: str) -> str:
       return value + "." + hmac.new(KEY, value.encode(), hashlib.sha256).hexdigest()
   def load_cookie(cookie: str):
       value, _, sig = cookie.rpartition(".")
       good = hmac.new(KEY, value.encode(), hashlib.sha256).hexdigest()
       return value if hmac.compare_digest(sig, good) else None
   c = dump_cookie("user=ada")
   print(load_cookie(c), load_cookie(c.replace("ada", "root")))
   # user=ada None
   ```
5. `literal_eval` only accepts Python literals (numbers, strings, lists, dicts, tuples, sets, booleans, `None`), so it cannot call functions or import modules. It cannot evaluate names, arithmetic on variables or any call, which is exactly why it is safe.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Threat Modeling and Secure Python](01-threat-modeling-and-secure-python.md)
