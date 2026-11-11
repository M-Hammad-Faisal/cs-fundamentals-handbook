# Idempotency, Retries, Circuit Breakers, Sagas and the Outbox

**Prerequisites:** [Failures, time and clocks](../foundations/01-failures-time-and-clocks.md), [transactions and ACID](../../05-databases/transactions-acid/README.md), [exceptions and decorators](../../08-modern-python/exceptions-logging-testing/README.md). **You will learn:** how to make an operation **safe to repeat** (idempotency keys), how to **retry** without causing retry storms (exponential backoff with jitter), how a **circuit breaker** protects a failing dependency, how to keep data consistent across services with a **saga** (compensating actions) and the **transactional outbox**, and why **two-phase commit** is avoided, all with runnable code.

## 1. In plain words

When a request gets no reply, you cannot tell whether the work happened ([failures lesson](../foundations/01-failures-time-and-clocks.md)). So you **retry**. If the first attempt actually succeeded, the retry may do the work a **second time**: a customer is charged twice, two emails are sent, two orders are created. The central rule of reliable distributed programming is:

> **Make operations idempotent: doing them twice has the same effect as doing them once.** Then retries are always safe.

`SET balance = 100` is idempotent; `ADD 10 TO balance` is not. Reading is idempotent; "create a payment" is not, unless you make it so.

## 2. The double charge

A payment service that does the work, then loses the reply:

```python
class PaymentService:
    def __init__(self):
        self.charges = []                              # money actually taken
        self.reply_lost_next = False                   # simulate "the work happened, the reply never arrived"

    def charge(self, customer, amount):
        self.charges.append((customer, amount))
        if self.reply_lost_next:
            self.reply_lost_next = False
            raise TimeoutError("no reply")
        return "ok"

svc = PaymentService()
svc.reply_lost_next = True
try:
    svc.charge("ada", 50)
except TimeoutError:
    svc.charge("ada", 50)                              # the client dutifully retries
print(svc.charges)
# [('ada', 50), ('ada', 50)]                           # charged twice!
```

### The fix: idempotency keys

