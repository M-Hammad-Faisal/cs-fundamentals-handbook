# Exceptions, Logging and Testing: Exercises

1. Write `safe_divide(a, b)` that returns `None` for division by zero, raises `TypeError` for non-numbers, and logs a warning in the zero case. Use `else`/`finally` correctly.
2. Create an exception hierarchy `AppError > (ValidationError, NotFoundError, PermissionDenied)` and a function that raises each. Catch the whole family in one handler and one member in another.
3. Convert a low-level error into a domain error with `raise ... from e` and show that the cause is preserved.
4. Write a `retry(times, retry_on)` decorator and a test showing it retries transient errors but not `ValueError`.
5. Build a context manager `timer(name, log)` that records how long the block took, even when it raises.
6. Configure a logger named `app.payments` with a console handler (level INFO) and write messages at each level; show which ones appear. Then make output JSON.
7. Write a function that logs with `logger.exception` and re-raises, and test the log with `caplog` (pytest).
8. Write pytest tests for `is_palindrome(text)` ignoring case and punctuation, using `parametrize` for at least 6 cases (including empty string and non-letters).
9. Write a `fixture` that provides a populated in-memory SQLite database and tests for a `find_by_email` function (found, not found, case-insensitive).
10. Test an `EmailSender`-using `SignupService` with mocks: the email is sent once on success and never when the username is taken. Then rewrite with a fake and compare the two styles.
11. A test passes locally and fails randomly in CI. List five likely causes and how to fix each.

<details>
<summary>Solutions</summary>

**1.**
```python
import logging
log = logging.getLogger("math")

def safe_divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        log.warning("division by zero: %s / %s", a, b)
        return None
    except TypeError:
        raise TypeError(f"numbers required, got {type(a).__name__} and {type(b).__name__}") from None
    else:
        return result
    finally:
        log.debug("safe_divide(%r, %r) finished", a, b)

print(safe_divide(6, 3), safe_divide(1, 0))                  # 2.0 None
try:
    safe_divide("a", 2)
except TypeError as e:
    print(e)
```

**2.**
```python
class AppError(Exception): pass
class ValidationError(AppError): pass
class NotFoundError(AppError): pass
class PermissionDenied(AppError): pass

def act(kind):
    raise {"v": ValidationError, "n": NotFoundError, "p": PermissionDenied}[kind](f"{kind} failed")

for kind in "vnp":
    try:
        act(kind)
    except NotFoundError as e:
        print("not found handler:", e)
    except AppError as e:                                    # everything else in the family
        print("generic app handler:", type(e).__name__)
```

**3.**
```python
import sqlite3

class DuplicateUser(AppError): pass

def create_user(db, email):
    try:
        db.execute("INSERT INTO u VALUES (?)", (email,))
    except sqlite3.IntegrityError as e:
        raise DuplicateUser(f"{email} already registered") from e

db = sqlite3.connect(":memory:"); db.execute("CREATE TABLE u (email TEXT UNIQUE)")
create_user(db, "a@x.com")
try:
    create_user(db, "a@x.com")
except DuplicateUser as e:
    print(e, "| cause:", type(e.__cause__).__name__)        # a@x.com already registered | cause: IntegrityError
```

**4.**
```python
# pytest
import pytest

def retry(times, retry_on=(ConnectionError,)):
    def deco(fn):
        def wrapper(*a, **kw):
            for attempt in range(1, times + 1):
                try:
                    return fn(*a, **kw)
                except retry_on:
                    if attempt == times:
                        raise
        return wrapper
    return deco

def test_retries_transient_errors():
    calls = []
    @retry(3)
    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise ConnectionError
        return "ok"
    assert flaky() == "ok" and len(calls) == 3

def test_does_not_retry_value_error():
    calls = []
    @retry(3)
    def bad():
        calls.append(1)
        raise ValueError
    with pytest.raises(ValueError):
        bad()
    assert len(calls) == 1
```

**5.**
```python
import time
from contextlib import contextmanager

@contextmanager
def timer(name, sink):
    start = time.perf_counter()
    try:
        yield
    finally:
        sink.append((name, time.perf_counter() - start))     # runs even when the block raises

sink = []
try:
    with timer("risky", sink):
        raise RuntimeError("fail")
except RuntimeError:
    pass
print(sink[0][0], sink[0][1] >= 0)                           # risky True
```

