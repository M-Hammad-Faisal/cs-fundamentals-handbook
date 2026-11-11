# Observability: One-Page Summary

## Key facts

- **Three pillars:** *logs* (events, structured as JSON with a **correlation id**), *metrics* (numbers over time: counters only go up, gauges go up and down, histograms record distributions), *traces* (one request's path across services as spans with a shared trace id).
- **Percentiles, not averages:** the mean hides the tail; alert on p95 or p99 of a user-facing latency; you cannot average percentiles across servers, merge the histograms instead.
- **SLI, SLO, error budget:** an SLI is a measurement (successful requests / all requests), an SLO the target (99.9% over 30 days), the error budget what is left (0.1%, about 43 minutes a month); burn-rate alerts tell you when you are spending it too fast.
- **Fan-out effect:** a request making 20 backend calls hits at least one p99-slow call about `1 - 0.99²⁰ ≈ 18%` of the time.
- **Debugging flow:** metric shows something is wrong, trace shows where, logs show why.
- **Safe logging:** redact secrets and personal data; log at the right level.

## Pitfalls

- Alerting on averages or on every error instead of on SLO burn.
- Logs without a correlation id, so one request cannot be followed.
- High-cardinality metric labels (user id, URL with ids) that explode storage.
- Logging secrets, tokens or personal data.
- Dashboards nobody looks at and alerts nobody acts on.

## Self-check

- **Which question does each pillar (logs, metrics, traces) answer best?** Logs: what happened in detail; metrics: how the system behaves in aggregate; traces: where a request spent time across services.
- **Why are averages misleading for latency?** They hide the slow tail; most users can be fast while a few suffer, and at scale each request touches many components so tail latency affects many users.
- **What is context propagation, and what breaks without it?** Passing the trace id and parent span id along with each call so every service attaches its spans to the same trace; without it, a trace breaks into unconnected fragments.
- **Define SLI, SLO, SLA and error budget.** SLI: a measured quality indicator; SLO: the target for it over a window; SLA: a contract with penalties; error budget: the allowed failure, `1 - SLO`.
- **What does a burn rate of 1 mean? Of 14.4?** Consuming the budget at exactly the rate that would use it up at the end of the window; 14.4 drains a 30-day budget in about two days.
- **Why alert on symptoms rather than causes?** Symptoms are what users feel and need action; many causes (high CPU) are harmless on their own and generate noisy pages.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Observability](01-observability-logs-metrics-traces-slos.md)