The **client** generates a unique key per logical operation (a UUID) and sends it with **every** retry. The **server** remembers the result for each key and returns the stored result instead of repeating the work (Stripe's API works exactly this way).

```python
import uuid

class IdempotentPaymentService:
    def __init__(self):
        self.charges = []
        self.results = {}                              # idempotency_key -> result (in production: a database table with a unique constraint)
        self.reply_lost_next = False

    def charge(self, key, customer, amount):
        if key in self.results:                        # seen before: return the saved result, do NOT repeat the work
            return self.results[key]
        self.charges.append((customer, amount))
        self.results[key] = "ok"
        if self.reply_lost_next:
            self.reply_lost_next = False
            raise TimeoutError("no reply")
        return "ok"

svc = IdempotentPaymentService()
svc.reply_lost_next = True
key = str(uuid.uuid4())                                # ONE key for this purchase
for attempt in range(3):
    try:
        print("attempt", attempt + 1, "->", svc.charge(key, "ada", 50))
        break
    except TimeoutError:
        print("attempt", attempt + 1, "-> timeout, retrying with the SAME key")
print(svc.charges)
# attempt 1 -> timeout, retrying with the SAME key
# attempt 2 -> ok
# [('ada', 50)]
```

In a real service the check-and-record must be **atomic** (a unique index on the key, inserted in the same database transaction as the work), otherwise two concurrent retries could both pass the check. Other idempotent designs: use **natural keys** (`INSERT ... ON CONFLICT DO NOTHING` on an order id), **versioned updates** (`UPDATE ... WHERE version = 7`), and **deduplication** of messages by id on the consumer ([logs and queues lesson](../messaging-storage/01-logs-queues-and-lsm-trees.md)).

## 3. Retrying well: backoff and jitter

Retrying instantly, forever, makes outages worse: thousands of clients hammer a struggling server in lockstep (a **retry storm** or **thundering herd**). The standard recipe:

- **Exponential backoff:** wait `base * 2^attempt` (capped) between tries.
- **Jitter:** randomise the wait so clients spread out instead of retrying at the same instants.
- **Limits:** a maximum number of attempts and an overall deadline.
- **Only retry what is retryable** (timeouts, 503, connection resets), never client errors (400, 404) or non-idempotent calls without a key.

```python
import random

def backoff_delays(attempts, base=0.1, cap=5.0, rng=None):
    """'Full jitter': sleep a random time between 0 and min(cap, base * 2**attempt)."""
    rng = rng or random.Random()
    return [rng.uniform(0, min(cap, base * 2 ** n)) for n in range(attempts)]

def retry(fn, attempts=5, base=0.1, cap=5.0, rng=None, sleep=lambda s: None, retryable=(TimeoutError,)):
    delays = backoff_delays(attempts - 1, base, cap, rng)
    for n in range(attempts):
        try:
            return fn()
        except retryable as exc:
            if n == attempts - 1:
                raise                                   # out of attempts: give up loudly
            sleep(delays[n])

calls = {"n": 0}
def flaky():
    calls["n"] += 1
    if calls["n"] < 4:
        raise TimeoutError("slow server")
    return f"succeeded on call {calls['n']}"

waited = []
print(retry(flaky, rng=random.Random(1), sleep=waited.append))
print("slept", len(waited), "times; each wait is no longer than its ceiling:",
      all(w <= min(5.0, 0.1 * 2 ** i) for i, w in enumerate(waited)))
# succeeded on call 4
# slept 3 times; each wait is no longer than its ceiling: True

# without jitter every client waits exactly the same time; with jitter they spread out
no_jitter = {round(min(5.0, 0.1 * 2 ** 3), 2) for _ in range(100)}
with_jitter = {round(backoff_delays(4, rng=random.Random(seed))[3], 2) for seed in range(100)}
print(len(no_jitter), "distinct wait without jitter vs", len(with_jitter) > 50, "(many) with jitter")
# 1 distinct wait without jitter vs True (many) with jitter
```

(The `sleep` parameter is injectable so tests run instantly; pass `time.sleep` in production.) Also propagate a **deadline** through call chains so a request that is already too late is abandoned instead of retried at every layer (retries multiply: 3 layers each retrying 3 times means up to 27 calls to the bottom).

## 4. Circuit breaker

If a dependency is down, calling it repeatedly wastes threads, adds latency and prevents its recovery. A **circuit breaker** watches failures and **fails fast** while the dependency is unhealthy:

- **Closed:** calls pass through; failures are counted.
- **Open:** after N consecutive failures, calls are rejected immediately for a cool-down period.
- **Half-open:** after the cool-down, one trial call is allowed; success closes the breaker, failure re-opens it.

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=3, cooldown=10.0, clock=None):
        self.threshold, self.cooldown, self.clock = failure_threshold, cooldown, clock
        self.failures, self.opened_at, self.state = 0, None, "closed"

    def call(self, fn):
        if self.state == "open":
            if self.clock() - self.opened_at >= self.cooldown:
                self.state = "half-open"                  # allow one trial request
            else:
                raise RuntimeError("circuit open: failing fast")
        try:
            result = fn()
        except Exception:
            self.failures += 1
            if self.state == "half-open" or self.failures >= self.threshold:
                self.state, self.opened_at = "open", self.clock()
            raise
        self.failures, self.state = 0, "closed"
        return result

now = [0.0]                                               # a fake clock we control
breaker = CircuitBreaker(failure_threshold=3, cooldown=10.0, clock=lambda: now[0])
healthy = [False]
def dependency():
    if not healthy[0]:
        raise TimeoutError("down")
    return "fine"

for i in range(5):
    try:
        breaker.call(dependency)
    except Exception as e:
        print(f"t={now[0]:>4}  call {i + 1}: {type(e).__name__}: {e}   state={breaker.state}")
