# Failures, Time and Clocks in Distributed Systems

**Prerequisites:** [TCP/IP and sockets](../../07-networking/tcp-ip-osi/README.md), [processes and threads](../../06-operating-systems/processes-threads/README.md), [classes in Python](../../04-oop/classes-objects/README.md). **You will learn:** why distributed systems are hard (**partial failure** and **no shared clock**), the standard **failure models**, how to build a **deterministic simulated network** to experiment safely, why wall clocks cannot order events, and how **Lamport clocks** and **vector clocks** capture "happened before" and detect concurrent updates, all implemented and run below.

## 1. In plain words

One program on one computer either works or crashes, and everything inside shares one clock and one memory. A **distributed system** is several computers cooperating over a network, and three things change:

1. **Partial failure:** some parts fail while others keep running, and you often cannot tell which.
2. **Unreliable network:** messages can be lost, delayed, duplicated or reordered.
3. **No shared clock:** each machine's clock drifts differently, so "at the same time" has no precise meaning.

If you send a request and get no reply, three different things could have happened: the request was lost, the server crashed, or the server did the work and the **reply** was lost. From the sender's side these look identical. Everything in this part of the handbook (replication, consensus, retries, idempotency) exists because of that ambiguity.

### The classic fallacies

Beginners assume (wrongly): the network is reliable; latency is zero; bandwidth is infinite; the network is secure; topology does not change; there is one administrator; transport cost is zero; the network is homogeneous.

## 2. Failure models

| Model | What a faulty node does | Example |
|-------|------------------------|---------|
| **Crash-stop** | stops forever | process killed, power lost |
| **Crash-recovery** | stops, later restarts (maybe losing memory, keeping disk) | server reboot |
| **Omission** | drops some messages | full buffer, firewall rule |
| **Timing (performance)** | answers too late | overloaded server, GC pause, slow disk |
| **Byzantine** | behaves arbitrarily, even maliciously | corrupted memory, hacked node, buggy firmware |

Most systems assume crash-recovery plus an unreliable network, and handle Byzantine faults only in special cases (blockchains, aircraft computers). A **timeout** is an imperfect **failure detector**: too short and you declare healthy nodes dead; too long and you wait on dead ones.

## 3. A deterministic simulated network

Experimenting on real networks is slow and unrepeatable. A **simulator** with a seeded random generator gives the same "bad luck" every run, which is how distributed algorithms are tested.

```python
import random

class Network:
    """Delivers messages with random loss, delay and duplication, deterministically (seeded)."""
    def __init__(self, seed=0, loss=0.0, max_delay=3, duplicate=0.0):
        self.rng = random.Random(seed)
        self.loss, self.max_delay, self.duplicate = loss, max_delay, duplicate
        self.now = 0
        self.in_flight = []                       # (deliver_at, order, dst, msg)
        self.counter = 0
        self.log = []

    def send(self, src, dst, msg):
        copies = 2 if self.rng.random() < self.duplicate else 1
        for _ in range(copies):
            if self.rng.random() < self.loss:
                self.log.append(("LOST", self.now, src, dst, msg))
                continue
            self.counter += 1
            self.in_flight.append((self.now + self.rng.randint(1, self.max_delay), self.counter, dst, msg))

    def tick(self):
        """Advance one time step and return the messages delivered now, as (dst, msg)."""
        self.now += 1
        due = sorted(m for m in self.in_flight if m[0] <= self.now)
        self.in_flight = [m for m in self.in_flight if m[0] > self.now]
        return [(dst, msg) for _, _, dst, msg in due]

net = Network(seed=2, loss=0.3, max_delay=3, duplicate=0.2)
for n in range(1, 9):
    net.send("A", "B", f"msg{n}")                 # A sends msg1..msg8 in order
received = []
for _ in range(6):
    received += [msg for _, msg in net.tick()]
print(received)
print("lost:", [e[4] for e in net.log])
# ['msg1', 'msg2', 'msg8', 'msg7', 'msg2', 'msg5', 'msg6']
# lost: ['msg3', 'msg4']
```

Look at what the receiver saw: `msg8` arrived **before** `msg7`; `msg2` arrived **twice**; `msg3` and `msg4` never arrived. Any protocol built on this must tolerate **loss, duplication and reordering**: that is why TCP numbers and acknowledges segments, and why [retries need idempotency](../transactions/01-idempotency-retries-and-sagas.md).

## 4. Why wall clocks cannot order events

Every machine has a clock that **drifts** (quartz crystals run slightly fast or slow) and is corrected by NTP, which itself can **jump** the time forwards or backwards. Two machines' clocks typically differ by milliseconds, sometimes seconds. Suppose A's clock is correct and B's is 5 seconds slow:

```python
class Node:
    def __init__(self, name, skew):
        self.name, self.skew = name, skew            # skew = how far this clock is from true time
    def clock(self, true_time):
        return true_time + self.skew

a, b = Node("A", 0), Node("B", -5)
events = [("A sends order", a.clock(100)), ("B receives order", b.clock(101))]   # true order: send, then receive
for name, ts in sorted(events, key=lambda e: e[1]):
    print(ts, name)
# 96 B receives order
# 100 A sends order
```

Sorting by timestamp says the order was **received before it was sent**, which is impossible. Using wall clocks to order events across machines (for example "last write wins by timestamp") silently loses writes. We need a clock that respects **causality**.

## 5. Happened-before and Lamport clocks

Leslie Lamport defined **happened-before** (written `a → b`): if `a` and `b` are in the same process and `a` comes first, or `a` is sending a message and `b` is its receipt, then `a → b` (and the relation is transitive). Events with no such chain are **concurrent**.

A **Lamport clock** is a counter per process:

1. Before each local event or send, increment the counter.
2. A message carries the sender's counter.
3. On receive, set `counter = max(own, received) + 1`.

```python
class LamportClock:
    def __init__(self, name):
        self.name, self.t = name, 0
    def event(self, what):
        self.t += 1
        print(f"  {self.name} t={self.t}: {what}")
        return self.t
    def send(self, what):
        return self.event("send " + what)            # the timestamp travels with the message
    def receive(self, what, ts):
        self.t = max(self.t, ts)
        return self.event("receive " + what)

A, B, C = LamportClock("A"), LamportClock("B"), LamportClock("C")
A.event("local work")
ts1 = A.send("m1 to B")
B.event("unrelated work")
B.receive("m1 from A", ts1)
ts2 = B.send("m2 to C")
C.event("independent event")
C.receive("m2 from B", ts2)
# A t=1: local work
# A t=2: send m1 to B
# B t=1: unrelated work
# B t=3: receive m1 from A
# B t=4: send m2 to C
# C t=1: independent event
# C t=5: receive m2 from B
```

The guarantee: **if `a → b` then `L(a) < L(b)`**. Check: A's send (2) < B's receive (3) < B's send (4) < C's receive (5). The converse is **not** true: `L(a) < L(b)` does not prove `a → b` (compare "B unrelated work" t=1 and "A send" t=2: they are concurrent, yet the numbers differ). Lamport clocks give a consistent total order (break ties by process id), but cannot tell you whether two events are **concurrent**.

## 6. Vector clocks: detecting concurrency

A **vector clock** keeps one counter **per process**. Compare two vectors entry by entry: if one is `<=` the other everywhere, that event happened before; if neither dominates, the events are **concurrent** (a conflict).

```python
def vc_merge(a: dict, b: dict) -> dict:
    return {k: max(a.get(k, 0), b.get(k, 0)) for k in set(a) | set(b)}

def vc_compare(a: dict, b: dict) -> str:
    keys = set(a) | set(b)
    a_le = all(a.get(k, 0) <= b.get(k, 0) for k in keys)
    b_le = all(b.get(k, 0) <= a.get(k, 0) for k in keys)
    if a_le and b_le:
        return "equal"
    if a_le:
        return "before"            # a happened before b
    if b_le:
        return "after"
    return "concurrent"            # neither knew about the other

class Replica:
    def __init__(self, name):
        self.name, self.vc, self.value = name, {}, None
    def write(self, value):
        self.vc[self.name] = self.vc.get(self.name, 0) + 1
        self.value = value
    def sync_from(self, other):                      # receive other's state
        relation = vc_compare(other.vc, self.vc)
        if relation == "after":                      # other is strictly newer: adopt it
            self.value, self.vc = other.value, dict(other.vc)
            return "took newer value"
        if relation == "concurrent":
            self.vc = vc_merge(self.vc, other.vc)
            return f"CONFLICT between {self.value!r} and {other.value!r}"
        return "already up to date"

r1, r2 = Replica("r1"), Replica("r2")
r1.write("cart=[book]")
print(r2.sync_from(r1), r2.vc)                       # r2 learns of r1's write: no conflict
# took newer value {'r1': 1}
r1.write("cart=[book, pen]")                          # r1 and r2 now update independently...
r2.write("cart=[book, mug]")
print(r1.vc, r2.vc, vc_compare(r1.vc, r2.vc))
# {'r1': 2} {'r1': 1, 'r2': 1} concurrent
print(r2.sync_from(r1))
# CONFLICT between 'cart=[book, mug]' and 'cart=[book, pen]'
```

