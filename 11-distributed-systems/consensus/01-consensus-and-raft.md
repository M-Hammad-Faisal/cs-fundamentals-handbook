# Consensus and Raft: Agreeing Despite Failures

**Prerequisites:** [Failures, time and clocks](../foundations/01-failures-time-and-clocks.md), [replication and sharding](../replication-sharding/01-replication-and-sharding.md), [classes](../../04-oop/classes-objects/README.md). **You will learn:** what **consensus** is and why it is hard, the **Raft** algorithm (leader election, log replication, commitment), and you will **run a working Raft simulator**: elect a leader, replicate a log, crash the leader, partition the network and check **safety** properties across hundreds of random failure runs.

## 1. In plain words

Five friends must agree on a restaurant by text message, but messages get lost and some friends' phones die. **Consensus** is getting a group of machines to agree on **one value** (or one ordered sequence of values) even though some machines crash and messages are lost or delayed. It is the foundation of replicated databases, lock services (etcd, ZooKeeper, Consul), Kubernetes' control plane and leader election.

Requirements:

- **Agreement (safety):** no two nodes decide different values.
- **Validity:** the decided value was proposed by someone.
- **Termination (liveness):** if enough nodes stay up and the network behaves, a decision is eventually made.

The **FLP result** proves no algorithm can guarantee termination in a fully asynchronous network with even one crash, so practical algorithms (Paxos, Raft, Zab) always keep **safety** and give up **liveness** when the network misbehaves (for example during a partition they may stall rather than risk a wrong answer). With `N = 2f + 1` nodes they tolerate `f` crashes: 3 nodes survive 1 failure, 5 survive 2.

## 2. Raft in one page

Raft solves consensus by electing a **leader** who orders all changes in a **replicated log**.

**Roles:** every node is a **follower**, **candidate** or **leader**. Time is divided into **terms** (numbered, increasing); each term has at most one leader.

**Leader election.**
1. A follower that hears no heartbeat for a random **election timeout** becomes a candidate, increments its term, votes for itself and asks everyone for votes (`RequestVote`).
2. A node grants **one vote per term**, and only to a candidate whose log is **at least as up to date** as its own.
3. A candidate with votes from a **majority** becomes leader and sends **heartbeats** (`AppendEntries`) to stop new elections. Random timeouts make split votes rare.

**Log replication.**
1. Clients send commands to the leader, which appends `(term, command)` to its log and sends `AppendEntries` to followers.
2. A follower accepts entries only if its log **matches** the leader's at the previous index and term (the **log matching** property); otherwise it refuses, and the leader backs up and retries.
3. When an entry is stored on a **majority**, the leader marks it **committed** and applies it; followers learn the commit index from later messages.

**Safety rules** that make it correct: majority votes mean two leaders in one term are impossible; the up-to-date vote rule means a new leader always contains every committed entry; a leader only commits entries from its **own term** directly (older ones are committed along with them).

## 3. A Raft simulator

The code below is a compact but faithful Raft: elections, replication, backtracking, commitment, crashes (a node keeps its term, vote and log, like data on disk) and partitions. Messages travel through a simulated network with random delay, and a seeded random generator makes every run repeatable.

