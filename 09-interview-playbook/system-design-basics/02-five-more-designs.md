# System Design, Part 2: Five More Designs

**Prerequisites:** [System design basics](README.md) (framework, estimation, building blocks, URL shortener, news feed, chat), [replication and sharding](../../11-distributed-systems/replication-sharding/01-replication-and-sharding.md), [idempotency and sagas](../../11-distributed-systems/transactions/01-idempotency-retries-and-sagas.md). **You will learn:** five classic design problems, each with requirements, a back-of-the-envelope estimate, the core data structure or algorithm **implemented and run in Python**, and the trade-offs an interviewer will probe: **a rate limiter** (three algorithms compared), **a notification service**, **a payment ledger**, **search autocomplete** and **file storage with deduplication**.

Use the same framework as in part 1: clarify requirements, estimate scale, sketch the high-level design, deep-dive one or two components, then discuss bottlenecks and failures.

## Design 1: A rate limiter

**Requirements:** limit each client to N requests per time window across a fleet of API servers; low overhead (it runs on every request); clear rejection (HTTP 429 with a `Retry-After` header). **Estimate:** 100,000 requests per second, 10 million distinct clients: counters must be in a **fast shared store** (Redis) with small per-client state.

Three algorithms (the [token bucket](README.md) is the fourth, allowing bursts):

```python
from collections import deque

class FixedWindow:
    """Count per window of fixed length. Cheap but allows a double burst at the boundary."""
    def __init__(self, limit, window, clock):
        self.limit, self.window, self.clock = limit, window, clock
        self.window_id, self.count = None, 0
    def allow(self):
        wid = int(self.clock() // self.window)
        if wid != self.window_id:
            self.window_id, self.count = wid, 0
        if self.count < self.limit:
            self.count += 1
            return True
        return False

class SlidingWindowLog:
    """Remember each request time; exact but stores up to `limit` timestamps per client."""
    def __init__(self, limit, window, clock):
        self.limit, self.window, self.clock, self.times = limit, window, clock, deque()
    def allow(self):
        now = self.clock()
        while self.times and self.times[0] <= now - self.window:
            self.times.popleft()
        if len(self.times) < self.limit:
            self.times.append(now)
            return True
        return False

class SlidingWindowCounter:
    """Two counters with weighting: nearly exact, two numbers per client."""
    def __init__(self, limit, window, clock):
        self.limit, self.window, self.clock = limit, window, clock
        self.current_id, self.current, self.previous = None, 0, 0
    def allow(self):
        now = self.clock()
        wid = int(now // self.window)
        if wid != self.current_id:
            self.previous = self.current if self.current_id is not None and wid == self.current_id + 1 else 0
            self.current_id, self.current = wid, 0
        overlap = 1 - (now % self.window) / self.window                 # how much of the previous window is still in range
        if self.previous * overlap + self.current < self.limit:
            self.current += 1
            return True
        return False

def burst_test(cls):
    t = [0.0]
    limiter = cls(limit=5, window=10, clock=lambda: t[0])
    t[0] = 9.9
    first = sum(limiter.allow() for _ in range(5))                      # five requests just before the boundary
    t[0] = 10.1
    second = sum(limiter.allow() for _ in range(5))                     # five more just after it
    return first, second

for cls in (FixedWindow, SlidingWindowLog, SlidingWindowCounter):
    first, second = burst_test(cls)
    print(f"{cls.__name__:<20} allowed {first} then {second}  (total {first + second} within 0.2 s; the limit is 5 per 10 s)")
# FixedWindow          allowed 5 then 5  (total 10 within 0.2 s; the limit is 5 per 10 s)
# SlidingWindowLog     allowed 5 then 0  (total 5 within 0.2 s; the limit is 5 per 10 s)
# SlidingWindowCounter allowed 5 then 1  (total 6 within 0.2 s; the limit is 5 per 10 s)
```

