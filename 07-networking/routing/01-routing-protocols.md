# Routing Protocols: Distance Vector, Link State and BGP

**Prerequisites:** [packets, addressing and subnets](../tcp-ip-osi/01-packets-addressing-and-subnets.md) (routing tables, longest-prefix match), [graph algorithms](../../02-data-structures/graphs/02-graph-algorithms.md) (Dijkstra, Bellman-Ford), [shortest paths beyond Dijkstra](../../03-algorithms/graph-algorithms/01-all-pairs-and-heuristic-shortest-paths.md). **You will learn:** how routers **learn** where networks are instead of being configured by hand; the three families of routing protocol: **distance vector** (RIP: "tell your neighbors what you know"), **link state** (OSPF: "tell everyone about your links, then each computes the map") and **path vector** (BGP: the protocol that glues the whole internet together, driven by **business policy**); the classic failure **count to infinity** and its fix; **route selection and filtering rules**; and how **prefix hijacks** happen. Each protocol is implemented as a small simulation and checked against Dijkstra or expected paths.

## 1. The routing problem

A router forwards a packet by looking up its destination in the [routing table](../tcp-ip-osi/01-packets-addressing-and-subnets.md) (longest prefix match) and sending it to the **next hop**. Someone has to **fill that table**:

- **Static routes:** an administrator types them. Fine for a small office, impossible for thousands of routers and changing links.
- **Dynamic routing:** routers **run a protocol**, talk to each other, learn the network's shape, and **recompute automatically when a link fails**.

Two layers of routing exist:

| | **IGP** (interior gateway protocol) | **EGP** (exterior gateway protocol) |
|---|-------------------------------------|--------------------------------------|
| Where | **inside** one organization or ISP (one **autonomous system**, AS) | **between** autonomous systems (the internet) |
| Goal | find the **best (cheapest) path** | follow **business and policy** while keeping the internet connected |
| Protocols | **RIP**, **OSPF**, **IS-IS**, EIGRP | **BGP** (the only one in use) |
| Trust | all routers are yours | other organizations: you cannot trust, only filter |

An **autonomous system (AS)** is a network under one administrative control with its own policy, identified by an **AS number** (ASN): Google is AS15169, Cloudflare AS13335, your ISP has one too. There are about 75,000 active ASes.

## 2. A test network and a ground truth

We use one small topology throughout: routers `A` to `E`, links with **costs** (think delay or inverse bandwidth).

```text
  A ---1--- B ---2--- C ---4--- E
  |                   |         |
  5                   1         3
  |                   |         |
  +-------------------D---------+          (D links to A with cost 5, to C with cost 1, to E with cost 3)
```

```python
import heapq

LINKS = {("A", "B"): 1, ("B", "C"): 2, ("A", "D"): 5, ("C", "D"): 1, ("D", "E"): 3, ("C", "E"): 4}

def neighbors_of(links):
    adj = {}
    for (a, b), cost in links.items():
        adj.setdefault(a, {})[b] = cost
        adj.setdefault(b, {})[a] = cost
    return adj

def dijkstra_all(links):
    """Ground truth: {source: {destination: (cost, first_hop)}} from Dijkstra run at every router."""
    adj = neighbors_of(links)
    result = {}
    for source in adj:
        dist, first = {source: 0}, {source: None}
        heap = [(0, source, None)]
        while heap:
            d, node, hop = heapq.heappop(heap)
            if d > dist.get(node, float("inf")):
                continue
            for nxt, w in adj[node].items():
                nd = d + w
                if nd < dist.get(nxt, float("inf")):
                    dist[nxt] = nd
                    first[nxt] = nxt if node == source else first[node]
                    heapq.heappush(heap, (nd, nxt, hop))
        result[source] = {dest: (dist[dest], first[dest]) for dest in dist}
    return result

truth = dijkstra_all(LINKS)
print(truth["A"])                                       # {'A': (0, None), 'B': (1, 'B'), 'D': (4, 'B'), 'C': (3, 'B'), 'E': (7, 'B')}
```

