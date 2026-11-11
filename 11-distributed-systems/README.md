# Part 11: Distributed Systems

How systems made of many machines stay correct and available when networks fail and clocks disagree. Each lesson builds the idea in runnable Python (simulated networks, a Raft cluster, an LSM tree) so you can watch the failures happen and see the fix.

**Prerequisites:** [networking](../07-networking/README.md), [operating systems](../06-operating-systems/README.md), [databases](../05-databases/README.md), and the [system design basics](../09-interview-playbook/system-design-basics/README.md) chapter.

## Topics in this part

Read the topics in this order. Each has an overview, detailed lessons, exercises with solutions and a one-page summary (the full map is in the [index](../INDEX.md)).

<!-- topics:start -->
| Topic | Lessons | Exercises | Summary |
|-------|---------|-----------|---------|
| Foundations of Distributed Systems | [overview](foundations/README.md)<br>[Failures, Time and Clocks in Distributed Systems](foundations/01-failures-time-and-clocks.md) | [ex](foundations/exercises.md) | [sum](foundations/summary.md) |
| Replication and Sharding | [overview](replication-sharding/README.md)<br>[Replication, Quorums and Sharding](replication-sharding/01-replication-and-sharding.md) | [ex](replication-sharding/exercises.md) | [sum](replication-sharding/summary.md) |
| Consensus | [overview](consensus/README.md)<br>[Consensus and Raft](consensus/01-consensus-and-raft.md) | [ex](consensus/exercises.md) | [sum](consensus/summary.md) |
| Distributed Transactions and Reliability Patterns | [overview](transactions/README.md)<br>[Idempotency, Retries, Circuit Breakers, Sagas and the Outbox](transactions/01-idempotency-retries-and-sagas.md) | [ex](transactions/exercises.md) | [sum](transactions/summary.md) |
| Messaging and Storage | [overview](messaging-storage/README.md)<br>[Logs, Queues and LSM Trees](messaging-storage/01-logs-queues-and-lsm-trees.md) | [ex](messaging-storage/exercises.md) | [sum](messaging-storage/summary.md) |
| Observability | [overview](observability/README.md)<br>[Observability](observability/01-observability-logs-metrics-traces-slos.md) | [ex](observability/exercises.md) | [sum](observability/summary.md) |
<!-- topics:end -->

## How the lessons connect

Failures and clocks (1) explain *why* you need copies and agreement. Replication and sharding (2) scale data; consensus (3) keeps the copies in agreement. Retries, sagas and the outbox (4) keep business operations correct across services. Logs and LSM trees (5) show how the data is actually stored and moved. Observability (6) lets you see all of it in production.

## Related lessons

- [System design basics](../09-interview-playbook/system-design-basics/README.md) and [more designs and reliability](../09-interview-playbook/system-design-basics/02-five-more-designs.md): applying these ideas in interviews
- [Load balancing and resilience lab](../07-networking/load-balancing-cdn/01-load-balancing-and-resilience-lab.md)
- [Transactions and ACID](../05-databases/transactions-acid/README.md) and [NoSQL](../05-databases/nosql/README.md)
- [Security](../10-security/README.md)

Back to the [handbook home](../README.md) · [index](../INDEX.md).
