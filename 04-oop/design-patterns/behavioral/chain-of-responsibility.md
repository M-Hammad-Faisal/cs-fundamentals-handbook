# Chain of Responsibility Pattern

**Family:** behavioral · **Also called:** middleware, pipeline of handlers · **How often you will use it:** often (web middleware) · **Difficulty:** easy to medium

## 1. In plain words

A request travels along a **chain of handlers**. Each handler either **deals with it** or **passes it on** to the next. The sender does not know which handler will finally take it.

Analogy: **customer support escalation**. First-line support tries; if they cannot solve it they pass it to a specialist, then to a manager. Or **airport security**: ticket check, ID check, scanner, each can stop you or let you through.

## 2. The problem

One big function decides everything, with a tangle of checks that is hard to reorder or extend:

```python
def handle(request):
    if not request.user: return "401"
    if request.calls > 100: return "429"
    if request.path not in ROUTES: return "404"
    ...                                  # every new rule edits this function and the order is fixed
```

## 3. The solution

```text
Client ──► Handler A ──next──► Handler B ──next──► Handler C ──► (nobody) 
          (can handle?          (can handle?        (can handle?
           yes: stop, no: pass)  yes: stop ...)      ...)
```

Each handler has a reference to the next. Adding, removing or reordering handlers does not require changing the others.

## 4. Step by step

```python
class Handler:
    def __init__(self, next_handler=None):
        self.next = next_handler

    def handle(self, request):
        if self.can_handle(request):
            return self.process(request)
        if self.next:
            return self.next.handle(request)             # pass it along
        return f"no handler for {request!r}"

    def can_handle(self, request): raise NotImplementedError
    def process(self, request): raise NotImplementedError

class AuthHandler(Handler):
    def can_handle(self, r): return not r.get("user")
    def process(self, r): return "401 unauthenticated"

class RateLimitHandler(Handler):
    def can_handle(self, r): return r.get("calls", 0) > 100
    def process(self, r): return "429 too many requests"

class AppHandler(Handler):
    def can_handle(self, r): return True
    def process(self, r): return f"200 hello {r['user']}"

chain = AuthHandler(RateLimitHandler(AppHandler()))
print(chain.handle({}))                                  # 401 unauthenticated
print(chain.handle({"user": "ana", "calls": 500}))       # 429 too many requests
print(chain.handle({"user": "ana", "calls": 3}))         # 200 hello ana
```

### Variant: every handler may act, then pass on (middleware style)

```python
def logging_middleware(next_fn):
    def handler(request):
        print("log:", request["path"])
        return next_fn(request)
    return handler

def auth_middleware(next_fn):
    def handler(request):
        if request.get("user") != "admin":
            return "403 forbidden"
        return next_fn(request)
    return handler

def view(request):
    return f"200 secret page {request['path']}"

app = logging_middleware(auth_middleware(view))          # build the chain by wrapping
print(app({"path": "/a", "user": "admin"}))              # log: /a   then   200 secret page /a
print(app({"path": "/b", "user": "bob"}))                # log: /b   then   403 forbidden
```

### A simple validation chain

```python
import re

def not_empty(d):      return None if d.get("name") else "name is required"
def valid_email(d):    return None if re.fullmatch(r"[^@\s]+@[^@\s]+\.\w+", d.get("email", "")) else "invalid email"
def long_password(d):  return None if len(d.get("password", "")) >= 8 else "password too short"

def validate(data, chain=(not_empty, valid_email, long_password)):
    for check in chain:
        error = check(data)
        if error:
            return error                                 # first failing handler stops the chain
    return "ok"

print(validate({"name": "a", "email": "a@x.com", "password": "12345678"}))     # ok
print(validate({"name": "a", "email": "bad"}))                                  # invalid email
```

## 5. The Pythonic way

- A chain can be a **list of callables** iterated in order; no linked handler classes needed.
- **Middleware stacks** (WSGI, ASGI, Django, Express) are chains built by wrapping functions.
- **Exception handling** is a chain: `except` clauses are tried in order and the exception propagates up the call stack until a handler matches.
- `logging` propagates records through a hierarchy of loggers and handlers.

