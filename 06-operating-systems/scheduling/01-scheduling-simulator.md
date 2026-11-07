# CPU Scheduling Algorithms: A Hands-On Simulator

**Prerequisites:** [what is an OS](../00-what-is-an-operating-system.md), [processes and threads](../processes-threads/README.md), [queues](../../02-data-structures/stacks-queues/02-queues-deques-priority-queues.md), [heaps](../../02-data-structures/heaps/01-binary-heaps-and-heapsort.md) (helpful). **You will learn:** why the OS needs a scheduler, the metrics used to judge one (**waiting, turnaround, response time, throughput**), and how **FCFS, SJF, SRTF, Round Robin and Priority** scheduling behave, by building and running a simulator you can experiment with; plus **starvation and aging**, **multilevel feedback queues**, and how Linux's **CFS** thinks.

## 1. In plain words

You have **one CPU core** and several programs ready to run. Only one can run at any instant, so the OS decides **who runs next and for how long**. That decision-maker is the **scheduler**. Switching quickly between programs creates the illusion that everything runs at once (**time-sharing**).

Analogy: one cashier, several customers with baskets of different sizes. Do you serve in arrival order? The smallest basket first? Give each customer 30 seconds and rotate? Each rule has winners and losers.

## 2. Vocabulary and metrics

| Term | Meaning |
|------|---------|
| **Arrival time** | when the process becomes ready |
| **Burst time** | CPU time it needs in total |
| **Preemptive** | the OS may interrupt a running process; **non-preemptive**: it runs until it finishes or blocks |
| **Context switch** | saving one process's state and loading another's (pure overhead) |
| **Quantum (time slice)** | the maximum run time before preemption in time-sharing |

Metrics (smaller is better unless noted):

- **Turnaround time** = finish time - arrival time (total time in the system).
- **Waiting time** = turnaround - burst (time spent ready but not running).
- **Response time** = first time on the CPU - arrival (how soon the user sees *something*).
- **Throughput** = jobs finished per unit time (larger is better).
- **CPU utilization** = fraction of time the CPU is busy.

## 3. The simulator

Each process is `(name, arrival, burst, priority)` (smaller priority number means more important). Every algorithm returns the **Gantt chart** (who ran when), per-process metrics and the averages.

```python
from collections import deque
import heapq

def metrics(procs, finish, first_run):
    rows = {}
    for name, arrival, burst, *_ in procs:
        turnaround = finish[name] - arrival
        rows[name] = {"finish": finish[name], "turnaround": turnaround,
                      "waiting": turnaround - burst, "response": first_run[name] - arrival}
    n = len(rows)
    avg = lambda key: round(sum(r[key] for r in rows.values()) / n, 2)
    return rows, {k: avg(k) for k in ("waiting", "turnaround", "response")}

def fcfs(procs):
    time, finish, first, gantt = 0, {}, {}, []
    for name, arrival, burst, *_ in sorted(procs, key=lambda p: p[1]):
        time = max(time, arrival)
        first[name] = time
        gantt.append((name, time, time + burst))
        time += burst
        finish[name] = time
    return gantt, *metrics(procs, finish, first)

def sjf(procs):                                   # non-preemptive shortest job first
    remaining, time, finish, first, gantt = sorted(procs, key=lambda p: p[1]), 0, {}, {}, []
    while remaining:
        ready = [p for p in remaining if p[1] <= time]
        if not ready:
            time = remaining[0][1]; continue
        job = min(ready, key=lambda p: (p[2], p[1]))
        remaining.remove(job)
        name, arrival, burst, *_ = job
        first[name] = time
        gantt.append((name, time, time + burst)); time += burst; finish[name] = time
    return gantt, *metrics(procs, finish, first)

def srtf(procs):                                  # preemptive shortest remaining time first
    left = {p[0]: p[2] for p in procs}
    arrivals = sorted(procs, key=lambda p: p[1])
    time, finish, first, gantt, i = 0, {}, {}, [], 0
    while len(finish) < len(procs):
        ready = [p for p in procs if p[1] <= time and left[p[0]] > 0]
        if not ready:
            time = min(p[1] for p in procs if left[p[0]] > 0); continue
        name = min(ready, key=lambda p: (left[p[0]], p[1]))[0]
        first.setdefault(name, time)
        if gantt and gantt[-1][0] == name and gantt[-1][2] == time:
            gantt[-1] = (name, gantt[-1][1], time + 1)
        else:
            gantt.append((name, time, time + 1))
        left[name] -= 1; time += 1
        if left[name] == 0:
            finish[name] = time
    return gantt, *metrics(procs, finish, first)

def round_robin(procs, quantum):
    left = {p[0]: p[2] for p in procs}
    pending = deque(sorted(procs, key=lambda p: p[1]))
    queue, time, finish, first, gantt = deque(), 0, {}, {}, []
    def admit():
        while pending and pending[0][1] <= time:
            queue.append(pending.popleft()[0])
    admit()
    while len(finish) < len(procs):
        if not queue:
            time = pending[0][1]; admit(); continue
        name = queue.popleft()
        first.setdefault(name, time)
        run = min(quantum, left[name])
        gantt.append((name, time, time + run)); time += run; left[name] -= run
        admit()                                    # newcomers that arrived during the slice queue BEFORE the preempted process
        if left[name] > 0:
            queue.append(name)
        else:
            finish[name] = time
    return gantt, *metrics(procs, finish, first)

def priority_np(procs):                           # non-preemptive, smaller number = more important
    remaining, time, finish, first, gantt = sorted(procs, key=lambda p: p[1]), 0, {}, {}, []
    while remaining:
        ready = [p for p in remaining if p[1] <= time]
        if not ready:
            time = remaining[0][1]; continue
        job = min(ready, key=lambda p: (p[3], p[1]))
        remaining.remove(job)
        name, arrival, burst, prio = job
        first[name] = time
        gantt.append((name, time, time + burst)); time += burst; finish[name] = time
    return gantt, *metrics(procs, finish, first)
```