Dynamo-style databases (Riak, early Amazon Dynamo) use vector clocks and then let the application or a merge rule resolve conflicts (for example, take the **union** of the two shopping carts). Cheaper schemes pick a winner by timestamp (**last-write-wins**) and accept lost updates; **CRDTs** (conflict-free replicated data types) are structures designed so that any merge order gives the same result. Google's Spanner instead makes clocks trustworthy with GPS and atomic clocks (**TrueTime**) and waits out the uncertainty.

## 7. Common mistakes

- Treating a timeout as proof the other side did **not** do the work.
- Ordering events from different machines by wall-clock time.
- Assuming messages arrive once and in order.
- Using local time (and daylight saving) instead of UTC; or measuring durations with a clock that can jump (use a **monotonic** clock: `time.monotonic()`).
- Thinking Lamport timestamps tell you two events are related.
- Testing only on a fast, reliable local network.

## 8. Two real-world examples

**Example 1: The lost update.** A shopping-cart service used last-write-wins by timestamp across two data centers. A phone and a laptop each added an item within a second of each other; the machine with the later (slightly fast) clock won and the other item vanished. Switching to a merge (union of items) removed the complaints.

**Example 2: The leap second.** When a leap second was inserted, some servers' clocks stepped back by one second; code that measured elapsed time as `end - start` with wall-clock time computed negative durations, and timers fired in a tight loop. Using monotonic clocks for durations and smearing the leap second across hours prevents the problem.

## 9. Practice

1. Run the network with `loss=0` and `duplicate=0`: can messages still arrive out of order? Why?
2. Add a `retransmit` experiment: keep sending `msg1` every tick until the receiver has seen it. How many copies does the receiver get on average, and what must the receiver do about duplicates?
3. Give Lamport timestamps for: A does event, A sends to B, B receives, B does event. 
4. Using `vc_compare`, classify `{'a':2,'b':1}` versus `{'a':2,'b':3}` and `{'a':1,'b':2}` versus `{'a':2,'b':1}`.
5. Write a `merge_carts` that resolves the conflict in section 6 by taking the union of items.
6. Why is `time.monotonic()` the right clock for a timeout, and `time.time()` the wrong one?

<details>
<summary>Solutions</summary>

1. ```python
   net2 = Network(seed=1, loss=0, max_delay=3, duplicate=0)
   for n in range(1, 6):
       net2.send("A", "B", n)
   got = []
   for _ in range(5):
       got += [m for _, m in net2.tick()]
   print(sorted(got) == [1, 2, 3, 4, 5], got == sorted(got))
   # True False   (all arrive, but not necessarily in order)
   ```
   Yes: each message gets its own random delay, so a later one can overtake an earlier one.
2. The receiver gets about as many copies as the network lets through; it must **deduplicate** (remember ids it has processed) so processing is idempotent.
3. A event t=1; A send t=2; B receive t=3 (max(0,2)+1); B event t=4.
4. `vc_compare({'a':2,'b':1}, {'a':2,'b':3})` is `before`; `vc_compare({'a':1,'b':2}, {'a':2,'b':1})` is `concurrent`.
5. ```python
   import re
   def merge_carts(x: str, y: str) -> str:
       items = lambda s: set(re.findall(r"\[(.*)\]", s)[0].replace(" ", "").split(","))
       return "cart=[" + ", ".join(sorted(items(x) | items(y))) + "]"
   print(merge_carts("cart=[book, mug]", "cart=[book, pen]"))
   # cart=[book, mug, pen]
   ```
6. `time.monotonic()` only moves forward at a steady rate and is unaffected by NTP adjustments or manual changes; `time.time()` can jump backwards or forwards, making elapsed time negative or huge.

</details>

## 10. Check yourself

1. Name the three ways a request with no reply could have failed.
2. What is the difference between crash-stop and Byzantine failures?
3. Why can't you order events across machines by wall-clock time?
4. State the Lamport clock rules and the guarantee they give. What is the guarantee's converse, and does it hold?
5. How does a vector clock detect concurrent updates?
6. Name two ways to resolve conflicting updates.
7. What clock should you use to measure a timeout?

<details>
<summary>Answers</summary>

1. The request was lost; the server crashed (or is slow); the server did the work but the reply was lost.
2. A crashed node simply stops; a Byzantine node may keep running but send wrong or malicious messages.
3. Clocks drift and are adjusted by NTP, so a later event can carry an earlier timestamp.
4. Increment on every event; send the counter with messages; on receive set `max(own, received) + 1`. Guarantee: `a → b` implies `L(a) < L(b)`. The converse (smaller timestamp means happened-before) does not hold.
5. Each process keeps a counter per process; if neither vector dominates the other, neither event knew about the other, so they are concurrent.
6. Last-write-wins (simple, may lose data), application-level merge (such as set union), or CRDTs.
7. A monotonic clock (`time.monotonic()`).

</details>

[Back to Distributed Systems](../README.md)