**6.**
```python
import logging, io, json

buf = io.StringIO()
h = logging.StreamHandler(buf); h.setLevel(logging.INFO)
h.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
lg = logging.getLogger("app.payments"); lg.setLevel(logging.DEBUG); lg.addHandler(h); lg.propagate = False
for level in ("debug", "info", "warning", "error", "critical"):
    getattr(lg, level)("%s message", level)
print(buf.getvalue().split())                                # DEBUG is filtered out by the handler level (INFO)

class JsonFormatter(logging.Formatter):
    def format(self, r): return json.dumps({"level": r.levelname, "msg": r.getMessage(), "logger": r.name})
h.setFormatter(JsonFormatter()); buf.truncate(0); buf.seek(0)
lg.warning("disk %s%% full", 91)
print(buf.getvalue().strip())
```

**7.**
```python
# pytest
import logging
import pytest

log = logging.getLogger("svc")

def risky():
    try:
        return 1 / 0
    except ZeroDivisionError:
        log.exception("risky failed")
        raise

def test_logs_and_reraises(caplog):
    with caplog.at_level(logging.ERROR), pytest.raises(ZeroDivisionError):
        risky()
    assert "risky failed" in caplog.text
    assert "ZeroDivisionError" in caplog.text
```

**8.**
```python
# pytest
import re
import pytest

def is_palindrome(text):
    letters = [c.lower() for c in text if c.isalnum()]
    return letters == letters[::-1]

@pytest.mark.parametrize("text, expected", [
    ("racecar", True),
    ("A man, a plan, a canal: Panama", True),
    ("hello", False),
    ("", True),
    ("!!!", True),
    ("ab", False),
    ("Was it a car or a cat I saw?", True),
])
def test_is_palindrome(text, expected):
    assert is_palindrome(text) is expected
```

**9.**
```python
# pytest
import sqlite3
import pytest

@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, name TEXT)")
    conn.executemany("INSERT INTO users (email, name) VALUES (?, ?)", [("ana@x.com", "Ana"), ("bo@x.com", "Bo")])
    yield conn
    conn.close()

def find_by_email(conn, email):
    row = conn.execute("SELECT name FROM users WHERE lower(email) = lower(?)", (email,)).fetchone()
    return row[0] if row else None

def test_found(db):
    assert find_by_email(db, "ana@x.com") == "Ana"

def test_not_found(db):
    assert find_by_email(db, "zed@x.com") is None

def test_case_insensitive(db):
    assert find_by_email(db, "BO@X.COM") == "Bo"
```

**10.**
```python
# pytest
from unittest.mock import Mock

class SignupService:
    def __init__(self, users, mailer):
        self.users, self.mailer = users, mailer
    def signup(self, name, email):
        if name in self.users:
            return False
        self.users.add(name)
        self.mailer.send(email, f"Welcome {name}")
        return True

def test_with_mock_sends_once():
    mailer = Mock()
    assert SignupService(set(), mailer).signup("ana", "a@x.com")
    mailer.send.assert_called_once_with("a@x.com", "Welcome ana")

def test_with_mock_not_sent_when_taken():
    mailer = Mock()
    assert not SignupService({"ana"}, mailer).signup("ana", "a@x.com")
    mailer.send.assert_not_called()

class FakeMailer:
    def __init__(self): self.outbox = []
    def send(self, to, body): self.outbox.append((to, body))

def test_with_fake():
    mailer = FakeMailer()
    svc = SignupService(set(), mailer)
    svc.signup("ana", "a@x.com"); svc.signup("ana", "a@x.com")
    assert mailer.outbox == [("a@x.com", "Welcome ana")]       # asserts the OUTCOME, not how it was called
```
The fake version survives refactors of how the service calls the mailer; the mock version checks the exact interaction.

**11.** (1) Shared state or test order dependence: isolate with fixtures, use `tmp_path`, never mutate module globals; (2) real time/sleeps and race conditions: inject a clock, wait on conditions not durations; (3) randomness: seed or inject the random source; (4) network or external services: replace with fakes or recorded responses; (5) environment differences (timezone, locale, file paths, dependency versions): pin versions, set `TZ`, use `pathlib` and temp dirs. Also: parallel test runs sharing a database or port.

</details>

[Lesson](README.md) · [Summary](summary.md)