## 6. When to use it (and when not to)

**Use it when** more than one object may handle a request and the handler is not known in advance; you need ordered, pluggable processing (authentication, validation, logging, caching, rate limiting); you want to add/remove steps by configuration.

**Skip it when** exactly one known object handles the request (call it directly), or the order or outcome must be explicit and easily traced.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Decouples sender from receivers | A request may fall off the end unhandled |
| Add/remove/reorder handlers freely | Hard to debug long chains ("who handled it?") |
| Each handler has a single responsibility | Order bugs are subtle (auth after logging vs before) |

## 8. Related patterns

- [Decorator](../structural/decorator.md): wrapping chains look similar (middleware is both).
- [Observer](observer.md): notifies *all* listeners; the chain stops at the first handler (in the strict form).
- [Command](command.md): requests passed along the chain can be commands.
- [Composite](../structural/composite.md): a handler's parent can be the next handler.

## 9. Two real-world examples

**Example 1: Web framework middleware.** A request flows through security headers, session loading, authentication, CSRF protection, rate limiting and finally the view. Each can respond early (401, 429) or pass along.

**Example 2: Approval workflows.** Expenses under 100 are approved by a team lead, under 1,000 by a manager, under 10,000 by a director; larger go to the CFO. Each handler approves if within its limit or escalates.

## 10. Common mistakes

- Forgetting to call the next handler (the chain silently stops).
- Unclear order (document it; test it).
- No fallback at the end of the chain.
- Handlers that mutate the request in conflicting ways.

## 11. Practice

1. Implement an expense approval chain with limits 100, 1000, 10000.
2. Add a "log everything" handler that logs and always passes on.
3. Write a middleware chain that adds timing and catches exceptions, returning `500`.

<details>
<summary>Solutions</summary>

**1.**
```python
class Approver:
    def __init__(self, name, limit, next_approver=None):
        self.name, self.limit, self.next = name, limit, next_approver
    def approve(self, amount):
        if amount <= self.limit:
            return f"{self.name} approved {amount}"
        if self.next:
            return self.next.approve(amount)
        return f"{amount} needs board approval"
chain = Approver("lead", 100, Approver("manager", 1000, Approver("director", 10000)))
print(chain.approve(50), "|", chain.approve(5000), "|", chain.approve(50000))
```

**2.**
```python
def audit(next_fn, sink):
    def handler(req):
        sink.append(req)
        return next_fn(req)
    return handler
seen = []
app2 = audit(view, seen)
app2({"path": "/z"}); print(seen)
```

**3.**
```python
import time
def timing(next_fn, sink):
    def handler(req):
        t = time.perf_counter()
        try:
            return next_fn(req)
        finally:
            sink.append(time.perf_counter() - t)         # record how long the rest of the chain took
    return handler
def errors(next_fn):
    def handler(req):
        try:
            return next_fn(req)
        except Exception:
            return "500 server error"
    return handler
def boom(req): raise RuntimeError
durations = []
print(errors(timing(boom, durations))({}), errors(timing(view, durations))({"path": "/ok"}), len(durations))
# 500 server error 200 secret page /ok 2
```

</details>

## 12. Check yourself

1. How does a request move along the chain?
2. What is the main danger of a chain?
3. How is middleware a chain of responsibility?
4. Chain versus Observer?

<details>
<summary>Answers</summary>

1. Each handler either handles it or passes it to the next handler.
2. The request may reach the end unhandled, and order mistakes are hard to spot.
3. Each middleware inspects the request and either responds early or calls the next layer.
4. Observer notifies every subscriber; a chain gives the request to handlers in order, usually stopping at the first one that handles it.

</details>

## More examples

Runnable script (added to your companion repository with this lesson): [`behavioralPattern/chainOfResponsibilityPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/behavioralPattern/chainOfResponsibilityPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