A helper to draw the Gantt chart as text:

```python
def draw(gantt):
    line, marks = "", ""
    for name, start, end in gantt:
        width = max(len(name) + 2, 4)
        line += name.center(width, " ")[:width] + "|"
        marks += str(start).ljust(width + 1)
    return "|" + line + "\n" + marks + str(gantt[-1][2])

procs = [("P1", 0, 8, 3), ("P2", 1, 4, 1), ("P3", 2, 9, 4), ("P4", 3, 5, 2)]
```

## 4. First-Come First-Served (FCFS)

Run in arrival order, to completion. Simple and fair in the "queue at a shop" sense.

```python
gantt, rows, avg = fcfs(procs)
print(draw(gantt))
print({name: r["waiting"] for name, r in rows.items()}, avg)
# | P1 | P2 | P3 | P4 |
# 0    8    12   21   26
# {'P1': 0, 'P2': 7, 'P3': 10, 'P4': 18} {'waiting': 8.75, 'turnaround': 15.25, 'response': 8.75}
```

**The convoy effect:** one long job at the front makes many short jobs wait behind it, like a single huge shopping cart blocking the express lane.

```python
convoy = [("long", 0, 100, 1), ("a", 1, 2, 1), ("b", 2, 2, 1), ("c", 3, 2, 1)]
print(fcfs(convoy)[2])           # {'waiting': 75.0, 'turnaround': 101.5, 'response': 75.0}
print(sjf(convoy)[2])            # {'waiting': 75.0, 'turnaround': 101.5, 'response': 75.0}   (the long job was already running)
print(srtf(convoy)[2])           # {'waiting': 2.25, 'turnaround': 28.75, 'response': 0.75}
```

(Preemption rescues the short jobs: they cut in front of the long one, so average waiting drops from 75 to 2.25 time units.)

## 5. Shortest Job First (SJF) and Shortest Remaining Time First (SRTF)

**SJF:** among the ready jobs, run the one with the **smallest burst**. It provably gives the **minimum average waiting time** among non-preemptive algorithms. **SRTF** is the preemptive version: whenever a new job arrives with less time left than the running one, switch.

