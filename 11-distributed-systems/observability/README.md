# Observability

Logs, metrics, traces and service level objectives.

## Detailed lessons

- [Observability: logs, metrics, traces and SLOs](01-observability-logs-metrics-traces-slos.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Question | Answer |
|----------|--------|
| Which question does each pillar (logs, metrics, traces) answer best? | Logs: what happened in detail; metrics: how the system behaves in aggregate; traces: where a request spent time across services. |
| Why are averages misleading for latency? | They hide the slow tail; most users can be fast while a few suffer, and at scale each request touches many components so tail latency affects many users. |
| What is context propagation, and what breaks without it? | Passing the trace id and parent span id along with each call so every service attaches its spans to the same trace; without it, a trace breaks into unconnected fragments. |
| Define SLI, SLO, SLA and error budget. | SLI: a measured quality indicator; SLO: the target for it over a window; SLA: a contract with penalties; error budget: the allowed failure, `1 - SLO`. |
| What does a burn rate of 1 mean? Of 14.4? | Consuming the budget at exactly the rate that would use it up at the end of the window; 14.4 drains a 30-day budget in about two days. |

Back to the [part overview](../README.md).