From `A`, everything goes through `B` even `D` (cost 1 + 2 + 1 = 4, cheaper than the direct link of 5).

## 3. Distance vector (RIP): tell your neighbors what you know

**Idea ("routing by rumor"):** each router knows only the **cost to each destination, and which neighbor to send it through**. Periodically it sends its whole table (**the distance vector**) to its **direct neighbors**. When a router hears "neighbor `N` can reach `X` at cost `c`", and the link to `N` costs `w`, it can reach `X` via `N` at cost `w + c`; if that beats its current entry, it updates. This is the **Bellman-Ford algorithm run in a distributed way**.

```python
INF = 16                                                # RIP's "infinity": 16 hops means unreachable

def distance_vector(links, max_rounds=50):
    adj = neighbors_of(links)
    table = {r: {r: (0, None)} for r in adj}             # router -> destination -> (cost, next hop)
    for rounds in range(1, max_rounds + 1):
        snapshot = {r: dict(t) for r, t in table.items()}    # everybody sends the table they had at the start of the round
        changed = False
        for r in adj:
            for n, w in adj[r].items():
                for dest, (c, _) in snapshot[n].items():
                    new = w + c
                    if new < table[r].get(dest, (INF * 100, None))[0]:
                        table[r][dest] = (new, n)
                        changed = True
        if not changed:
            return table, rounds                         # converged: a full round without any update
    return table, max_rounds

dv, rounds = distance_vector(LINKS)
print("converged after", rounds, "rounds")              # converged after 4 rounds
print(dv["A"])                                          # {'A': (0, None), 'B': (1, 'B'), 'D': (4, 'B'), 'C': (3, 'B'), 'E': (7, 'B')}
print(all(dv[r][d] == truth[r][d] for r in dv for d in dv[r]), len(dv["A"]) == 5)      # True True   identical to Dijkstra's answer
```

Information travels **one hop per round**, so convergence takes about as many rounds as the network's diameter. Distance-vector is simple (each router needs no global map), uses little memory, and is what RIP uses (updates every 30 seconds, maximum 15 hops).

### The problem: count to infinity

Good news travels fast; **bad news travels slowly**. Take a line `A - B - C` (each link cost 1). Everyone knows C is reachable (`B` at cost 1, `A` at cost 2). Now the `B - C` link **breaks**. B loses its route to C, but **A still advertises "C is at cost 2"** (via B!). B believes A: "I can reach C through A at cost 3." Then A hears B's new route (cost 3) and updates to 4, and so on, each round adding 1, **bouncing between two routers**, until the cost reaches "infinity".

```python
def count_to_infinity(poison_reverse=False, infinity=16, max_rounds=100):
    # State right after the break: B lost its direct route to C, but A still believes "C via B at cost 2".
    cost_a, cost_b = 2, None                             # A's cost to C (via B); B's cost to C (unknown)
    history = [(cost_a, cost_b)]
    for _ in range(max_rounds):
        advertised_by_a = infinity if poison_reverse else cost_a     # poison reverse: A tells B "C is unreachable", since A's route to C goes THROUGH B
        new_b = min(infinity, 1 + advertised_by_a)                   # B hears A and adopts "C via A"
        new_a = min(infinity, 1 + new_b)                             # A then hears B's new cost and updates too
        if (new_a, new_b) == (cost_a, cost_b):
            break
        cost_a, cost_b = new_a, new_b
        history.append((cost_a, cost_b))
        if cost_a >= infinity and cost_b >= infinity:
            break
    return history

plain = count_to_infinity(poison_reverse=False)
print(len(plain) - 1, "rounds; costs (A, B):", plain[:6], "...")
# 8 rounds; costs (A, B): [(2, None), (4, 3), (6, 5), (8, 7), (10, 9), (12, 11)] ...
poisoned = count_to_infinity(poison_reverse=True)
print(len(poisoned) - 1, "round; costs (A, B):", poisoned)
# 1 round; costs (A, B): [(2, None), (16, 16)]
```

During the counting the network has a **routing loop**: packets for C bounce between A and B (their TTLs eventually run out, see the [packets lesson](../tcp-ip-osi/01-packets-addressing-and-subnets.md)), and convergence is painfully slow (RIP counts to 16 at 30 seconds per update: minutes of outage).