```python
import random

HEARTBEAT = 3

class Node:
    def __init__(self, nid, cluster):
        self.id, self.cluster = nid, cluster
        self.alive = True
        self.state = "follower"
        self.term = 0
        self.voted_for = None
        self.log = []                  # entries are (term, command); log index 1 is log[0]
        self.commit = 0
        self.votes = set()
        self.next_index, self.match_index = {}, {}
        self.reset_timer()

    def reset_timer(self):
        self.elapsed = 0
        self.timeout = self.cluster.rng.randint(10, 20)      # randomized so nodes rarely time out together

    def last_log(self):
        return (self.log[-1][0] if self.log else 0, len(self.log))     # (last term, last index)

    def step_down(self, term):
        self.term, self.state, self.voted_for = term, "follower", None

    def tick(self):
        if not self.alive:
            return
        self.elapsed += 1
        if self.state == "leader":
            if self.elapsed >= HEARTBEAT:
                self.elapsed = 0
                self.broadcast_append()
        elif self.elapsed >= self.timeout:                   # no heartbeat heard: start an election
            self.state, self.voted_for = "candidate", self.id
            self.term += 1
            self.votes = {self.id}
            self.reset_timer()
            last_term, last_index = self.last_log()
            for peer in self.cluster.peers(self.id):
                self.cluster.send(self.id, peer, {"type": "RequestVote", "term": self.term,
                                                  "last_term": last_term, "last_index": last_index})

    def broadcast_append(self):
        for peer in self.cluster.peers(self.id):
            prev_index = self.next_index[peer] - 1
            prev_term = self.log[prev_index - 1][0] if prev_index > 0 else 0
            self.cluster.send(self.id, peer, {"type": "AppendEntries", "term": self.term,
                                              "prev_index": prev_index, "prev_term": prev_term,
                                              "entries": self.log[prev_index:], "leader_commit": self.commit})

    def handle(self, src, m):
        if not self.alive:
            return
        if m["term"] > self.term:
            self.step_down(m["term"])                        # a higher term always wins
        kind = m["type"]
        if kind == "RequestVote":
            my_last_term, my_last_index = self.last_log()
            up_to_date = (m["last_term"], m["last_index"]) >= (my_last_term, my_last_index)
            grant = m["term"] == self.term and self.voted_for in (None, src) and up_to_date
            if grant:
                self.voted_for = src
                self.reset_timer()
            self.cluster.send(self.id, src, {"type": "VoteReply", "term": self.term, "granted": grant})
        elif kind == "VoteReply":
            if self.state == "candidate" and m["term"] == self.term and m["granted"]:
                self.votes.add(src)
                if len(self.votes) > self.cluster.n // 2:    # a majority
                    self.become_leader()
        elif kind == "AppendEntries":
            if m["term"] < self.term:                        # message from a stale leader
                self.cluster.send(self.id, src, {"type": "AppendReply", "term": self.term, "success": False, "match": 0})
                return
            self.state = "follower"
            self.reset_timer()
            pi = m["prev_index"]
            if pi > 0 and (len(self.log) < pi or self.log[pi - 1][0] != m["prev_term"]):
                self.cluster.send(self.id, src, {"type": "AppendReply", "term": self.term, "success": False, "match": 0})
                return                                        # log does not match here: leader must back up
            for offset, entry in enumerate(m["entries"]):
                idx = pi + 1 + offset
                if len(self.log) >= idx and self.log[idx - 1][0] != entry[0]:
                    del self.log[idx - 1:]                    # conflicting entries from an old leader are discarded
                if len(self.log) < idx:
                    self.log.append(entry)
            if m["leader_commit"] > self.commit:
                self.commit = min(m["leader_commit"], pi + len(m["entries"]))
            self.cluster.send(self.id, src, {"type": "AppendReply", "term": self.term, "success": True,
                                             "match": pi + len(m["entries"])})
        elif kind == "AppendReply":
            if self.state != "leader" or m["term"] != self.term:
                return
            if m["success"]:
                self.match_index[src] = m["match"]
                self.next_index[src] = m["match"] + 1
                for n in range(len(self.log), self.commit, -1):          # highest index stored on a majority
                    replicated = 1 + sum(1 for p in self.cluster.peers(self.id) if self.match_index[p] >= n)
                    if replicated > self.cluster.n // 2 and self.log[n - 1][0] == self.term:
                        self.commit = n                                   # only current-term entries are counted directly
                        break
            else:
                self.next_index[src] = max(1, self.next_index[src] - 1)  # back up and retry

    def become_leader(self):
        self.state = "leader"
        self.elapsed = 0
        for p in self.cluster.peers(self.id):
            self.next_index[p], self.match_index[p] = len(self.log) + 1, 0
        self.broadcast_append()                                           # announce leadership immediately


class Cluster:
    def __init__(self, n=5, seed=0):
        self.n, self.rng, self.now = n, random.Random(seed), 0
        self.nodes = [Node(i, self) for i in range(n)]
        self.in_flight = []                                   # (deliver_at, order, src, dst, message)
        self.counter = 0
        self.groups = None                                    # None = fully connected; else a list of sets (a partition)
        self.leaders_by_term = {}                             # safety bookkeeping: term -> set of leaders seen

    def peers(self, nid):
        return [i for i in range(self.n) if i != nid]

    def connected(self, a, b):
        return self.groups is None or any(a in g and b in g for g in self.groups)

    def send(self, src, dst, msg):
        if self.connected(src, dst):
            self.counter += 1
            self.in_flight.append((self.now + self.rng.randint(1, 2), self.counter, src, dst, msg))

    def tick(self, times=1):
        for _ in range(times):
            self.now += 1
            due = sorted(m for m in self.in_flight if m[0] <= self.now)
            self.in_flight = [m for m in self.in_flight if m[0] > self.now]
            for _, _, src, dst, msg in due:
                self.nodes[dst].handle(src, msg)
            for node in self.nodes:
                node.tick()
                if node.alive and node.state == "leader":
                    self.leaders_by_term.setdefault(node.term, set()).add(node.id)

    def leader(self):
        leaders = [n for n in self.nodes if n.alive and n.state == "leader"]
        return max(leaders, key=lambda n: n.term) if leaders else None

    def submit(self, command):
        leader = self.leader()
        if leader is None:
            return False
        leader.log.append((leader.term, command))
        return True
```

