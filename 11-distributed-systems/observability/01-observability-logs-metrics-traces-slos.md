# Observability: Logs, Metrics, Traces and SLOs

**Prerequisites:** [Exceptions, logging and testing](../../08-modern-python/exceptions-logging-testing/README.md), [failures and clocks](../foundations/01-failures-time-and-clocks.md), [system design basics](../../09-interview-playbook/system-design-basics/README.md) (availability and "the nines"). **You will learn:** how to **see inside** a running distributed system using the three pillars (**structured logs**, **metrics**, **traces**), why **averages lie** and percentiles do not, how a request id and **context propagation** let you follow one request across services, and how **SLIs, SLOs and error budgets** turn "is it reliable enough?" into numbers, all built in plain Python.

## 1. In plain words

In a single program you can add a `print` or open a debugger. In a system of dozens of services on hundreds of machines you cannot attach to anything; you can only **look at what the system emits**. **Observability** is the ability to answer new questions about your system's behaviour from its outputs, without shipping new code. Monitoring tells you *that* something is wrong (an alert); observability helps you work out *why*.

| Pillar | Question it answers | Shape | Cost |
|--------|--------------------|-------|------|
| **Logs** | What happened, in detail? | discrete timestamped events | high volume, expensive to store and search |
| **Metrics** | How is it behaving overall? | numbers aggregated over time | cheap, fast to query, little detail |
| **Traces** | Where did this request spend its time, across services? | a tree of timed spans | sampled; shows causality |

## 2. Structured logs with correlation ids

Plain-text logs (`"user 42 failed to pay"`) are hard to search. **Structured logs** emit machine-readable fields (usually JSON), so you can query `status=500 AND service=checkout`. Add a **request id** to every line so you can pull out everything one request did. Python's `contextvars` carries the id through code (and across `async` tasks) without passing it by hand.

```python
import contextvars, io, itertools, json, logging

request_id = contextvars.ContextVar("request_id", default="-")
request_counter = itertools.count(1)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        entry = {"level": record.levelname, "msg": record.getMessage(), "request_id": request_id.get(), **getattr(record, "fields", {})}
        return json.dumps(entry, sort_keys=True)

stream = io.StringIO()
handler = logging.StreamHandler(stream)
handler.setFormatter(JsonFormatter())
log = logging.getLogger("checkout")
log.handlers, log.propagate = [handler], False
log.setLevel(logging.INFO)

def handle_request(user, amount):
    request_id.set(f"req-{next(request_counter)}")                    # a fresh id per request (real systems use a random id or accept one from the caller)
    log.info("payment started", extra={"fields": {"user": user, "amount": amount}})
    if amount > 100:
        log.error("payment rejected", extra={"fields": {"user": user, "reason": "limit"}})
    else:
        log.info("payment ok", extra={"fields": {"user": user}})

handle_request("ada", 40)
handle_request("bob", 500)
lines = [json.loads(l) for l in stream.getvalue().splitlines()]
print(len(lines), "log lines;", len({l["request_id"] for l in lines}), "different request ids")
print([l["msg"] for l in lines if l["level"] == "ERROR"], {l["request_id"] == lines[2]["request_id"] for l in lines[2:]})
# 4 log lines; 2 different request ids
# ['payment rejected'] {True}
```

Rules: log **events with fields** rather than formatted sentences; include ids, never secrets or personal data (see [redaction](../../10-security/secrets-and-supply-chain/01-secrets-dependencies-and-hardening.md)); use levels consistently (`ERROR` means someone should look); and keep an eye on volume, because logging everything at `DEBUG` in production is expensive.

## 3. Metrics: counters, gauges and histograms

A **metric** is a number tracked over time and aggregated cheaply. Three basic types:

- **Counter:** only goes up (requests served, errors). You look at its **rate** (per second).
- **Gauge:** goes up and down (queue length, memory in use, active connections).
- **Histogram:** counts how many observations fell into value ranges (latency buckets), so you can estimate **percentiles**.

```python
import bisect
from collections import defaultdict

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
```

**Averages lie.** The mean (62 ms) describes nobody: 96 percent of users saw 20 to 25 ms, and four saw over a second. The **p99** exposes the tail. At scale the tail matters most: a page that makes 50 backend calls will hit at least one p99-slow call about 40 percent of the time (`1 - 0.99^50`). Therefore: track **percentiles** (p50, p95, p99), never only averages; and be careful aggregating them (you cannot average percentiles across servers: merge the underlying histograms instead).

**What to measure:**

- **RED** for services: **R**ate (requests/s), **E**rrors (failed fraction), **D**uration (latency percentiles).
- **USE** for resources: **U**tilization, **S**aturation (queueing), **E**rrors.
- Google's four **golden signals**: latency, traffic, errors, saturation.

**Beware high-cardinality labels:** `user_id` as a metric label creates one time series per user and can overwhelm the metrics system; put such detail in logs or traces instead.

## 4. Distributed tracing

When one user click fans out through a gateway, an order service, an inventory service and a database, which hop was slow? A **trace** records the whole request as a tree of **spans** (one timed operation each). All spans share one **trace id**; each carries its **parent span id**. The id travels between services in a **header** (the W3C `traceparent` standard) so each service can attach its spans to the same trace: **context propagation**.