**Fixes used in practice:**

| Technique | Idea |
|-----------|------|
| **Small infinity** | declare 16 hops unreachable so counting stops quickly (but it limits RIP networks to 15 hops) |
| **Split horizon** | never advertise a route back to the neighbor you learned it from (A does not tell B about C, because it learned C from B) |
| **Poison reverse** | the stronger form: advertise that route **back with infinite cost**, so the neighbor learns immediately that you cannot help it |
| **Triggered updates** | send changes immediately instead of waiting for the periodic timer |
| **Hold-down timers** | after a route fails, ignore worse-looking news about it for a while |

(Split horizon and poison reverse fix this two-router loop but not every loop; three-router loops still count. This is a main reason large networks moved to link-state.)

## 4. Link state (OSPF, IS-IS): everyone gets the whole map

**Idea:** instead of sharing *conclusions* (distances), share the *facts*: each router describes **its own links** in a **link-state advertisement (LSA)** and **floods it to every router** in the network. After flooding, **every router has the same complete map** (the **link-state database, LSDB**) and runs **Dijkstra itself** to compute its own shortest-path tree. There are no rumors to go stale: each router computes from the same facts.

```python
from collections import deque

def link_state(links):
    adj = neighbors_of(links)
    # each router originates one LSA: (origin, sequence number, its own links)
    lsas = {r: (r, 1, dict(adj[r])) for r in adj}
    lsdb = {r: {} for r in adj}                           # each router's copy of the database
    messages = 0
    for origin, lsa in lsas.items():                      # flood each LSA through the network
        queue = deque([(origin, None)])                   # (router that just received it, neighbor it came from)
        lsdb[origin][origin] = lsa
        while queue:
            router, came_from = queue.popleft()
            for n in adj[router]:
                if n == came_from:
                    continue                              # do not send it back
                messages += 1
                known = lsdb[n].get(origin)
                if known is None or known[1] < lsa[1]:    # NEW information (higher sequence number): store and forward it
                    lsdb[n][origin] = lsa
                    queue.append((n, router))
    return lsdb, messages

def spf_from_lsdb(db, source):
    """Dijkstra on the topology a router learned from LSAs."""
    graph = {origin: lsa[2] for origin, lsa in db.items()}
    dist, first = {source: 0}, {source: None}
    heap = [(0, source)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue
        for nxt, w in graph[node].items():
            if d + w < dist.get(nxt, float("inf")):
                dist[nxt] = d + w
                first[nxt] = nxt if node == source else first[node]
                heapq.heappush(heap, (d + w, nxt))
    return {dest: (dist[dest], first[dest]) for dest in dist}

lsdb, messages = link_state(LINKS)
print(all(len(lsdb[r]) == 5 for r in lsdb), "| LSA transmissions:", messages)      # True | LSA transmissions: 40
print(all(spf_from_lsdb(lsdb[r], r) == truth[r] for r in lsdb))                   # True    every router computed the same shortest paths as the ground truth
print(lsdb["E"]["A"])                                                             # ('A', 1, {'B': 1, 'D': 5})      E has A's exact link list, flooded hop by hop
```

Why link-state is preferred inside large networks:

| | Distance vector | Link state |
|---|-----------------|------------|
| Each router knows | distances only | the **whole topology** |
| Convergence | slow, loops possible (count to infinity) | fast, loop-free once flooding completes |
| Messages | whole table to neighbors, periodically | only **changes**, flooded when a link changes |
| CPU and memory | low | higher (an LSDB and Dijkstra), scaled by splitting into **areas** |
| Metrics | hop count (RIP) | configurable cost (bandwidth-based), supports **equal-cost multipath (ECMP)** |
| Examples | RIP, early IGRP | **OSPF**, **IS-IS** (used by almost every ISP and data center) |

