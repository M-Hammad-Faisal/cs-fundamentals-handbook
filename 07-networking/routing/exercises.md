# Routing: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## Routing Protocols

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

1. ```python no-run
   no_de = {k: v for k, v in LINKS.items() if k != ("D", "E")}
   table, rounds = distance_vector(no_de)
   print(table["E"], rounds)
   # {'E': (0, None), 'C': (4, 'C'), 'B': (6, 'C'), 'D': (5, 'C'), 'A': (7, 'C')} 4
   print(table["A"]["E"])                                 # (7, 'B')
   ```
   `E` is still reachable (through `C`, cost 4): nothing becomes unreachable. `A`'s route to `E` is unchanged (cost 7 via `B`), because `A` never used the `D-E` link.
2. The costs grow by two per round (A: 2, 4, 6, ... and B: 3, 5, 7, ...), so reaching 16 takes **8 rounds** in our simulation, with a loop the whole time. With poison reverse, A tells B "C costs 16 (unreachable)" because A's route to C goes through B, so B immediately learns C is gone and the loop never forms.
3. Because the same LSA may arrive over several paths and routers must tell **new from old**: a higher sequence number means newer information; equal or lower is a duplicate to drop (this also stops flooding loops).
4. ```python no-run
   net8 = Internet(customer_of=[(3, 1), (7, 1), (4, 2), (5, 3), (5, 4), (8, 2)], peers=[(1, 2)])
   routes8 = net8.propagate(origin=8)
   print(list(routes8[5][0]), routes8[5][1])             # [5, 4, 2, 8] provider
   ```
   AS5 hears AS8 via AS4 (`[5,4,2,8]`, length 4) and via AS3 (`[5,3,1,2,8]`, length 5): both from providers, so the shorter one through AS4 wins.
5. ```python no-run
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

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Routing Protocols](01-routing-protocols.md)
