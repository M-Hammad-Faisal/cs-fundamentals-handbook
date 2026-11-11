# Distributed Systems

How systems made of many machines stay correct and available when networks fail and clocks disagree. Each lesson builds the idea in runnable Python (simulated networks, a Raft cluster, an LSM tree) so you can watch the failures happen and see the fix.

**Prerequisites:** [networking](../07-networking/README.md), [operating systems](../06-operating-systems/README.md), [databases](../05-databases/README.md), and the [system design basics](../09-interview-playbook/system-design-basics/README.md) chapter.

## Learning path

| # | Lesson | You will learn |
|---|--------|----------------|
| 1 | [Failures, time and clocks](foundations/01-failures-time-and-clocks.md) | partial failure, failure models, a simulated lossy network, why wall clocks fail, Lamport and vector clocks |
| 2 | [Replication, quorums and sharding](replication-sharding/01-replication-and-sharding.md) | leader and followers, replication lag, `R + W > N` verified by brute force, range versus hash sharding, consistent hashing measured |
| 3 | [Consensus and Raft](consensus/01-consensus-and-raft.md) | leader election, log replication, a working Raft simulator, crashes, partitions and a randomized safety test |
| 4 | [Idempotency, retries, circuit breakers, sagas and the outbox](transactions/01-idempotency-retries-and-sagas.md) | idempotency keys, backoff with jitter, circuit breaker, saga compensation, transactional outbox, why 2PC blocks |
| 5 | [Logs, queues and LSM trees](messaging-storage/01-logs-queues-and-lsm-trees.md) | append-only logs, delivery guarantees, partitions and consumer groups, an LSM tree, Bloom filters |
| 6 | [Observability: logs, metrics, traces and SLOs](observability/01-observability-logs-metrics-traces-slos.md) | structured logs, percentiles, distributed tracing, SLIs, SLOs, error budgets and burn rates |

## How the lessons connect

Failures and clocks (1) explain *why* you need copies and agreement. Replication and sharding (2) scale data; consensus (3) keeps the copies in agreement. Retries, sagas and the outbox (4) keep business operations correct across services. Logs and LSM trees (5) show how the data is actually stored and moved. Observability (6) lets you see all of it in production.

## Related lessons

- [System design basics](../09-interview-playbook/system-design-basics/README.md) and [more designs and reliability](../09-interview-playbook/system-design-basics/02-five-more-designs.md): applying these ideas in interviews
- [Load balancing and resilience lab](../07-networking/load-balancing-cdn/01-load-balancing-and-resilience-lab.md)
- [Transactions and ACID](../05-databases/transactions-acid/README.md) and [NoSQL](../05-databases/nosql/README.md)
- [Security](../10-security/README.md)

Back to the [handbook home](../README.md).
