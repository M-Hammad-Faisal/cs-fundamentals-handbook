# Observability: Exercises

These problems go with the [Observability lesson](README.md). Try each one before opening its solution.

<details>
<summary>Setup code the solutions use (copied from the lessons)</summary>

```python
import bisect
from collections import defaultdict
import contextvars

class Metrics:
    def __init__(self):
        self.counters = defaultdict(int)
        self.gauges = {}
        self.histograms = defaultdict(list)
    def inc(self, name, by=1, **labels):
        self.counters[(name, tuple(sorted(labels.items())))] += by
    def set_gauge(self, name, value):
        self.gauges[name] = value
    def observe(self, name, value):
        self.histograms[name].append(value)

def percentile(values, p):
    """Nearest-rank percentile: the smallest value that at least p percent of observations do not exceed."""
    ordered = sorted(values)
    rank = max(1, -(-len(ordered) * p // 100))              # ceiling division
    return ordered[int(rank) - 1]

m = Metrics()
for ms in [20] * 90 + [25] * 6 + [900, 1000, 1100, 1200]:    # 100 requests: mostly fast, a slow tail of four
    m.observe("latency_ms", ms)
    m.inc("requests_total", status="200")

m.inc("requests_total", by=3, status="500")
m.set_gauge("queue_length", 12)

lat = m.histograms["latency_ms"]
print(f"mean = {sum(lat) / len(lat):.0f} ms | p50 = {percentile(lat, 50)} | p95 = {percentile(lat, 95)} | p99 = {percentile(lat, 99)} | max = {max(lat)}")
# mean = 62 ms | p50 = 20 | p95 = 25 | p99 = 1100 | max = 1200
print("requests:", dict(m.counters))
# requests: {('requests_total', (('status', '200'),)): 100, ('requests_total', (('status', '500'),)): 3}


current_span = contextvars.ContextVar("current_span", default=None)
clock = [0.0]                                              # a fake clock so the demo is deterministic
spans = []

class Span:
    def __init__(self, name, trace_id=None):
        parent = current_span.get()
        self.name = name
        self.trace_id = trace_id or (parent.trace_id if parent else "trace-1")
        self.parent = parent
        self.depth = parent.depth + 1 if parent else 0
    def __enter__(self):
        self.start, self.token = clock[0], current_span.set(self)
        return self
    def __exit__(self, *exc):
        self.end = clock[0]
        current_span.reset(self.token)
        spans.append(self)

def work(ms):
    clock[0] += ms

def database():
    with Span("db.query"):
        work(30)

def inventory_service(headers):
    with Span("inventory.check", trace_id=headers["trace_id"]):   # continues the caller's trace via the header
        work(5)
        database()

def order_service():
    with Span("order.create"):
        work(10)
        inventory_service({"trace_id": current_span.get().trace_id})   # propagate the context on the "network" call
        work(5)

with Span("gateway.request"):
    work(2)
    order_service()
    work(3)

for s in sorted(spans, key=lambda s: s.start):
    print(f"{'  ' * s.depth}{s.name:<{22 - 2 * s.depth}} {s.end - s.start:>5.0f} ms   (starts at {s.start:.0f})")

# gateway.request           55 ms   (starts at 0)
#   order.create            50 ms   (starts at 2)
#     inventory.check       35 ms   (starts at 12)
#       db.query            30 ms   (starts at 17)
print("all spans share one trace:", {s.trace_id for s in spans})
# all spans share one trace: {'trace-1'}
```

</details>

## Problems

1. Add a `p90` line to the latency output. Which of mean, p50, p90, p95 and p99 would you alert on, and why?
2. Compute the chance that a request making 20 independent backend calls hits at least one p99 slow call.
3. Extend `Span` to record an `error` flag when the `with` block raises, and show it in the printout.
4. A service handles 5 million requests a month with a 99.95 percent SLO. How many failed requests may it have? How many minutes of total outage?
5. Make `handle_request` log the amount only when it is under 100 and redact it otherwise. Why?
6. Explain why you cannot average the p99 latencies of three servers to get the overall p99.

<details>
<summary>Solutions</summary>

1. ```python
   print(percentile(lat, 90))
   # 20
   ```
   Alert on a high percentile of a user-facing SLI (for example p99 or the SLO burn rate); the mean hides the tail and the median hides it too.
2. ```python
   print(round(1 - 0.99 ** 20, 3))
   # 0.182
   ```
3. ```python
   class Span2(Span):
       def __exit__(self, exc_type, exc, tb):
           self.error = exc_type is not None
           super().__exit__(exc_type, exc, tb)
   try:
       with Span2("flaky.call") as sp:
           raise ValueError("boom")
   except ValueError:
       print(sp.error)
   # True
   ```
4. ```python
   print(round(5_000_000 * (1 - 0.9995)), round(30 * 24 * 60 * (1 - 0.9995), 1))
   # 2500 21.6
   ```
   2,500 failed requests, or about 21.6 minutes of full outage in a 30-day month.
5. Logging a sensitive or high-cardinality value everywhere is a privacy and cost risk; redacting at the logging call keeps useful fields while preventing leaks. (Apply the rule at the source rather than trusting a downstream filter.)
6. A percentile depends on the whole distribution and on how many requests each server handled; the 99th percentile of the combined data can be higher or lower than any weighted mix of the individual p99s. Merge the histograms (bucket counts) and compute the percentile from the merged histogram.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Observability](01-observability-logs-metrics-traces-slos.md)
