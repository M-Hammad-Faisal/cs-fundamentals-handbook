# Threat Modeling and Secure Python: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## Threat Modeling and Secure Python

1. Add two threats to the notes-API table (one Elevation of privilege, one Tampering), score them and see where they rank.
2. Write `safe_ping(host)` that validates `host` against an allow-list pattern and calls `subprocess.run(["ping", "-c", "1", host])` without a shell. What happens if `host` is `"x; rm -rf /"`?
3. Generate a 6-digit one-time code securely. Why is `random.randint` wrong here?
4. Sign a cookie value `"user=ada"` with HMAC and write a `load_cookie` that returns the value only if the signature is valid.
5. Why is `ast.literal_eval` safer than the `eval` built-in, and what can it *not* do?

<details>
<summary>Solutions</summary>

1. ```python no-run
   threats += [
       Threat("API", "Elevation of privilege", "normal user calls an /admin endpoint", 3, 5, "role check on every route"),
       Threat("browser -> API", "Tampering", "client sets price in the order request", 4, 4, "ignore client prices; look them up server-side"),
   ]
   print(sorted(t.risk for t in threats))
   # [6, 9, 12, 12, 15, 15, 16, 20]
   ```
2. ```python no-run
   import re, subprocess
   HOST = re.compile(r"[A-Za-z0-9.-]{1,253}")
   def safe_ping(host: str):
       if not HOST.fullmatch(host):
           raise ValueError("invalid host")
       return subprocess.run(["ping", "-c", "1", host])
   # safe_ping("x; rm -rf /") raises ValueError: the ';' and spaces are not in the allow-list
   ```
3. ```python no-run
   import secrets
   code = f"{secrets.randbelow(1_000_000):06d}"
   print(len(code), code.isdigit())
   # 6 True
   ```
   `random.randint` is predictable, so an attacker who observes outputs could predict future codes.
4. ```python no-run
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
