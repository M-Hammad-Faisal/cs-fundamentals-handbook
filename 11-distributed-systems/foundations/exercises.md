# Foundations of Distributed Systems: Exercises

These problems go with the [Foundations of Distributed Systems lesson](README.md). Try each one before opening its solution.

<details>
<summary>Setup code the solutions use (copied from the lessons)</summary>

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
```

</details>

## Problems

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

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Failures, Time and Clocks in Distributed Systems](01-failures-time-and-clocks.md)
