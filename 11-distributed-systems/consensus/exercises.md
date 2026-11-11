# Consensus: Exercises

These problems go with the [Consensus lesson](README.md). Try each one before opening its solution.

## Problems

1. How many failures can 7 nodes tolerate? What is the minimum number of votes to elect a leader?
2. In experiment 1, print each node's `term`. Why are they all equal after recovery?
3. Why must a node vote at most once per term? What could go wrong otherwise?
4. Explain why a candidate whose log is behind cannot win, using the up-to-date check.
5. Break the algorithm: set `up_to_date = True` in `RequestVote` handling and rerun `random_run` over seeds. (Do it on a copy: restore the line afterwards.) What does the harness report?
6. What is a fencing token, and what failure does it prevent?

<details>
<summary>Solutions</summary>

1. `7 = 2f + 1` gives `f = 3`; a majority is 4 votes.
2. Run `print([n.term for n in c.nodes])` right after experiment 1: it prints `[2, 2, 2, 2, 2]`. Every message carries the sender's term and a node adopts any higher term it sees, so after the old leader hears from the new one, all terms converge.
3. If a node could vote for two candidates in one term, both could collect a majority, giving two leaders in the same term; they could commit conflicting entries.
4. Votes are granted only if the candidate's `(last_term, last_index)` is at least the voter's. A committed entry is on a majority of nodes, and any winning candidate needs votes from a majority, so at least one voter holds that entry; that voter rejects a candidate that lacks it.
5. Change the line to `up_to_date = True` and run `random_run` over seeds 0 to 299: **53 of the 300 runs report a violation** (with the correct rule: 0). A node with a stale log can now win an election and overwrite entries that were already committed. The harness catches the broken rule, which is why such randomized testing is worth writing.
6. A number that increases with each leadership or lock grant; a storage service rejects any write carrying a token lower than one it has already seen. It prevents a deposed leader (paused, then waking up believing it is still leader) from overwriting newer data.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Consensus and Raft](01-consensus-and-raft.md)