```python
for label, fn in (("SJF", sjf), ("SRTF", srtf)):
    gantt, rows, avg = fn(procs)
    print(label, [(n, s, e) for n, s, e in gantt])
    print("   ", avg)
# SJF  [('P1', 0, 8), ('P2', 8, 12), ('P4', 12, 17), ('P3', 17, 26)]
#     {'waiting': 7.75, 'turnaround': 14.25, 'response': 7.75}
# SRTF [('P1', 0, 1), ('P2', 1, 5), ('P4', 5, 10), ('P1', 10, 17), ('P3', 17, 26)]
#     {'waiting': 6.5, 'turnaround': 13.0, 'response': 4.25}
```

SRTF beats both on waiting time here. The catch: **you cannot know the burst time in advance**. Real systems **predict** it from history (exponential averaging: `next_estimate = a * last_burst + (1 - a) * old_estimate`). SJF also **starves** long jobs if short ones keep arriving.

## 6. Round Robin (RR)

Give each process a **quantum**; if it is not finished, put it at the back of the ready queue. This is the model behind interactive time-sharing.

```python
gantt, rows, avg = round_robin(procs, 4)
print([(n, s, e) for n, s, e in gantt])
print(avg)
# [('P1', 0, 4), ('P2', 4, 8), ('P3', 8, 12), ('P4', 12, 16), ('P1', 16, 20), ('P3', 20, 24), ('P4', 24, 25), ('P3', 25, 26)]
# {'waiting': 11.75, 'turnaround': 18.25, 'response': 4.5}
```

Round Robin has a worse average **waiting** time but a good **response** time and fairness: nobody waits long to start. The quantum matters:

- **Quantum too large:** RR degenerates into FCFS (long waits for response).
- **Quantum too small:** most time goes into context switches (overhead).
- Typical values are 10-100 ms, chosen so that most interactive bursts finish within one quantum.

```python
for q in (1, 2, 4, 8, 100):
    gantt, rows, avg = round_robin(procs, q)
    switches = len(gantt) - 1
    print(f"quantum={q:3}  context switches={switches:2}  avg waiting={avg['waiting']:5}  avg response={avg['response']}")
# quantum=  1  context switches=25  avg waiting= 12.5  avg response=0.75
# quantum=  2  context switches=13  avg waiting=12.75  avg response=2.0
# quantum=  4  context switches= 7  avg waiting=11.75  avg response=4.5
# quantum=  8  context switches= 4  avg waiting= 9.75  avg response=8.5
# quantum=100  context switches= 3  avg waiting= 8.75  avg response=8.75
```