**Practical OSPF notions:** routers form **adjacencies** by exchanging **hello** packets, elect a **designated router** on shared segments, group the network into **areas** (area 0 is the backbone) so that LSAs do not flood the whole network, and use **sequence numbers and ages** so stale LSAs are discarded. Link cost defaults to `reference bandwidth / interface bandwidth`, so faster links look "closer".

### Reacting to a failure

When a link goes down, the two routers on it flood a **new LSA** (sequence number 2) with that link removed; every router updates its LSDB and re-runs Dijkstra:

```python
LINKS_AFTER = {k: v for k, v in LINKS.items() if k != ("B", "C")}          # the B-C link fails
after = dijkstra_all(LINKS_AFTER)
print(truth["A"]["C"], "->", after["A"]["C"])           # (3, 'B') -> (6, 'D')    A now reaches C through D (5 + 1 = 6)
print(truth["B"]["E"], "->", after["B"]["E"])           # (6, 'C') -> (9, 'A')    B's best path to E changes from B-C-D-E to B-A-D-E
```

Convergence for OSPF is typically **sub-second** on modern gear (tuned timers plus fast failure detection such as BFD), versus minutes for classic RIP.

## 5. BGP: routing between organizations

Inside an AS the goal is "cheapest path". **Between** ASes (different companies who are partners, customers, or competitors) the goal is **business policy**: *who pays whom, whose traffic do I carry, which routes do I even want to hear?* **BGP (Border Gateway Protocol)** is the protocol that connects the roughly 75,000 ASes of the internet. It is a **path-vector** protocol: each route advertisement carries the **list of ASes the route has passed through (the AS path)**.

```text
BGP advertisement:   prefix 203.0.113.0/24   AS_PATH = [64500, 64510, 64520]   next hop = ...
meaning: "traffic for this prefix can go through AS 64500, which reaches it via AS 64510, which originates it (AS 64520)"
```

Properties:

- **Loop prevention for free:** if a router sees **its own AS number** in an incoming AS path, it **rejects** the route (it would loop). No count-to-infinity.
- **Policy, not just metrics:** the best route is chosen by rules the operator sets, **before** path length matters.
- **Runs over TCP (port 179)**; sends **incremental updates** only; sessions are manually configured between neighbors (eBGP between ASes, iBGP inside).
- **Scale:** the global table has about 1,000,000 IPv4 prefixes. Convergence can take minutes; the system is stable but slow and fragile.

### Business relationships and export rules

ASes relate in two main ways: **customer-provider** (the customer **pays** the provider for transit to the entire internet) and **peer-to-peer** (two ASes exchange traffic for their own customers **for free**). That produces the **Gao-Rexford rules** that nearly all real routing follows:

| Route learned from | Preference (higher wins) | May be exported to |
|--------------------|--------------------------|--------------------|
| a **customer** | **highest** (it earns money) | **everyone** (customers, peers, providers) |
| a **peer** | middle (free) | **customers only** |
| a **provider** | **lowest** (it costs money) | **customers only** |

An AS announces its customers' routes to the world (to attract paying traffic), but it will **not give free transit**: it never takes a route learned from one provider or peer and re-announces it to another provider or peer. The result is **valley-free** paths: up the hierarchy (customer to provider), at most one peer link across the top, then down.

### A BGP simulation