# t= 0.0  call 1: TimeoutError: down   state=closed
# t= 0.0  call 2: TimeoutError: down   state=closed
# t= 0.0  call 3: TimeoutError: down   state=open
# t= 0.0  call 4: RuntimeError: circuit open: failing fast   state=open
# t= 0.0  call 5: RuntimeError: circuit open: failing fast   state=open

now[0] = 11.0; healthy[0] = True                          # cool-down passed and the dependency recovered
print(breaker.call(dependency), breaker.state)
# fine closed
```

Combine the patterns: **timeout** on every call, **bounded retries with backoff and jitter** for transient errors, a **circuit breaker** for persistent ones, **bulkheads** (separate thread or connection pools per dependency) and a **fallback** (cached data or a degraded response).

## 5. Sagas: distributed business transactions without 2PC

A single database transaction gives all-or-nothing across tables. When one business operation spans **several services, each with its own database** (orders, payments, inventory), no single transaction covers them. The **saga** pattern runs a sequence of **local transactions**; if step *k* fails, run **compensating actions** for steps *k-1 ... 1* in reverse (refund, release stock).

```python
class Saga:
    def __init__(self):
        self.steps = []                                    # (name, action, compensation)
    def step(self, name, action, compensation):
        self.steps.append((name, action, compensation))
        return self
    def run(self, ctx):
        done = []
        for name, action, compensation in self.steps:
            try:
                action(ctx)
                done.append((name, compensation))
                ctx["log"].append(f"+ {name}")
            except Exception as exc:
                ctx["log"].append(f"! {name} failed: {exc}")
                for done_name, comp in reversed(done):     # undo what already succeeded, in reverse order
                    comp(ctx)
                    ctx["log"].append(f"- undo {done_name}")
                return False
        return True

def reserve_stock(ctx):  ctx["stock"] -= ctx["qty"]
def release_stock(ctx):  ctx["stock"] += ctx["qty"]
def charge_card(ctx):
    if ctx["balance"] < ctx["price"]:
        raise ValueError("insufficient funds")
    ctx["balance"] -= ctx["price"]
def refund_card(ctx):    ctx["balance"] += ctx["price"]
def create_shipment(ctx): ctx["shipped"] = True
def cancel_shipment(ctx): ctx["shipped"] = False

order_saga = (Saga().step("reserve stock", reserve_stock, release_stock)
                    .step("charge card", charge_card, refund_card)
                    .step("create shipment", create_shipment, cancel_shipment))

ok_ctx = {"stock": 10, "qty": 2, "balance": 100, "price": 60, "log": []}
print(order_saga.run(ok_ctx), ok_ctx["stock"], ok_ctx["balance"], ok_ctx["log"])
# True 8 40 ['+ reserve stock', '+ charge card', '+ create shipment']