| Algorithm | Memory per client | Accuracy | Notes |
|-----------|------------------|----------|-------|
| Fixed window | 1 counter | allows 2x limit across a boundary | simplest, often good enough |
| Sliding log | up to N timestamps | exact | expensive for large N |
| Sliding counter | 2 counters | approximate (here it let 1 extra request through) | good default |
| Token bucket | 2 numbers | smooths and allows bursts | what many gateways use |

**Deep dive.** Share state in Redis; make check-and-increment **atomic** (a Lua script or `INCR` with `EXPIRE`) or two servers can both let the 5th request through. Key by API key, user id or IP (IP alone punishes shared NATs). Decide **fail open** (allow if Redis is down, favouring availability) or **fail closed** (protect the backend). Return `429` with `Retry-After`; apply limits at the edge or gateway, with a stricter limit on sensitive routes such as login ([security](../../10-security/authentication/01-authn-authz-sessions-jwt.md)). To avoid a Redis round trip on every request, servers can keep local counters and sync periodically at the cost of slight over-admission.

## Design 2: A notification service

**Requirements:** send email, SMS and push notifications triggered by other services; respect user preferences and quiet hours; never send duplicates; retry failures; handle spikes (a marketing blast of 10 million). **Estimate:** 10 million notifications in an hour is about 2,800 per second, bursty; the channel providers (SMS, email gateways) have their own rate limits, so a **queue** between producers and workers is essential.

Architecture: producers call an API, which **validates, deduplicates and enqueues**; **per-channel queues** feed worker pools that call providers with **retry and backoff**; failures after N attempts go to a **dead-letter queue**; a status store feeds dashboards and "was it delivered?" queries. The core logic:

```python
import heapq

class NotificationService:
    def __init__(self, providers, quiet_hours=(22, 7)):
        self.providers = providers                          # channel -> function(user, text) that may raise
        self.quiet = quiet_hours
        self.queue = []                                     # (send_at, priority, seq, notification)
        self.seen, self.sent, self.dead, self.seq = set(), [], [], 0

    def submit(self, dedupe_key, user, channel, text, hour, priority=5, send_at=0):
        if dedupe_key in self.seen:
            return "duplicate ignored"                       # idempotency: the same event never notifies twice
        self.seen.add(dedupe_key)
        if priority > 1 and (hour >= self.quiet[0] or hour < self.quiet[1]):
            send_at = max(send_at, 7 * 3600 + 0)             # defer non-urgent messages to 07:00 (seconds)
        self.seq += 1
        heapq.heappush(self.queue, (send_at, priority, self.seq, {"user": user, "channel": channel, "text": text, "attempts": 0}))
        return "queued"

    def run(self, now, max_attempts=3):
        while self.queue and self.queue[0][0] <= now:
            send_at, priority, seq, n = heapq.heappop(self.queue)
            try:
                self.providers[n["channel"]](n["user"], n["text"])
                self.sent.append((n["user"], n["channel"], n["text"]))
            except ConnectionError:
                n["attempts"] += 1
                if n["attempts"] >= max_attempts:
                    self.dead.append(n)                       # give up: dead-letter queue for a human or a later replay
                else:
                    delay = 30 * 2 ** n["attempts"]           # exponential backoff
                    heapq.heappush(self.queue, (now + delay, priority, seq, n))

outbox = []
def email_ok(user, text):   outbox.append(("email", user, text))
def sms_down(user, text):   raise ConnectionError("sms gateway down")

svc = NotificationService({"email": email_ok, "sms": sms_down})
print(svc.submit("order-1:shipped", "ada", "email", "Your order shipped", hour=14))
print(svc.submit("order-1:shipped", "ada", "email", "Your order shipped", hour=14))       # same event again
print(svc.submit("promo-9", "ada", "email", "50% off", hour=23, priority=5))                # night: deferred
print(svc.submit("otp-77", "ada", "sms", "Your code is 4821", hour=23, priority=1))          # urgent: sent now, provider is down
# queued
# duplicate ignored
# queued
# queued

svc.run(now=0)
print("sent now:", [t for _, _, t in svc.sent])
# sent now: ['Your order shipped']
for t in (60, 180, 400):                                      # retries of the SMS: backoff 60 s, 120 s, then give up
    svc.run(now=t)
print("dead letters:", [(d["channel"], d["attempts"]) for d in svc.dead], "| promo still waiting until 07:00:", len(svc.queue) == 1)
svc.run(now=7 * 3600)
print("sent by morning:", [t for _, _, t in svc.sent])
# dead letters: [('sms', 3)] | promo still waiting until 07:00: True
# sent by morning: ['Your order shipped', '50% off']
```