```python
CUSTOMER, PEER, PROVIDER = "customer", "peer", "provider"       # how a route was learned (relative to the receiving AS)
RANK = {CUSTOMER: 3, PEER: 2, PROVIDER: 1, "origin": 4}         # local preference: customer > peer > provider

class Internet:
    def __init__(self, customer_of=(), peers=()):
        self.rel = {}                                            # rel[a][b] = what b is TO a ("customer", "peer", "provider")
        for cust, prov in customer_of:
            self.rel.setdefault(cust, {})[prov] = PROVIDER
            self.rel.setdefault(prov, {})[cust] = CUSTOMER
        for a, b in peers:
            self.rel.setdefault(a, {})[b] = PEER
            self.rel.setdefault(b, {})[a] = PEER

    def propagate(self, origin):
        """Return {asn: (path, learned_from)} after BGP converges for a prefix originated by `origin`."""
        best = {origin: ((origin,), "origin")}
        changed = True
        while changed:
            changed = False
            for sender in list(best):
                path, learned_from = best[sender]
                for receiver, role_of_receiver in self.rel[sender].items():
                    # EXPORT rule (sender's side): customer/own routes go to everyone; peer/provider routes go to customers only
                    if learned_from not in (CUSTOMER, "origin") and role_of_receiver != CUSTOMER:
                        continue
                    if receiver in path:
                        continue                                # LOOP PREVENTION: my own AS is already in the path
                    candidate = ((receiver,) + path, self.rel[receiver][sender])      # prepend myself; how I learned it = what the sender is to me
                    current = best.get(receiver)
                    # SELECTION: higher local-pref first, then shorter AS path, then lowest neighbor AS number as a tie-break
                    key = lambda route: (-RANK[route[1]], len(route[0]), route[0][1] if len(route[0]) > 1 else 0)
                    if current is None or key(candidate) < key(current):
                        best[receiver] = candidate
                        changed = True
        return best

#      AS1 ====peer==== AS2           (tier-1 style providers, peering with each other)
#     /   \                \
#   AS3    AS7             AS4        AS3 and AS7 are customers of AS1; AS4 is a customer of AS2
#     \                    /
#      +------ AS5 -------+           AS5 is a customer of BOTH AS3 and AS4 (multi-homed)
net = Internet(customer_of=[(3, 1), (7, 1), (4, 2), (5, 3), (5, 4)], peers=[(1, 2)])

routes = net.propagate(origin=5)                                # AS5 announces its prefix
for asn in sorted(routes):
    path, how = routes[asn]
    print(f"AS{asn} -> AS5 : path {list(path)} learned from a {how}")
# AS1 -> AS5 : path [1, 3, 5] learned from a customer
# AS2 -> AS5 : path [2, 4, 5] learned from a customer
# AS3 -> AS5 : path [3, 5] learned from a customer
# AS4 -> AS5 : path [4, 5] learned from a customer
# AS5 -> AS5 : path [5] learned from a origin
# AS7 -> AS5 : path [7, 1, 3, 5] learned from a provider
```

Read the results: AS1 and AS2 each reach AS5 through **their own customer** (a customer route is preferred and earns revenue), not through their peer. AS7 has a single provider, so its path goes up to AS1 and down through AS3.

Now the other direction, a prefix originated by AS7, and watch **policy and path length** decide for the multi-homed AS5:

```python
routes = net.propagate(origin=7)
for asn in (1, 2, 3, 4, 5):
    path, how = routes[asn]
    print(f"AS{asn} -> AS7 : path {list(path)} learned from a {how}")
# AS1 -> AS7 : path [1, 7] learned from a customer
# AS2 -> AS7 : path [2, 1, 7] learned from a peer
# AS3 -> AS7 : path [3, 1, 7] learned from a provider
# AS4 -> AS7 : path [4, 2, 1, 7] learned from a provider
# AS5 -> AS7 : path [5, 3, 1, 7] learned from a provider
```

AS5 hears two routes to AS7: via AS3 (`[5,3,1,7]`, length 4) and via AS4 (`[5,4,2,1,7]`, length 5). Both come from **providers** (same local preference), so the **shorter AS path** wins. If AS5 wanted its traffic to prefer the cheaper or faster provider regardless of length, it would raise that neighbor's **local preference**: this is the knob operators use for **traffic engineering**.

**Valley-free check:** AS5 does **not** carry traffic between its two providers. With the export rules, AS5 never announces AS3's route to AS4 (a provider route may only go to customers), so it cannot become a free transit path:

```python
def exports_to(asn, neighbor, routes_for_origin, net):
    """Would `asn` announce its best route for this prefix to `neighbor`?"""
    path, learned_from = routes_for_origin[asn]
    return learned_from in (CUSTOMER, "origin") or net.rel[asn][neighbor] == CUSTOMER

print(exports_to(5, 4, routes, net), exports_to(5, 3, routes, net))              # False False    the route to AS7 came from a provider, so AS5 will not advertise it to its other provider
print(exports_to(1, 2, net.propagate(origin=5), net), exports_to(1, 7, net.propagate(origin=5), net))      # True True   AS1 learned AS5's route from a customer, so it tells its peer and its customer
```

