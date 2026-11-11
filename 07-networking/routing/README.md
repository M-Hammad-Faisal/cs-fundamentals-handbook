# Routing

How routers learn where networks are, and how the internet's thousands of independent networks stay connected.

## Detailed lessons

- [Routing protocols: distance vector, link state and BGP](01-routing-protocols.md): RIP-style distance vector and count-to-infinity, OSPF-style link state with LSA flooding, BGP path-vector with customer/peer/provider policy, prefix hijacks and RPKI, all as verified simulations

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Family | Example | Router knows | Weakness |
|--------|---------|--------------|----------|
| Distance vector | RIP | distances via neighbors | count to infinity, slow convergence |
| Link state | OSPF, IS-IS | the whole topology; runs Dijkstra | more CPU and memory (use areas) |
| Path vector | BGP | full AS paths per prefix | trust: hijacks and leaks without filters/RPKI |

Related: [packets and subnets](../tcp-ip-osi/01-packets-addressing-and-subnets.md), [graph algorithms](../../03-algorithms/graph-algorithms/01-all-pairs-and-heuristic-shortest-paths.md).

Back to [networking](../README.md).