**Deep dive.** **Deduplicate** with an idempotency key stored in a database with a unique constraint (not an in-memory set, as here). **Fan-out** big blasts by splitting recipients into batches so one campaign cannot starve urgent traffic: separate queues and priorities. Respect provider **rate limits** (a token bucket per provider) and **user preferences** (a preferences service cached near the workers). Track delivery status via provider webhooks. Template rendering and localisation happen in the worker. Failure modes: provider outage (switch provider, circuit breaker), poison messages (DLQ), duplicate sends on redelivery (idempotent workers), and "notification fatigue" (rate limit per user).

## Design 3: A payment ledger

**Requirements:** move money between accounts correctly: **never lose or create money**, never double-process a retry, keep a full audit trail, and make balances verifiable. **Estimate:** 1,000 transfers per second is modest in volume but **correctness** dominates: this is a place for a relational database with strong transactions, not an eventually consistent store.

The core idea of **double-entry bookkeeping**: every transfer writes **two or more entries that sum to zero** (a debit and a credit). Balances are not stored values you overwrite but **derived from an append-only list of entries**, so history is never lost and the invariant "total of all entries = 0" is easy to audit.

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE accounts (id TEXT PRIMARY KEY, allow_negative INTEGER DEFAULT 0);
CREATE TABLE transfers (idempotency_key TEXT PRIMARY KEY, src TEXT, dst TEXT, amount INTEGER CHECK (amount > 0));
CREATE TABLE entries (id INTEGER PRIMARY KEY AUTOINCREMENT, transfer_key TEXT, account TEXT, delta INTEGER);   -- cents; positive = credit
INSERT INTO accounts VALUES ('bank', 1), ('ada', 0), ('bob', 0);
""")

def balance(account):
    return db.execute("SELECT COALESCE(SUM(delta), 0) FROM entries WHERE account = ?", (account,)).fetchone()[0]

def transfer(key, src, dst, amount):
    try:
        with db:                                                      # one atomic transaction: all rows or none
            db.execute("INSERT INTO transfers VALUES (?, ?, ?, ?)", (key, src, dst, amount))       # unique key = idempotency
            allow_negative = db.execute("SELECT allow_negative FROM accounts WHERE id = ?", (src,)).fetchone()[0]
            if not allow_negative and balance(src) < amount:
                raise ValueError("insufficient funds")                # rolls back the transfer row too
            db.execute("INSERT INTO entries (transfer_key, account, delta) VALUES (?, ?, ?)", (key, src, -amount))
            db.execute("INSERT INTO entries (transfer_key, account, delta) VALUES (?, ?, ?)", (key, dst, +amount))
        return "ok"
    except sqlite3.IntegrityError:
        return "duplicate request: already processed"                # a retry of the same transfer
    except ValueError as e:
        return str(e)

print(transfer("t1", "bank", "ada", 10_000))          # fund Ada with 100.00
print(transfer("t2", "ada", "bob", 3_500))
print(transfer("t2", "ada", "bob", 3_500))            # the client retried after a timeout
print(transfer("t3", "ada", "bob", 99_999))           # more than she has
# ok
# ok
# duplicate request: already processed
# insufficient funds
print({a: balance(a) for a in ("bank", "ada", "bob")}, "| sum of all balances:", sum(balance(a) for a in ("bank", "ada", "bob")))
# {'bank': -10000, 'ada': 6500, 'bob': 3500} | sum of all balances: 0
```

**Deep dive.** Use **integer minor units** (cents), never floats. The idempotency key has a **unique constraint in the same transaction** as the entries. Lock the source account row (`SELECT ... FOR UPDATE`) so two concurrent transfers cannot both pass the balance check (the demo uses SQLite's single writer; in PostgreSQL use `FOR UPDATE`, see [PostgreSQL features](../../05-databases/postgresql/01-postgresql-specific-features.md)). Cross-bank or cross-service payments use a [saga](../../11-distributed-systems/transactions/01-idempotency-retries-and-sagas.md) with states `PENDING`, `COMPLETED`, `FAILED` and reconciliation jobs that compare your ledger with the bank's statements daily. Scale by sharding on account id, keeping each transfer's two accounts on the same shard where possible. Keep entries immutable: corrections are **new reversing entries**, never edits.

## Design 4: Search autocomplete (typeahead)

**Requirements:** as the user types a prefix, return the top 5 popular completions within about 100 ms; update popularity from recent searches; handle 10,000 queries per second at peak. **Estimate:** 10 million distinct queries at about 20 bytes: roughly 200 MB, so the whole index fits in memory on one machine, replicated for load.

A **trie** (prefix tree, see [tries](../../02-data-structures/tries/README.md)) finds the prefix node in O(length). Storing the **top-k completions at every node** makes each query O(prefix length) instead of walking the whole subtree.

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.top = []                                       # up to K (count, word) pairs, best first

K = 3

class Autocomplete:
    def __init__(self):
        self.root, self.counts = TrieNode(), {}

    def record(self, word, times=1):
        self.counts[word] = self.counts.get(word, 0) + times
        node = self.root
        for ch in word:                                     # update the top-k list at every prefix of the word
            node = node.children.setdefault(ch, TrieNode())
            entry = (self.counts[word], word)
            node.top = [e for e in node.top if e[1] != word] + [entry]
            node.top = sorted(node.top, key=lambda e: (-e[0], e[1]))[:K]

    def suggest(self, prefix):
        node = self.root
        for ch in prefix:
            node = node.children.get(ch)
            if node is None:
                return []
        return [w for _, w in node.top]

ac = Autocomplete()
for word, times in [("python", 50), ("pytest", 20), ("pytorch", 30), ("python tutorial", 40), ("java", 60), ("javascript", 45)]:
    ac.record(word, times)
print(ac.suggest("py"))
print(ac.suggest("pyt"))
print(ac.suggest("jav"), ac.suggest("zzz"))
# ['python', 'python tutorial', 'pytorch']
# ['python', 'python tutorial', 'pytorch']
# ['java', 'javascript'] []
ac.record("pytest", 100)                                    # a burst of searches for pytest
print(ac.suggest("py"))
# ['pytest', 'python', 'python tutorial']
```

**Deep dive.** Do **not** update the trie on every keystroke: log searches, **aggregate offline** every few minutes or hours (a batch job counting queries, optionally weighted toward recent ones), build a fresh trie and **swap it in** atomically; real-time updates only for trending queries. Cache popular prefixes (`"a"`, `"ho"`) in Redis or the CDN, since short prefixes are the hottest. Shard the trie by first letter(s) if it outgrows memory; a replica set serves reads. Add **typo tolerance** (edit distance, see [worked problems](../worked-problems/02-graph-string-dp-and-design-rounds.md)), personalisation, filtering of offensive or private queries, and debounce requests on the client (send after a short pause or at 2 to 3 characters).

## Design 5: File storage with chunking and deduplication

**Requirements:** upload and download large files (like Dropbox or Google Drive); resume interrupted uploads; avoid storing the same bytes twice; verify integrity. **Estimate:** 100 million users at 5 GB average is 500 PB of logical data, so **deduplication and compression** matter; metadata (names, folders, versions) is small and relational, the chunks are huge and go in object storage.

Split files into **chunks**, name each chunk by the **hash of its content** (**content-addressed storage**), and store a **manifest** (the ordered list of chunk hashes) per file. Identical chunks (across files, versions and users) are stored once.

```python
import hashlib

CHUNK = 16                                                     # bytes; real systems use roughly 4 MB

class ChunkStore:
    def __init__(self):
        self.chunks = {}                                       # sha256 hex -> bytes   (stands in for object storage)
        self.manifests = {}                                    # file name -> [hash, hash, ...]
        self.bytes_stored = 0

    @staticmethod
    def split(data):
        return [data[i:i + CHUNK] for i in range(0, len(data), CHUNK)]

    def missing(self, hashes):
        """Resumable and dedup-friendly upload: the client asks which chunks the server does not have yet."""
        return [h for h in hashes if h not in self.chunks]

    def upload(self, name, data):
        pieces = self.split(data)
        hashes = [hashlib.sha256(p).hexdigest() for p in pieces]
        needed = set(self.missing(hashes))
        sent = 0
        for p, h in zip(pieces, hashes):
            if h in needed:
                self.chunks[h] = p
                self.bytes_stored += len(p)
                needed.discard(h)
                sent += len(p)
        self.manifests[name] = hashes
        return sent

    def download(self, name):
        data = b"".join(self.chunks[h] for h in self.manifests[name])
        return data

store = ChunkStore()
v1 = b"The quick brown fox jumps over the lazy dog. " * 4
sent1 = store.upload("report_v1.txt", v1)
v2 = v1 + b"An appended sentence."                              # a new version: only the tail differs
sent2 = store.upload("report_v2.txt", v2)
print(f"v1: {len(v1)} bytes, uploaded {sent1}")
print(f"v2: {len(v2)} bytes, uploaded only {sent2} (the unchanged chunks already existed)")
print("stored in total:", store.bytes_stored, "bytes instead of", len(v1) + len(v2))
print("round trip intact:", store.download("report_v2.txt") == v2)
# v1: 180 bytes, uploaded 180
# v2: 201 bytes, uploaded only 25 (the unchanged chunks already existed)
# stored in total: 205 bytes instead of 381
# round trip intact: True
```

The first upload sends all 180 bytes (11 full chunks plus a 4-byte tail). Version 2 appends 21 bytes, so only the changed tail chunk and the new chunk (16 + 9 = 25 bytes) are sent; the first 11 chunks already exist on the server. Total stored: 205 bytes instead of 381. **Fixed-size chunking has a weakness:** inserting one byte at the start shifts every later chunk boundary, so nothing matches. Real systems (rsync, Dropbox, backup tools) use **content-defined chunking** (a rolling hash decides boundaries, so they move with the content) to keep dedup working after insertions.

**Deep dive.** Components: **metadata service** (file tree, versions, permissions; a sharded SQL database), **block service** (chunks in object storage, replicated or erasure-coded), **upload sessions** (the client uploads chunks in parallel and resumes by asking `missing`), a **sync notification** channel (long poll or WebSocket) so other devices fetch changes, and **garbage collection** (reference counts or mark-and-sweep over manifests; never delete a chunk another manifest uses). Encrypt at rest and in transit; beware **cross-user dedup** privacy leaks (an attacker can learn whether a file exists by checking whether an upload was skipped), so many services dedupe only within one account or require proof of possession.

## Common mistakes in these designs

- A rate limiter that is not atomic across servers, or that trusts `X-Forwarded-For` blindly.
- Sending notifications synchronously from the request path instead of via a queue; no dedupe key; no quiet hours.
- Storing balances as floats, or overwriting a balance without an entries history.
- Updating the autocomplete index on every keystroke instead of aggregating.
- Naming chunks by file name instead of content hash, losing dedup and integrity checking.
- Designing for peak throughput without estimating (see [estimation](README.md)).
- Skipping failure modes: what if Redis, the provider, the shard or the queue is down?

## Practice

1. For the rate limiter, add a `retry_after()` method to `FixedWindow` returning seconds until the next window.
2. Extend the notification service so an SMS that fails over to email after exhausting its retries (fallback channel).
3. In the ledger, write `reverse(key, new_key)` that creates a compensating transfer undoing transfer `key`. Why reverse rather than delete?
4. Add `delete(word)` handling to the autocomplete (hint: recompute `top` for each prefix node on the path).
5. Estimate: 50,000 requests/s rate limiting with a 60-second window and up to 100 requests per client: memory for the sliding log versus the sliding counter for 1 million active clients.
6. Content-defined chunking: why does it keep dedup working after inserting bytes at the start of a file?

<details>
<summary>Solutions</summary>

1. ```python
   def retry_after(self):
       return self.window - (self.clock() % self.window)
   FixedWindow.retry_after = retry_after
   t = [3.0]
   fw = FixedWindow(1, 10, lambda: t[0])
   fw.allow()
   print(fw.allow(), round(fw.retry_after(), 1))
   # False 7.0
   ```
2. ```python
   def run_with_fallback(svc, now, fallback_channel="email"):
       svc.run(now)
       while svc.dead:
           n = svc.dead.pop()
           svc.submit(f"fallback:{n['user']}:{n['text']}", n["user"], fallback_channel, n["text"], hour=12, priority=1, send_at=now)
       svc.run(now)
   run_with_fallback(svc, 8 * 3600)
   print([(ch, t) for _, ch, t in svc.sent if t.startswith("Your code")])
   # [('email', 'Your code is 4821')]
   ```
3. ```python
   def reverse(key, new_key):
       src, dst, amount = db.execute("SELECT src, dst, amount FROM transfers WHERE idempotency_key = ?", (key,)).fetchone()
       return transfer(new_key, dst, src, amount)
   print(reverse("t2", "t2-reversal"), {a: balance(a) for a in ("ada", "bob")})
   # ok {'ada': 10000, 'bob': 0}
   ```
   Deleting rows would erase the history and break audit and reconciliation; a reversing entry keeps both the original and its correction.
4. Remove the word from `counts`, then for every prefix node on its path recompute `top` from the words still present under that prefix (or keep a larger candidate list and drop the word). The simplest correct approach for small data: rebuild the trie from `counts` after the batch of deletions.
5. Sliding log: up to 100 timestamps at 8 bytes is 800 bytes per client, about **800 MB** for 1 million clients (plus overhead). Sliding counter: two counters at about 16 bytes, about **16 MB**. That is a 50x saving at the cost of approximate counting.
6. A rolling hash over a window of bytes marks a boundary wherever the hash matches a pattern, so boundaries depend on the **local content**, not the offset. Inserting bytes only changes the chunk(s) around the insertion; later boundaries land at the same content positions as before, so those chunks hash identically.

</details>

## Check yourself

1. Why does a fixed-window limiter allow twice the limit around a boundary, and how does the sliding window avoid it?
2. Why must a notification service deduplicate, and where should the dedupe key live?
3. What is double-entry bookkeeping and what invariant does it give?
4. Why store top-k at each trie node, and why update the index offline?
5. What does content-addressed storage give you?
6. Where would a rate limiter fail open versus closed, and why?

<details>
<summary>Answers</summary>

1. Requests just before and just after a window boundary are counted in different windows, so up to 2N pass within a short span; a sliding window counts requests over the last N seconds regardless of boundaries.
2. Producers retry and brokers redeliver; without a key each retry sends another message. Keep the key in a durable store with a unique constraint so it survives restarts and is shared by all workers.
3. Every transfer writes balanced entries (debits and credits that sum to zero); the total of all entries stays 0, which is easy to audit, and balances derive from immutable history.
4. A precomputed top-k answers a prefix query in O(length of prefix) with no subtree walk; updating per keystroke is too expensive and noisy, so periodic batch aggregation swaps in a fresh index.
5. Automatic deduplication (identical bytes are stored once), integrity verification (the name is the hash), easy resumable uploads and immutable data that is simple to cache and replicate.
6. Fail open when availability matters more than strict limiting (public read APIs); fail closed when the limit protects something fragile or security-sensitive (login, expensive operations).

</details>

[Back to System Design Basics](README.md)
