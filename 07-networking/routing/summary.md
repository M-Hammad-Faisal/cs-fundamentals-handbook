# Routing: One-Page Summary

## Key facts

| Family | Example | Router knows | Weakness |
|--------|---------|--------------|----------|
| Distance vector | RIP | distances via neighbors | count to infinity, slow convergence |
| Link state | OSPF, IS-IS | the whole topology; runs Dijkstra | more CPU and memory (use areas) |
| Path vector | BGP | full AS paths per prefix | trust: hijacks and leaks without filters/RPKI |

Related: [packets and subnets](../tcp-ip-osi/01-packets-addressing-and-subnets.md), [graph algorithms](../../03-algorithms/graph-algorithms/01-all-pairs-and-heuristic-shortest-paths.md).

## Pitfalls

- The longest matching prefix wins, not the lowest metric.
- Routing loops and asymmetric paths: TTL stops loops from living forever.
- Assuming BGP is secure by default: hijacks and leaks need filtering and RPKI.
- Count to infinity in distance-vector protocols (split horizon and poison reverse reduce it).
- Mixing up learning routes (the protocol) with forwarding packets (the data plane).

## Self-check

- **What is the difference between an IGP and BGP?** An IGP (OSPF, IS-IS, RIP) runs inside one organization to find cheapest paths; BGP runs between autonomous systems and selects routes by business policy.
- **How does distance-vector routing work, and why does it count to infinity?** Routers send their distance tables to neighbors and adopt `neighbor's distance + link cost` when it is better (distributed Bellman-Ford). After a failure, neighbors keep advertising routes that depended on the broken link, raising costs by one each exchange (count to infinity).
- **How does link-state routing work, and what does each router compute?** Each router floods an LSA of its own links; all routers end with the same topology database and each runs Dijkstra to compute its own shortest-path tree.
- **What is an AS path used for?** It lists the ASes a route passed through: loop prevention (reject paths containing your own ASN), path-length comparison and policy filtering.
- **State the Gao-Rexford preference and export rules.** Prefer customer routes over peer routes over provider routes; export customer routes to everyone, but export peer and provider routes only to customers (no free transit).
- **How can a more specific prefix hijack traffic, and what stops it?** Routers forward by longest prefix match, so a more specific announcement wins even if bogus; defenses are prefix filters, max-prefix limits, RPKI route origin validation and monitoring.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Routing Protocols](01-routing-protocols.md)