bad_ctx = {"stock": 10, "qty": 2, "balance": 20, "price": 60, "log": []}
print(order_saga.run(bad_ctx), bad_ctx["stock"], bad_ctx["balance"], bad_ctx["log"])
# False 10 20 ['+ reserve stock', '! charge card failed: insufficient funds', '- undo reserve stock']
```

Sagas trade the "I" in ACID for availability: other users may briefly see the intermediate state (stock reserved, payment not yet taken), so design states like `PENDING` and make **both actions and compensations idempotent** (they can be retried). Two styles: **orchestration** (a coordinator tells each service what to do, as above) and **choreography** (services react to each other's events, with no central controller). Some actions cannot be undone (an email already sent), so put those **last** or make the compensation a follow-up message.

## 6. The transactional outbox

A frequent trap: "save the order in the database, then publish an `OrderCreated` event." If the process crashes between the two, the order exists but the event is lost; if you publish first, the event may announce an order that never saved. You cannot make a database write and a message-broker write atomic. The **outbox pattern** writes the event into an `outbox` table **in the same local transaction** as the business data; a separate **relay** publishes outbox rows and marks them sent. Delivery becomes **at-least-once**, so consumers deduplicate by event id (idempotency again).

```python
import json, sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE orders (id INTEGER PRIMARY KEY, item TEXT);
CREATE TABLE outbox (event_id INTEGER PRIMARY KEY AUTOINCREMENT, payload TEXT, sent INTEGER DEFAULT 0);
""")

def create_order(item):
    with db:                                               # ONE transaction: both rows commit together or neither does
        cur = db.execute("INSERT INTO orders (item) VALUES (?)", (item,))
        db.execute("INSERT INTO outbox (payload) VALUES (?)", (json.dumps({"type": "OrderCreated", "order_id": cur.lastrowid}),))

broker, processed = [], set()                              # the "message broker" and a consumer's dedup memory

def relay(crash_after_publish=False):
    for event_id, payload in db.execute("SELECT event_id, payload FROM outbox WHERE sent = 0 ORDER BY event_id").fetchall():
        broker.append((event_id, payload))                 # publish first...
        if crash_after_publish:
            return                                          # ...crash before marking sent: the event will be published AGAIN
        db.execute("UPDATE outbox SET sent = 1 WHERE event_id = ?", (event_id,))
        db.commit()

def consume():
    handled = []
    for event_id, payload in broker:
        if event_id in processed:                          # duplicate delivery: ignore (idempotent consumer)
            continue
        processed.add(event_id)
        handled.append(json.loads(payload)["order_id"])
    return handled

create_order("book")
relay(crash_after_publish=True)                            # crash after publishing, before marking
relay()                                                    # relay restarts and publishes the same row again
print("events on the broker:", len(broker), "| orders handled by the consumer:", consume())
# events on the broker: 2 | orders handled by the consumer: [1]
```

The event reached the broker **twice** (at-least-once) but was **processed once** thanks to the consumer's deduplication; and it was **never lost**. (Change-data-capture tools such as Debezium can read the outbox from the database log instead of polling.)

## 7. Why two-phase commit is usually avoided

**Two-phase commit (2PC)** gives true atomicity across databases: phase 1, a coordinator asks every participant to **prepare** (and promise it can commit); phase 2, if all said yes it tells them to **commit**, otherwise to abort. The weakness is **blocking**: once a participant has voted yes it must hold its locks and wait for the coordinator's decision. If the coordinator crashes after collecting votes, participants are stuck "in doubt" holding locks until it returns.

```python
def two_phase_commit(participants_vote, coordinator_crashes_after_votes=False):
    if not all(participants_vote.values()):
        return "ABORT: someone voted no", {p: "released" for p in participants_vote}
    if coordinator_crashes_after_votes:
        return "BLOCKED: coordinator died before deciding", {p: "holding locks, in doubt" for p in participants_vote}
    return "COMMIT", {p: "committed" for p in participants_vote}

print(two_phase_commit({"orders": True, "payments": True}))
print(two_phase_commit({"orders": True, "payments": False}))
print(two_phase_commit({"orders": True, "payments": True}, coordinator_crashes_after_votes=True))
# ('COMMIT', {'orders': 'committed', 'payments': 'committed'})
# ('ABORT: someone voted no', {'orders': 'released', 'payments': 'released'})
# ('BLOCKED: coordinator died before deciding', {'orders': 'holding locks, in doubt', 'payments': 'holding locks, in doubt'})
```

2PC is used inside some databases (and across XA resources) but across microservices it hurts availability and throughput. Alternatives: sagas (eventual consistency), or **consensus-backed** commit protocols (Spanner, CockroachDB run 2PC over Raft groups so the coordinator cannot be lost).

## 8. Common mistakes

- Retrying non-idempotent operations without an idempotency key.
- Retrying immediately and without limits (retry storms), or retrying at every layer.
- Treating all errors as retryable (a 400 will fail the same way forever).
- A circuit breaker with no fallback, so failing fast just means failing.
- Compensations that are not idempotent or that can themselves fail silently.
- Writing to the database and the message broker as two separate steps.
- Assuming exactly-once delivery exists; what exists is **at-least-once delivery plus idempotent processing**, which has the same effect.
- Idempotency keys generated **per attempt** instead of **per operation**.

## 9. Two real-world examples

**Example 1: The double shipment.** A warehouse system consumed "order paid" messages from a queue. A broker failover redelivered the last 200 messages and 200 parcels were shipped twice. Adding a `processed_events` table with a unique constraint on the event id turned redelivery into a harmless no-op.

**Example 2: The outage amplifier.** A search service slowed down; every client timed out after 1 s and retried 3 times immediately, tripling the load on the struggling service, which then failed completely. After adding exponential backoff with jitter, a retry budget (at most 10 percent extra traffic) and circuit breakers, later slowdowns healed on their own.

## 10. Practice

1. Make the `retry` function also accept a `deadline` (total seconds budget) and stop retrying when the next sleep would exceed it.
2. Why is `UPDATE accounts SET balance = balance - 10 WHERE id = 1` not idempotent, and how would you make a money transfer idempotent?
3. Add a fourth step "send confirmation email" to the saga. Where should it go and why?
4. In the circuit breaker, what happens in `half-open` state if the trial call fails? Trace it.
5. A consumer crashes after processing a message but before acknowledging it. What happens on restart, and what must the handler do?
6. Compute the worst-case number of calls to the bottom service when 3 layers each make up to 3 attempts.

<details>
<summary>Solutions</summary>

1. ```python
   def retry_with_deadline(fn, budget, base=0.1, rng=None, retryable=(TimeoutError,)):
       rng = rng or random.Random(0)
       spent, n = 0.0, 0
       while True:
           try:
               return fn()
           except retryable:
               wait = rng.uniform(0, min(5.0, base * 2 ** n))
               if spent + wait > budget:
                   raise
               spent += wait
               n += 1
   calls["n"] = 0
   print(retry_with_deadline(flaky, budget=10))
   # succeeded on call 4
   ```
2. Running it twice subtracts 20. Give each transfer a unique id and record `transfer_id` in a table with a unique constraint **in the same transaction** as the balance update; a repeat hits the constraint and does nothing.
3. Last, after shipment: an email cannot be un-sent, so run it only when nothing after it can fail (or make its compensation "send a cancellation").
4. The next call is allowed through; it raises, so `self.state == "half-open"` triggers `state = "open"` and `opened_at = now`; the cool-down starts again.
5. The broker redelivers the message (it was never acknowledged), so the handler runs again; it must be idempotent (record processed ids, or make the effect repeat-safe).
6. `3 * 3 * 3 = 27` calls: each layer multiplies the attempts below it.

</details>

## 11. Check yourself

1. What does idempotent mean, and which of `SET x=5` and `x += 5` is idempotent?
2. How does an idempotency key work, and who generates it?
3. Why add jitter to exponential backoff?
4. Describe the three circuit breaker states.
5. What is a saga, and what is a compensating action?
6. What problem does the outbox pattern solve?
7. Why does two-phase commit hurt availability?

<details>
<summary>Answers</summary>

1. Doing it twice equals doing it once; `SET x=5` is idempotent, `x += 5` is not.
2. The client creates one unique key per logical operation and sends it on every retry; the server stores the result under the key and returns it instead of repeating the work.
3. Without jitter all clients retry at the same instants, producing synchronized bursts; randomising spreads the load.
4. Closed (normal, counting failures), open (reject immediately during a cool-down), half-open (allow one trial; success closes, failure re-opens).
5. A sequence of local transactions across services; if one fails, compensating actions undo the earlier steps (for example refund a charge).
6. It makes "update the database and publish an event" atomic by writing the event into the same local transaction, with a relay delivering it at-least-once.
7. Participants that voted yes hold locks until the coordinator decides, so a coordinator failure blocks them.

</details>

[Back to Distributed Systems](../README.md)
