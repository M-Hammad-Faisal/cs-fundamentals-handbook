# Web Vulnerabilities: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## Common Web Vulnerabilities in Python

1. Fix this: `db.execute("SELECT * FROM posts ORDER BY " + sort_column)`. Why can't a placeholder help here?
2. Write `safe_filename(name)` that keeps only the final path component and allows letters, digits, dot, dash and underscore.
3. Using `is_safe_url`, decide for `http://[::1]/` and `http://0.0.0.0/`. Why does the second matter?
4. Write a Pydantic-free validator that accepts a payload only if its keys are a subset of `{"title", "body"}` and raises `ValueError` otherwise (stricter than silently dropping).
5. Explain why `"http://trusted.com.evil.example".startswith("http://trusted.com")` is a broken check, and what to do instead.
6. Make the unsafe regex `(a+)+$` safe while matching the same strings.

<details>
<summary>Solutions</summary>

1. ```python no-run
   ALLOWED_SORT = {"created", "title", "score"}
   def order_clause(sort_column: str) -> str:
       if sort_column not in ALLOWED_SORT:
           raise ValueError("bad sort column")
       return "SELECT * FROM posts ORDER BY " + sort_column        # safe: only allow-listed names reach the string
   print(order_clause("score"))
   # SELECT * FROM posts ORDER BY score
   ```
   Placeholders bind **values**; identifiers (column names) are part of the SQL structure and cannot be bound, so they must be allow-listed.
2. ```python no-run
   import re
   from pathlib import PurePosixPath
   def safe_filename(name: str) -> str:
       base = PurePosixPath(name.replace("\\", "/")).name
       base = re.sub(r"[^A-Za-z0-9._-]", "_", base).lstrip(".")
       return base or "file"
   print(safe_filename("../../etc/passwd"), safe_filename("my report (1).pdf"))
   # passwd my_report__1_.pdf
   ```
3. ```python no-run
   print(is_safe_url("http://[::1]/"), is_safe_url("http://0.0.0.0/"))
   # False False
   ```
   `0.0.0.0` is "this host" on many systems, so a request to it can reach local services; it is flagged as reserved and must be blocked too.
4. ```python no-run
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
6. ```python no-run
   safe = re.compile(r"a+$")                  # one quantifier, no nesting, same language
   print(bool(safe.match("aaaa")), bool(safe.match("aaab")))
   # True False
   ```

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Common Web Vulnerabilities in Python](01-owasp-top-ten-in-python.md)
