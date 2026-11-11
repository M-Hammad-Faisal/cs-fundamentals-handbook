# Distributed Transactions and Reliability Patterns

Idempotency, retries, circuit breakers, sagas and the outbox.

## Detailed lessons

- [Idempotency, retries, circuit breakers, sagas and the outbox](01-idempotency-retries-and-sagas.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Question | Answer |
|----------|--------|
| What does idempotent mean, and which of `SET x=5` and `x += 5` is idempotent? | Doing it twice equals doing it once; `SET x=5` is idempotent, `x += 5` is not. |
| How does an idempotency key work, and who generates it? | The client creates one unique key per logical operation and sends it on every retry; the server stores the result under the key and returns it instead of repeating the work. |
| Why add jitter to exponential backoff? | Without jitter all clients retry at the same instants, producing synchronized bursts; randomising spreads the load. |
| Describe the three circuit breaker states. | Closed (normal, counting failures), open (reject immediately during a cool-down), half-open (allow one trial; success closes, failure re-opens). |
| What is a saga, and what is a compensating action? | A sequence of local transactions across services; if one fails, compensating actions undo the earlier steps (for example refund a charge). |

Back to the [part overview](../README.md).