### BGP attributes in practice

The decision process compares routes in order (a simplified Cisco/standard list): **highest LOCAL_PREF** (policy), **shortest AS_PATH**, **lowest origin type**, **lowest MED** (a hint from a neighbor AS), **eBGP over iBGP**, **lowest IGP cost to the exit**, then tie-breakers. Operators also use **AS-path prepending** (adding their own ASN repeatedly to make a path look longer and steer inbound traffic away), **communities** (tags that request actions such as "do not export to AS X"), and **prefix filters**.

## 6. Prefix hijacks and why BGP security matters

BGP was designed in a friendlier internet: **a neighbor's announcements are largely trusted**. If an AS announces a prefix it does not own, other networks may believe it. And because routers use **longest prefix match**, a more specific announcement **always wins**, even if bogus:

```python
import ipaddress

def lookup(table, destination):
    ip = ipaddress.ip_address(destination)
    matches = [(net, owner) for net, owner in table if ip in net]
    return max(matches, key=lambda m: m[0].prefixlen)[1] if matches else None

table = [(ipaddress.ip_network("203.0.113.0/24"), "AS64500 (legitimate owner)")]
print(lookup(table, "203.0.113.77"))                              # AS64500 (legitimate owner)

table.append((ipaddress.ip_network("203.0.113.0/25"), "AS666 (attacker)"))          # a MORE SPECIFIC bogus announcement
print(lookup(table, "203.0.113.77"))                              # AS666 (attacker)       traffic for .0 - .127 now flows to the attacker
print(lookup(table, "203.0.113.200"))                             # AS64500 (legitimate owner)   the other half is unaffected
```