(Simplifications: no persistence code (a crashed node just keeps its fields), no snapshots or membership changes, and the leader does not append a no-op on election. These are all in the full Raft paper.)

## 4. Experiment 1: elect a leader, replicate, survive a crash

```python
c = Cluster(5, seed=3)
c.tick(60)
L = c.leader()
print("leader:", L.id, "term", L.term, "| states:", [n.state[0] for n in c.nodes])
# leader: 3 term 1 | states: ['f', 'f', 'f', 'l', 'f']

for cmd in ["set x=1", "set y=2", "set x=3"]:
    c.submit(cmd)
c.tick(20)
print("commit index per node:", [n.commit for n in c.nodes], "| all logs identical:", len({tuple(n.log) for n in c.nodes}) == 1)
# commit index per node: [3, 3, 3, 3, 3] | all logs identical: True

old = L
old.alive = False                                   # crash the leader
c.tick(60)
L2 = c.leader()
print("new leader:", L2.id, "term", L2.term, "| contains every committed entry:", L2.log[:3] == old.log[:3])
# new leader: 1 term 2 | contains every committed entry: True

c.submit("set z=9")
c.tick(20)
print("commit among live nodes:", [n.commit for n in c.nodes if n.alive])
# commit among live nodes: [4, 4, 4, 4]

old.alive = True                                    # the old leader comes back
c.tick(30)
print("old leader is now:", old.state, "term", old.term, "| log length", len(old.log), "| commit", old.commit)
# old leader is now: follower term 2 | log length 4 | commit 4
print("all logs identical:", len({tuple(n.log) for n in c.nodes}) == 1)
# all logs identical: True
print("leaders seen per term:", c.leaders_by_term)
# leaders seen per term: {1: {3}, 2: {1}}
```

What happened: node 3 won term 1; the four live nodes elected node 1 in term 2 after the crash (a **majority of 5 is 3**, so 4 live nodes suffice); the new leader already had all three committed entries because only an up-to-date candidate can collect a majority of votes; the returning old leader saw the higher term, **stepped down**, and was brought up to date by the new leader. Exactly one leader per term.

## 5. Experiment 2: a network partition

```python
c = Cluster(5, seed=3)
c.tick(60)
leader = c.leader()
c.submit("a")
c.tick(15)

others = [i for i in range(5) if i != leader.id]
minority = {others[0], others[1]}                    # two nodes cut off from the other three
majority = set(range(5)) - minority
c.groups = [majority, minority]
c.tick(80)

print("leader on majority side:", c.leader().id in majority)
# leader on majority side: True
print("a minority node ever became leader:", any(i in minority for ids in c.leaders_by_term.values() for i in ids))
# a minority node ever became leader: False

c.submit("b")                                        # goes to the majority-side leader
c.tick(20)
print("commit index per node:", [n.commit for n in c.nodes])
# commit index per node: [1, 1, 2, 2, 2]

c.groups = None                                      # heal the partition
c.tick(60)
print("after healing:", [n.commit for n in c.nodes], "| logs identical:", len({tuple(n.log) for n in c.nodes}) == 1)
# after healing: [2, 2, 2, 2, 2] | logs identical: True
```

The two isolated nodes kept timing out and starting elections, but never got a majority (2 of 5), so they could not commit anything: **a minority cannot make progress, and cannot make wrong progress**. The majority side carried on and committed entry `b`. After healing the minority caught up. (Their inflated terms also forced a fresh election on healing; real implementations use a **pre-vote** phase to avoid such disruption.) This is the CAP trade-off in action: during the partition the minority side was **unavailable** to preserve consistency.

## 6. Testing safety with random failures

A distributed algorithm is only as good as its tests under bad luck. This harness runs hundreds of random scenarios (crashes, recoveries, partitions, heals, client commands) and checks two safety properties continuously:

1. **Election safety:** never two leaders in the same term.
2. **State-machine safety:** once any node commits an entry at an index, no node ever commits a different entry at that index.