As the quantum shrinks, response time improves (0.75 at `q=1`) but switches multiply (25 versus 3); at a huge quantum RR becomes identical to FCFS (the last row equals FCFS's 8.75 / 8.75).

## 7. Priority scheduling, starvation and aging

Each process has a priority; the highest-priority ready process runs. (Smaller number means more important in our simulator; some systems do the opposite.) Priority can be **preemptive** or not.

```python
gantt, rows, avg = priority_np(procs)
print([n for n, s, e in gantt], avg)
# ['P1', 'P2', 'P4', 'P3'] {'waiting': 7.75, 'turnaround': 14.25, 'response': 7.75}
```

**Starvation:** a low-priority process may never run if higher-priority work keeps arriving. **Aging** is the cure: gradually raise the priority of processes that have waited a long time.

```python
def priority_with_aging(procs, age_step=1):
    """Every `age_step` time units a process has waited improves its priority number by 1 (lower is better)."""
    remaining, time, order = [list(p) for p in procs], 0, []
    while remaining:
        ready = [p for p in remaining if p[1] <= time]
        if not ready:
            time = min(p[1] for p in remaining); continue
        def effective(p):
            return p[3] - (time - p[1]) // age_step
        job = min(ready, key=lambda p: (effective(p), p[1]))
        remaining.remove(job)
        order.append((job[0], time))
        time += job[2]
    return order

# A low-priority job (9) arrives just after a stream of important short jobs (priority 1) has started.
stream = [("hi0", 0, 3, 1), ("low", 1, 3, 9)] + [(f"hi{i}", i * 3, 3, 1) for i in range(1, 9)]
print([n for n, *_ in priority_np(stream)[0]])
# ['hi0', 'hi1', 'hi2', 'hi3', 'hi4', 'hi5', 'hi6', 'hi7', 'hi8', 'low']      (starved: runs after all nine)
print([n for n, t in priority_with_aging(stream)])
# ['hi0', 'hi1', 'hi2', 'low', 'hi3', 'hi4', 'hi5', 'hi6', 'hi7', 'hi8']      (aging lets it in after three)
```

## 8. Multilevel feedback queue (MLFQ): what real systems use

You rarely know burst times, so MLFQ **learns** from behavior:

- Several queues with different priorities (and quanta).
- New processes start at the **top queue**.
- A process that uses its **whole quantum** is probably CPU-bound: **demote** it to a lower queue.
- A process that gives up the CPU early (waits for I/O: interactive) **stays high**.
- Periodically **boost** everyone back to the top (prevents starvation).

Result: short interactive jobs (typing, clicking) stay responsive while long number-crunching jobs sink to the background, without anyone telling the OS which is which. Variants are used by classic Unix, Windows and macOS schedulers.

```python
def mlfq(procs, quanta=(2, 4, 8)):
    """Three queues; CPU-bound processes sink. Returns the order of (name, queue_level, run_length) slices."""
    left = {p[0]: p[2] for p in procs}
    queues = [deque() for _ in quanta]
    for p in sorted(procs, key=lambda p: p[1]):
        queues[0].append(p[0])                        # simplification: everyone arrives at time 0
    slices = []
    while any(queues):
        level = next(i for i, q in enumerate(queues) if q)    # highest non-empty queue
        name = queues[level].popleft()
        run = min(quanta[level], left[name])
        left[name] -= run
        slices.append((name, level, run))
        if left[name] > 0:
            queues[min(level + 1, len(quanta) - 1)].append(name)       # used its full quantum: demote
    return slices

print(mlfq([("short", 0, 2, 0), ("medium", 0, 6, 0), ("long", 0, 14, 0)]))
# [('short', 0, 2), ('medium', 0, 2), ('long', 0, 2), ('medium', 1, 4), ('long', 1, 4), ('long', 2, 8)]
```

## 9. How Linux thinks: CFS (fair scheduling)

Linux's **Completely Fair Scheduler** replaces fixed quanta with a notion of **virtual runtime** (`vruntime`): how much CPU each task has had, weighted by its niceness. The scheduler always runs the task with the **smallest vruntime** (kept in a red-black tree, so picking it is `O(log n)`). Tasks that sleep a lot (interactive) have low vruntime when they wake and are picked quickly; CPU hogs accumulate vruntime and yield. (Newer Linux kernels refine this with the EEVDF algorithm, but the "everyone gets a fair share" idea is the same.)

```python
import heapq

def fair_share(tasks, rounds=12, slice_ms=10):
    """tasks: {name: weight}. Always run the task with the smallest virtual runtime; heavier weight = slower vruntime growth."""
    heap = [(0.0, name) for name in tasks]
    heapq.heapify(heap)
    cpu = {name: 0 for name in tasks}
    for _ in range(rounds):
        vruntime, name = heapq.heappop(heap)
        cpu[name] += slice_ms
        heapq.heappush(heap, (vruntime + slice_ms / tasks[name], name))
    return cpu

print(fair_share({"editor": 1, "compiler": 1, "video": 2}, rounds=40))     # {'editor': 100, 'compiler': 100, 'video': 200}
```

Task `video` has twice the weight, so it receives twice the CPU: fair-share scheduling in about ten lines. In Linux, `nice` values (-20 to +19) set these weights: `nice -n 10 command` makes a process a considerate neighbor.

## 10. Summary table

| Algorithm | Preemptive? | Strength | Weakness |
|-----------|-------------|----------|----------|
| FCFS | no | simple, no starvation | convoy effect, poor response |
| SJF | no | best average waiting (non-preemptive) | needs burst predictions; starves long jobs |
| SRTF | yes | best average waiting overall | same; more context switches |
| Round Robin | yes | good response, fair | worse waiting; quantum choice matters |
| Priority | either | models importance | starvation (fix: aging) |
| MLFQ | yes | adapts without knowing bursts | tuning complexity |
| CFS | yes | proportional fairness | not hard real-time |

**Real-time systems** (pacemakers, flight controllers) use deadline-based schedulers (**EDF**, earliest deadline first; **rate-monotonic**), where missing a deadline is a failure, not just slowness.

## 11. Two real-world examples

**Example 1: Your desktop stays responsive during a build.** The compiler runs many CPU-bound threads; the scheduler (MLFQ or CFS style) lets the short bursts of your mouse and keyboard handling jump ahead, so the UI remains smooth.

**Example 2: Web servers and thread pools.** A server with 4 cores and 400 worker threads relies on the OS scheduler to time-slice them; if each request is short, response time stays good, but if all 400 are CPU-bound each gets 1% of a core and latency explodes, which is why CPU-heavy services size their pools near the core count.

## 12. Common mistakes

- Confusing waiting time (ready but not running) with turnaround time (total) or response time (until first run).
- Forgetting that burst times are unknown in practice, so "SJF is optimal" is theoretical.
- Ignoring context-switch cost when choosing a tiny quantum.
- Ordering ties inconsistently in Round Robin (state your rule about newcomers versus the preempted process).
- Assuming more threads than cores means more speed for CPU-bound work.
- Setting a priority scheme without aging.

## 13. Practice

1. Compute FCFS average waiting time by hand for `P1(0,5)`, `P2(1,3)`, `P3(2,8)`.
2. Do the same for SJF and SRTF with those processes.
3. Why does SJF minimize average waiting time? (Hint: where should the short jobs go?)
4. For Round Robin with quantum 2 on `A(0,5)`, `B(0,3)`, write the Gantt chart.
5. A process with a huge burst arrives with a stream of tiny jobs. Which algorithms starve it?
6. Add a `sjf_with_prediction` that predicts burst times with exponential averaging. (Describe the update rule only.)
7. Why do interactive systems prefer response time over average waiting time?

<details>
<summary>Solutions</summary>

1. FCFS: `P1` starts at 0 (wait 0), `P2` starts at 5 (arrived 1: wait 4), `P3` starts at 8 (arrived 2: wait 6): average `(0 + 4 + 6) / 3 = 3.33`.
   ```python
   small = [("P1", 0, 5, 1), ("P2", 1, 3, 1), ("P3", 2, 8, 1)]
   print(fcfs(small)[2]["waiting"])                        # 3.33
   ```
2. SJF: after `P1` (0-5), pick `P2` (burst 3) then `P3`: same order as FCFS here, so 3.33. SRTF: `P1` has 4 left when `P2` (3) arrives, so `P2` preempts at 1.
   ```python
   print(sjf(small)[2]["waiting"], srtf(small)[2]["waiting"])      # 3.33 3.0
   ```
3. Every job's burst delays all jobs behind it; putting short jobs first means short delays are counted many times and long delays few times.
4. `A` 0-2, `B` 2-4, `A` 4-6, `B` 6-7, `A` 7-8.
   ```python
   print([(n, s, e) for n, s, e in round_robin([("A", 0, 5, 1), ("B", 0, 3, 1)], 2)[0]])
   # [('A', 0, 2), ('B', 2, 4), ('A', 4, 6), ('B', 6, 7), ('A', 7, 8)]
   ```
5. SJF and SRTF (always a shorter job available) and any priority scheme without aging. FCFS and Round Robin do not starve it.
6. `estimate = alpha * last_actual_burst + (1 - alpha) * previous_estimate`, usually `alpha = 0.5`; run the process with the smallest estimate.
7. Users notice delay before the first reaction, not the total time to finish a long job; fast acknowledgement feels responsive.

</details>

## 14. Check yourself

1. Define turnaround, waiting and response time.
2. What is the convoy effect?
3. Why can SJF not be implemented exactly?
4. What trade-off does the Round Robin quantum control?
5. What problem does aging solve?
6. How does MLFQ identify interactive processes?

<details>
<summary>Answers</summary>

1. Turnaround = finish - arrival; waiting = turnaround - burst; response = first run - arrival.
2. Short jobs stuck behind a long job in a non-preemptive FCFS queue.
3. Burst length is not known in advance; only predictions are possible.
4. Response time and fairness (small quantum) versus context-switch overhead (large quantum is efficient but sluggish).
5. Starvation of low-priority processes (their priority rises the longer they wait).
6. They give up the CPU before their quantum ends (they wait for I/O), so they stay in high-priority queues.

</details>

[Back to scheduling](README.md)
