# Consensus: One-Page Summary

## Questions worth remembering

- **What are agreement, validity and termination?** Agreement: no two nodes decide differently; validity: the decided value was proposed by some node; termination: a decision is eventually reached.
- **What does the FLP result say, and how do real algorithms respond?** In a fully asynchronous system with even one crash, no deterministic algorithm can always terminate. Real algorithms keep safety always and give up liveness during bad network periods (using timeouts and randomisation to make progress likely).
- **What is a term, and why does a higher term always win?** A term is a numbered epoch with at most one leader; a node seeing a higher term knows its information is stale and steps down.
- **List the steps of a Raft election.** A follower times out, increments its term, becomes a candidate, votes for itself, requests votes; nodes grant one vote per term to an up-to-date candidate; a majority makes it leader, which sends heartbeats.
- **When is a log entry committed?** When the leader has stored it on a majority of nodes (and, directly, for an entry of its own term); it then applies it and followers learn the commit index.
- **Why can a minority partition not make progress, and why is that desirable?** It cannot gather a majority of votes or acknowledgements, so it cannot elect a leader or commit; this prevents two sides of a partition from making conflicting decisions (split brain).

Practice problems with solutions are in the **Practice** section of each lesson.

[Lesson](README.md) · [Consensus and Raft](01-consensus-and-raft.md)