```python
import contextvars

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

Reading the tree: the request took 55 ms; 35 ms of it is the inventory check and 30 ms of that is the database query, so the database is the place to look. Real systems use **OpenTelemetry** (the standard SDK and wire format) with backends such as Jaeger, Tempo or Zipkin. Because tracing every request is costly, systems **sample** (for example 1 percent, plus all errors and slow requests).

## 5. SLIs, SLOs and error budgets

Alerts on raw metrics ("CPU > 80%") page people about things users never notice. Reliability engineering instead starts from the user:

- **SLI** (service level indicator): a measurement of user-visible quality, such as "the fraction of requests that succeed in under 300 ms".
- **SLO** (service level objective): the target for the SLI over a window, such as "99.9 percent of requests over 30 days".
- **SLA** (agreement): a contract with consequences (refunds) for missing an SLO, usually looser than the internal SLO.
- **Error budget:** `1 - SLO`, the amount of failure you are **allowed**. While budget remains you can ship features and take risks; when it is spent, you slow down and invest in reliability.

```python
def error_budget(slo: float, window_days: int, requests_per_day: int):
    budget_fraction = 1 - slo
    minutes = window_days * 24 * 60 * budget_fraction
    bad_requests = window_days * requests_per_day * budget_fraction
    return round(minutes, 1), round(bad_requests)

for slo in (0.99, 0.999, 0.9999):
    minutes, bad = error_budget(slo, 30, 1_000_000)
    print(f"SLO {slo:.2%}: {minutes:>6} minutes of full outage per 30 days, or {bad:>6} failed requests out of 30,000,000")
# SLO 99.00%:  432.0 minutes of full outage per 30 days, or 300000 failed requests out of 30,000,000
# SLO 99.90%:   43.2 minutes of full outage per 30 days, or  30000 failed requests out of 30,000,000
# SLO 99.99%:    4.3 minutes of full outage per 30 days, or   3000 failed requests out of 30,000,000
```

Each extra nine costs roughly ten times more engineering effort for ten times less allowed failure: choose the SLO the **users actually need**, not "as high as possible".

**Burn rate** alerting: the **burn rate** is how fast you consume the budget compared with the rate that would exactly use it all by the end of the window. A burn rate of 1 is on pace to finish the budget exactly at the window's end; 14.4 would drain a 30-day budget in about 2 days.

```python
def burn_rate(error_ratio: float, slo: float) -> float:
    return error_ratio / (1 - slo)

def should_page(short_window_errors: float, long_window_errors: float, slo=0.999, threshold=14.4) -> bool:
    """Page only if BOTH a short window (still happening) and a long window (significant) burn fast."""
    return burn_rate(short_window_errors, slo) >= threshold and burn_rate(long_window_errors, slo) >= threshold

print(round(burn_rate(0.0144, 0.999), 1))
# 14.4
print(should_page(0.02, 0.016), should_page(0.02, 0.002), should_page(0.0005, 0.02))
# True False False
```

Requiring both windows avoids paging on a blip that already ended or a trickle too small to matter. The same budget thinking turns "reliability versus features" arguments into a number both sides can read.

## 6. Debugging with the pillars together

1. **Metric alert:** p99 latency of `checkout` jumped, or the SLO burn rate is high (*something is wrong*).
2. **Metric drill-down:** which route, region or version? (labels)
3. **Trace:** open a slow example; the span tree shows the slow hop (*where*).
4. **Logs:** filter by that trace or request id to see the error and context (*why*).
5. **Fix and verify** on the dashboards; write down what you learned (a **blameless postmortem**).

## 7. Common mistakes

- Alerting on causes (CPU, memory) rather than symptoms (users failing or slow); causes belong on dashboards.
- Reporting averages; not looking at p95 or p99.
- High-cardinality metric labels (user ids, full URLs) that blow up storage.
- Unstructured logs with no request id, so one request cannot be followed.
- No context propagation, so traces break into disconnected fragments at service boundaries.
- Logging secrets or personal data.
- Alert fatigue: pages that need no action get ignored, including the real one. Every page should be urgent and actionable.
- Dashboards nobody understands; an SLO nobody agreed to.

## 8. Two real-world examples

**Example 1: The 99th percentile.** A team celebrated a 40 ms average latency while customers complained of timeouts. Percentile dashboards showed p99 at 4 seconds, caused by a rarely used code path that fell back to a slow database query. Traces located it in minutes; an index fixed it.

**Example 2: The budget conversation.** A product team wanted to ship a risky migration; the platform team pointed out that the 30-day error budget was 85 percent spent after two incidents. They agreed to delay the migration, fix the flaky dependency first and ship the next week, a decision made from a number instead of an argument.

## 9. Practice

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

## 10. Check yourself

1. Which question does each pillar (logs, metrics, traces) answer best?
2. Why are averages misleading for latency?
3. What is context propagation, and what breaks without it?
4. Define SLI, SLO, SLA and error budget.
5. What does a burn rate of 1 mean? Of 14.4?
6. Why alert on symptoms rather than causes?
7. Why avoid high-cardinality metric labels?

<details>
<summary>Answers</summary>

1. Logs: what happened in detail; metrics: how the system behaves in aggregate; traces: where a request spent time across services.
2. They hide the slow tail; most users can be fast while a few suffer, and at scale each request touches many components so tail latency affects many users.
3. Passing the trace id and parent span id along with each call so every service attaches its spans to the same trace; without it, a trace breaks into unconnected fragments.
4. SLI: a measured quality indicator; SLO: the target for it over a window; SLA: a contract with penalties; error budget: the allowed failure, `1 - SLO`.
5. Consuming the budget at exactly the rate that would use it up at the end of the window; 14.4 drains a 30-day budget in about two days.
6. Symptoms are what users feel and need action; many causes (high CPU) are harmless on their own and generate noisy pages.
7. Each distinct label value creates a separate time series; unbounded values (user ids) explode storage and slow queries.

</details>

[Back to Distributed Systems](../README.md)
