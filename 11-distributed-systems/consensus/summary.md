# Consensus: One-Page Summary

## Key facts

- **Why consensus:** nodes must agree on one value or one ordered log even when nodes crash and messages are delayed; used for leader election, configuration and replicated state machines.
- **Raft roles:** each node is a follower, candidate or leader; time is divided into numbered **terms** with at most one leader per term.
- **Election:** a follower that hears nothing for a randomised timeout becomes a candidate and asks for votes; a majority wins. Randomised timeouts avoid repeated split votes.
- **Log replication:** the leader appends client commands, sends them to followers, and **commits** an entry once a majority stored it; followers apply committed entries in order.
- **Safety rules:** a node votes once per term and only for a candidate whose log is at least as up to date as its own; a leader never overwrites its own log; committed entries survive leader changes.
- **Majorities:** a cluster of `2f + 1` nodes tolerates `f` failures (3 nodes survive 1, 5 nodes survive 2); a partitioned minority cannot elect a leader or commit.
- **When you need it:** coordination services and strongly consistent stores, not for ordinary application data you can design around.

## Pitfalls

- Even-sized clusters (4 nodes tolerate no more failures than 3).
- Skipping the log up-to-date check when voting (the experiment shows it breaks safety).
- Serving reads from a leader that has been partitioned away without confirming leadership.
- Building your own consensus protocol instead of using a proven implementation.

## Self-check

- **What are agreement, validity and termination?** Agreement: no two nodes decide differently; validity: the decided value was proposed by some node; termination: a decision is eventually reached.
- **What does the FLP result say, and how do real algorithms respond?** In a fully asynchronous system with even one crash, no deterministic algorithm can always terminate. Real algorithms keep safety always and give up liveness during bad network periods (using timeouts and randomisation to make progress likely).
- **What is a term, and why does a higher term always win?** A term is a numbered epoch with at most one leader; a node seeing a higher term knows its information is stale and steps down.
- **List the steps of a Raft election.** A follower times out, increments its term, becomes a candidate, votes for itself, requests votes; nodes grant one vote per term to an up-to-date candidate; a majority makes it leader, which sends heartbeats.
- **When is a log entry committed?** When the leader has stored it on a majority of nodes (and, directly, for an entry of its own term); it then applies it and followers learn the commit index.
- **Why can a minority partition not make progress, and why is that desirable?** It cannot gather a majority of votes or acknowledgements, so it cannot elect a leader or commit; this prevents two sides of a partition from making conflicting decisions (split brain).

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Consensus and Raft](01-consensus-and-raft.md)
