# Distributed Transactions and Reliability Patterns: One-Page Summary

## Key facts

- **Duplicates are normal:** retries after timeouts mean a request can arrive twice; make operations **idempotent** with an idempotency key stored with the result.
- **Retrying well:** exponential backoff with jitter, a retry limit and a deadline; retry only safe or idempotent operations and only transient errors.
- **Circuit breaker:** after repeated failures stop calling the dependency (open), then probe (half-open) and close again on success; fail fast and degrade gracefully.
- **Saga:** a business transaction as a series of local transactions, each with a **compensating action** that undoes it if a later step fails; steps and compensations must be idempotent.
- **Transactional outbox:** write the business change and the event to publish in one local transaction, then a relay publishes the event; avoids the "saved but never announced" gap.
- **Two-phase commit:** a coordinator asks all participants to prepare, then commit; it blocks if the coordinator fails and holds locks, so it is usually avoided across services.
- **Delivery:** at-least-once delivery plus idempotent consumers gives effectively-once processing.

## Pitfalls

- Retrying without backoff, which turns a small outage into a retry storm.
- Retrying a non-idempotent call (a charge) with no idempotency key.
- Compensations that can fail or that are not idempotent.
- Updating the database and then publishing the event in a separate step with no outbox.
- Assuming exactly-once delivery exists.

## Self-check

- **What does idempotent mean, and which of `SET x=5` and `x += 5` is idempotent?** Doing it twice equals doing it once; `SET x=5` is idempotent, `x += 5` is not.
- **How does an idempotency key work, and who generates it?** The client creates one unique key per logical operation and sends it on every retry; the server stores the result under the key and returns it instead of repeating the work.
- **Why add jitter to exponential backoff?** Without jitter all clients retry at the same instants, producing synchronized bursts; randomising spreads the load.
- **Describe the three circuit breaker states.** Closed (normal, counting failures), open (reject immediately during a cool-down), half-open (allow one trial; success closes, failure re-opens).
- **What is a saga, and what is a compensating action?** A sequence of local transactions across services; if one fails, compensating actions undo the earlier steps (for example refund a charge).
- **What problem does the outbox pattern solve?** It makes "update the database and publish an event" atomic by writing the event into the same local transaction, with a relay delivering it at-least-once.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Idempotency, Retries, Circuit Breakers, Sagas and the Outbox](01-idempotency-retries-and-sagas.md)