```python
import random

def random_run(seed: int) -> bool:
    c = Cluster(5, seed=seed)
    rng = random.Random(seed * 7 + 1)
    committed = {}                                    # index -> entry, remembered forever
    for step in range(400):
        c.tick()
        if step % 25 == 0:                            # every 25 ticks, inject a random event
            r = rng.random()
            if r < 0.3:
                n = rng.choice(c.nodes)
                n.alive = not n.alive                 # crash or recover
                if n.alive:
                    n.elapsed = 0
            elif r < 0.5:
                ids = list(range(5)); rng.shuffle(ids)
                c.groups = [set(ids[:2]), set(ids[2:])]       # random partition
            elif r < 0.7:
                c.groups = None                               # heal
            else:
                c.submit(f"cmd{step}")
        for n in c.nodes:
            for i in range(1, n.commit + 1):
                entry = n.log[i - 1]
                if committed.setdefault(i, entry) != entry:
                    return False                      # two different committed entries at one index!
    return all(len(ids) <= 1 for ids in c.leaders_by_term.values())

violations = sum(not random_run(seed) for seed in range(200))
print("runs with a safety violation:", violations, "of 200")
# runs with a safety violation: 0 of 200
```

Zero violations across 200 hostile schedules is evidence, not proof (real Raft implementations are also checked with TLA+ models and tools such as Jepsen), but any bug in the rules above (for example, removing the up-to-date vote check) makes this harness fail quickly. Try breaking a rule yourself in practice question 5.

## 7. Where consensus is used (and when you need it)

- **Metadata and coordination:** etcd (Kubernetes), Consul, ZooKeeper: a small, strongly consistent store for configuration, leader election and locks.
- **Replicated databases:** CockroachDB, TiDB, Spanner and MongoDB replica sets use Raft or Paxos variants per shard.
- **Leader election for your own service:** do not implement Raft yourself; take a **lease** from etcd or ZooKeeper (a lock with an expiry) and use **fencing tokens** so a deposed leader's late writes are rejected.

You usually need consensus only for a **small amount of critical data**; bulk data uses cheaper replication. Cost: every write needs a majority round trip (latency) and throughput is bounded by the leader.

## 8. Common mistakes

- Running an **even** number of nodes (4 tolerates only 1 failure, the same as 3).
- Believing a leader can safely act alone after a pause: it may have been deposed while paused (a long GC pause or a stall); use leases with **fencing tokens**.
- Implementing your own consensus instead of using a tested library.
- Putting too much data through consensus (it is a bottleneck by design).
- Placing all nodes in one availability zone or one rack, so one failure takes a majority.
- Forgetting persistence: votes and logs must reach disk **before** replying, or a restart can double-vote.
- Mixing up replication with consensus: asynchronous replication can lose acknowledged writes; consensus does not.

## 9. Two real-world examples

**Example 1: The split brain that was not.** A team ran two database servers with a script that promoted the standby when the primary stopped answering. A network hiccup made both think the other was down; both accepted writes, and reconciling the data took days. A three-node etcd-backed election (a majority is required, so only one side can win) replaced the script.

**Example 2: Kubernetes' brain.** All cluster state lives in etcd, a Raft group of 3 or 5 nodes. When one control-plane machine is lost, the cluster keeps working because a majority remains; if two of three are lost, the API stops accepting changes (the cluster keeps running existing workloads, but cannot change), which is safety chosen over availability.

## 10. Practice

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

## 11. Check yourself

1. What are agreement, validity and termination?
2. What does the FLP result say, and how do real algorithms respond?
3. What is a term, and why does a higher term always win?
4. List the steps of a Raft election.
5. When is a log entry committed?
6. Why can a minority partition not make progress, and why is that desirable?
7. Why do clusters use an odd number of nodes?

<details>
<summary>Answers</summary>

1. Agreement: no two nodes decide differently; validity: the decided value was proposed by some node; termination: a decision is eventually reached.
2. In a fully asynchronous system with even one crash, no deterministic algorithm can always terminate. Real algorithms keep safety always and give up liveness during bad network periods (using timeouts and randomisation to make progress likely).
3. A term is a numbered epoch with at most one leader; a node seeing a higher term knows its information is stale and steps down.
4. A follower times out, increments its term, becomes a candidate, votes for itself, requests votes; nodes grant one vote per term to an up-to-date candidate; a majority makes it leader, which sends heartbeats.
5. When the leader has stored it on a majority of nodes (and, directly, for an entry of its own term); it then applies it and followers learn the commit index.
6. It cannot gather a majority of votes or acknowledgements, so it cannot elect a leader or commit; this prevents two sides of a partition from making conflicting decisions (split brain).
7. An even size adds a node without adding fault tolerance (4 nodes tolerate 1 failure, like 3) while making a split into two equal halves, neither with a majority, possible.

</details>

[Back to Distributed Systems](../README.md)