Famous incidents: **Pakistan Telecom and YouTube (2008)** (an ISP announcing a more specific YouTube prefix to block it locally accidentally black-holed YouTube worldwide for about two hours), **Facebook (2021)** (a configuration change withdrew Facebook's own BGP routes, taking the company and its DNS off the internet for hours), and cryptocurrency thefts using hijacked prefixes.

Defenses (partial, deployment is ongoing):

| Defense | What it does |
|---------|--------------|
| **Prefix and AS-path filtering** | customers may announce only prefixes registered to them (IRR databases); the most important defense |
| **Max-prefix limits** | tear down a session if a neighbor suddenly announces far too many prefixes |
| **RPKI and Route Origin Validation (ROV)** | owners publish signed **ROAs** ("AS64500 may originate 203.0.113.0/24, up to /24"); routers drop announcements that contradict them |
| **BGPsec / ASPA** | sign or validate the path, not just the origin (slow adoption) |
| **Monitoring** | RIPEstat, BGPStream, Cloudflare Radar detect leaks and hijacks |

```python
ROAS = {ipaddress.ip_network("203.0.113.0/24"): (64500, 24)}      # prefix -> (authorized origin AS, maximum allowed prefix length)

def validate(prefix, origin_as):
    prefix = ipaddress.ip_network(prefix)
    for roa_net, (roa_as, max_len) in ROAS.items():
        if prefix.subnet_of(roa_net):
            return "valid" if origin_as == roa_as and prefix.prefixlen <= max_len else "invalid"
    return "unknown"                                               # no ROA covers it

print(validate("203.0.113.0/24", 64500), validate("203.0.113.0/25", 666), validate("203.0.113.0/24", 666), validate("198.51.100.0/24", 64500))
# valid invalid invalid unknown      the hijack above is detected: wrong origin AND longer than the ROA allows
```

## 7. Other things routers do with routes

- **Administrative distance:** when several protocols offer a route, the router trusts them in a fixed order (connected 0, static 1, eBGP 20, OSPF 110, RIP 120, iBGP 200).
- **Route redistribution:** importing routes from one protocol into another (carefully: loops and suboptimal paths).
- **Equal-cost multipath (ECMP):** if two next hops have equal cost, spread flows across both (hashing the 5-tuple so a flow stays on one path).
- **Anycast:** many servers announce the **same prefix** from different places; routing delivers each client to the **nearest** one. Root DNS servers, CDNs and DDoS-scrubbing services rely on it ([DNS lab](../dns-http/02-dns-in-depth.md)).
- **Default route:** `0.0.0.0/0` points to the ISP; most end-user routers know only their own networks plus a default.
- **Software-defined networking (SDN):** a central controller computes paths and programs switches, replacing distributed protocols in some data centers; the big cloud providers still run BGP inside their data-center fabrics.

## 8. Tools you can use

```bash
ip route                         # Linux: the routing table      |  netstat -rn / route -n get default on macOS
traceroute example.com           # hops (via increasing TTL)      |  mtr example.com for a live view
whois -h whois.radb.net AS15169  # what an AS announces (Internet Routing Registry)
curl https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS15169     # prefixes an AS originates (RIPEstat)
# bgp.he.net and bgp.tools: look up an ASN, its peers and prefixes; looking glasses show a route from another network's viewpoint
```

## 9. Two real-world examples

**Example 1: A data center that runs BGP everywhere.** Large data centers use **BGP as their only routing protocol** in a leaf-and-spine fabric: each rack switch is its own AS, ECMP spreads traffic over all spines, and a link or switch failure is withdrawn in milliseconds. Operators like it because BGP is simple, scalable and has precise policy control, and because the same protocol connects the data center to the internet.

**Example 2: The 2021 Facebook outage.** During maintenance a command accidentally withdrew the BGP routes that told the world how to reach Facebook's DNS servers. Within minutes every resolver on Earth lost the path to those servers, so `facebook.com` stopped resolving, apps failed, and the engineers' own tools (and building access badges) that relied on the same network went dark. It shows both how **powerful and how brittle** BGP is: one announcement, or one withdrawal, changes global reachability.

## 10. Common mistakes

- Treating RIP as acceptable for anything but tiny networks (15-hop limit, slow convergence).
- Forgetting split horizon / poison reverse, or hold-down timers, in distance-vector designs.
- Letting a customer announce arbitrary prefixes (no filters) or **leaking** provider routes to another provider (the textbook cause of internet-wide outages).
- Assuming BGP picks the **fastest** path: it picks by **policy**, then AS-path length, which ignores latency.
- Forgetting that a **more specific prefix always wins**, including when it is a mistake or an attack.
- Running OSPF with one huge area instead of splitting into areas, or mismatched timers/MTU that prevent adjacencies.
- Redistributing routes between protocols without filters (loops).
- Believing "a route exists" means "traffic flows": policy, firewalls and asymmetric paths still matter.

## 11. Practice

1. Run `distance_vector` after removing the `D-E` link. Which destinations become unreachable from `E`, if any, and how does the table at `A` change for `E`?
2. In the three-router chain `A - B - C` (cost 1 each), how many rounds does count-to-infinity take with `infinity = 16`? Why does poison reverse stop it immediately?
3. Why does OSPF flood LSAs with **sequence numbers**?
4. Add an `AS8` that is a customer of `AS2` and run `propagate(origin=8)`. What path does AS5 choose?
5. Write `valley_free(path, net)` that checks an AS path goes up (customer to provider) zero or more times, across at most one peer link, then down.
6. Which BGP route wins: (a) a customer route with AS path length 5, (b) a peer route with length 2, (c) a provider route with length 1? Why?
7. How does RPKI prevent the `/25` hijack above, and what does it not protect against?
8. Why is link-state preferred over distance vector in large networks?

<details>
<summary>Solutions</summary>

1. ```python
   no_de = {k: v for k, v in LINKS.items() if k != ("D", "E")}
   table, rounds = distance_vector(no_de)
   print(table["E"], rounds)
   # {'E': (0, None), 'C': (4, 'C'), 'B': (6, 'C'), 'D': (5, 'C'), 'A': (7, 'C')} 4
   print(table["A"]["E"])                                 # (7, 'B')
   ```
   `E` is still reachable (through `C`, cost 4): nothing becomes unreachable. `A`'s route to `E` is unchanged (cost 7 via `B`), because `A` never used the `D-E` link.
2. The costs grow by two per round (A: 2, 4, 6, ... and B: 3, 5, 7, ...), so reaching 16 takes **8 rounds** in our simulation, with a loop the whole time. With poison reverse, A tells B "C costs 16 (unreachable)" because A's route to C goes through B, so B immediately learns C is gone and the loop never forms.
3. Because the same LSA may arrive over several paths and routers must tell **new from old**: a higher sequence number means newer information; equal or lower is a duplicate to drop (this also stops flooding loops).
4. ```python
   net8 = Internet(customer_of=[(3, 1), (7, 1), (4, 2), (5, 3), (5, 4), (8, 2)], peers=[(1, 2)])
   routes8 = net8.propagate(origin=8)
   print(list(routes8[5][0]), routes8[5][1])             # [5, 4, 2, 8] provider
   ```
   AS5 hears AS8 via AS4 (`[5,4,2,8]`, length 4) and via AS3 (`[5,3,1,2,8]`, length 5): both from providers, so the shorter one through AS4 wins.
5. ```python
   def valley_free(path, net):
       phase = "up"                                        # going up through providers
       peers_used = 0
       for a, b in zip(path, path[1:]):
           role = net.rel[a][b]                            # what b is to a
           if role == PROVIDER:                            # a -> its provider: only allowed while still going up
               if phase != "up":
                   return False
           elif role == PEER:                              # at most one peer hop, only at the top
               peers_used += 1
               if phase != "up" or peers_used > 1:
                   return False
               phase = "down"
           else:                                           # a -> its customer: going down; no more climbing afterwards
               phase = "down"
       return True
   print(valley_free([7, 1, 3, 5], net), valley_free([5, 3, 1, 2, 4], net), valley_free([3, 5, 4], net))
   # True True False      (the last path goes down to AS5 and then up to AS4: a "valley")
   ```
6. The **customer route (a)** wins: local preference (customer over peer over provider) is checked **before** AS-path length, because customer routes earn money and provider routes cost money.
7. With a ROA for `203.0.113.0/24` (origin AS64500, max length 24), routers doing ROV mark `203.0.113.0/25 from AS666` **invalid** (wrong origin and too long) and drop it. RPKI validates only the **origin** of a prefix: it does not stop an attacker who forges the correct origin by *appending* the legitimate AS to a bogus path, nor does it stop **route leaks** with valid origins; path validation (ASPA/BGPsec) is needed for that.
8. Each router has the full topology (no stale rumors), so convergence is fast and loop-free; updates are incremental and flooded only on change; costs can be flexible; and areas bound the size of the flooding domain. Distance vector can loop and counts slowly to infinity.

</details>

## 12. Check yourself

1. What is the difference between an IGP and BGP?
2. How does distance-vector routing work, and why does it count to infinity?
3. How does link-state routing work, and what does each router compute?
4. What is an AS path used for?
5. State the Gao-Rexford preference and export rules.
6. How can a more specific prefix hijack traffic, and what stops it?

<details>
<summary>Answers</summary>

1. An IGP (OSPF, IS-IS, RIP) runs inside one organization to find cheapest paths; BGP runs between autonomous systems and selects routes by business policy.
2. Routers send their distance tables to neighbors and adopt `neighbor's distance + link cost` when it is better (distributed Bellman-Ford). After a failure, neighbors keep advertising routes that depended on the broken link, raising costs by one each exchange (count to infinity).
3. Each router floods an LSA of its own links; all routers end with the same topology database and each runs Dijkstra to compute its own shortest-path tree.
4. It lists the ASes a route passed through: loop prevention (reject paths containing your own ASN), path-length comparison and policy filtering.
5. Prefer customer routes over peer routes over provider routes; export customer routes to everyone, but export peer and provider routes only to customers (no free transit).
6. Routers forward by longest prefix match, so a more specific announcement wins even if bogus; defenses are prefix filters, max-prefix limits, RPKI route origin validation and monitoring.

</details>

[Back to networking](../README.md)
