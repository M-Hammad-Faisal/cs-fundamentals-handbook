# CPU Scheduling

## Detailed lesson (start here if you are new)

- [CPU scheduling hands-on simulator](01-scheduling-simulator.md): metrics, FCFS/SJF/SRTF/RR/priority, aging, MLFQ, CFS, with runnable code

The rest of this page is the quick reference.

## 1. The concept

The **scheduler** decides which ready process or thread gets the CPU next, and for how long. With more runnable tasks than cores, this choice determines responsiveness, throughput and fairness.

Terms (for a job with arrival time `a`, burst time `b`, finishing at `f`):
- **Turnaround time** = `f - a`
- **Waiting time** = turnaround - `b` (time spent in the ready queue)
- **Response time** = first run - `a`
- **Throughput** = jobs finished per unit time; **CPU utilization** = fraction of time busy

**Preemptive** schedulers can take the CPU away (timer interrupt); **non-preemptive** ones wait until the task blocks or ends. Modern general-purpose OSes are preemptive.

## 2. The classic algorithms

| Algorithm | Rule | Pros | Cons |
|-----------|------|------|------|
| **FCFS** | First come, first served | Simple, no starvation | **Convoy effect**: short jobs queue behind a long one |
| **SJF** | Shortest burst first | Minimal average waiting time (provably optimal) | Needs burst estimates; starves long jobs |
| **SRTF** | Preemptive SJF (shortest *remaining* time) | Even lower waits | Same starvation, more switches |
| **Round Robin** | Each task gets a time quantum `q`, then goes to the back | Fair, good response time | Quantum too small: switch overhead; too large: behaves like FCFS |
| **Priority** | Highest priority first | Models importance | Starvation; fix with **aging** (raise priority while waiting) |
| **MLFQ** | Several queues; new tasks start high, CPU hogs sink, I/O-bound tasks stay high | Adapts without knowing bursts | Tuning; gaming risk |
| **CFS-style fair share** | Run the task with the least virtual runtime | Fairness by weight | Needs a balanced tree; latency tuning |

### A simulator you can run

```python
from collections import deque

def fcfs(procs):                       # procs: (name, arrival, burst)
    t, wait = 0, {}
    for name, arr, burst in sorted(procs, key=lambda p: p[1]):
        t = max(t, arr)
        wait[name] = t - arr
        t += burst
    return wait

def sjf(procs):                        # non-preemptive shortest job first
    todo, t, wait = list(procs), 0, {}
    while todo:
        ready = [p for p in todo if p[1] <= t] or [min(todo, key=lambda p: p[1])]
        p = min(ready, key=lambda p: p[2])
        t = max(t, p[1])
        wait[p[0]] = t - p[1]
        t += p[2]
        todo.remove(p)
    return wait

def srtf(procs):                       # preemptive SJF
    rem = {n: b for n, a, b in procs}
    arr = {n: a for n, a, b in procs}
    t, finish = 0, {}
    while rem:
        ready = [n for n in rem if arr[n] <= t]
        if not ready:
            t += 1; continue
        n = min(ready, key=lambda n: rem[n])
        rem[n] -= 1; t += 1
        if rem[n] == 0:
            del rem[n]; finish[n] = t
    burst = {n: b for n, a, b in procs}
    return {n: finish[n] - arr[n] - burst[n] for n in finish}

def round_robin(procs, q):
    procs = sorted(procs, key=lambda p: p[1])
    rem = {n: b for n, a, b in procs}
    arr = {n: a for n, a, b in procs}
    queue, t, i, finish = deque(), 0, 0, {}
    while len(finish) < len(procs):
        while i < len(procs) and procs[i][1] <= t:
            queue.append(procs[i][0]); i += 1
        if not queue:
            t = procs[i][1]; continue
        n = queue.popleft()
        run = min(q, rem[n]); t += run; rem[n] -= run
        while i < len(procs) and procs[i][1] <= t:
            queue.append(procs[i][0]); i += 1
        if rem[n]: queue.append(n)
        else: finish[n] = t
    burst = {n: b for n, a, b in procs}
    return {n: finish[n] - arr[n] - burst[n] for n in finish}

def avg(w): return sum(w.values()) / len(w)
```

Run the classic convoy example (three jobs arrive at time 0):

```python
jobs = [("P1", 0, 24), ("P2", 0, 3), ("P3", 0, 3)]
print(avg(fcfs(jobs)))            # 17.0   (P1 first: the short jobs wait 24 and 27)
print(avg(sjf(jobs)))             # 3.0    (short jobs first)
print(avg(round_robin(jobs, 4)))  # 5.666...
```

A second workload with staggered arrivals: `[("A",0,8),("B",1,4),("C",2,9),("D",3,5)]` gives average waits of 8.75 (FCFS), 7.75 (SJF), 6.5 (SRTF) and 13.5 (Round Robin, `q=3`). RR has the *worst* average waiting time here because it trades it for fairness and fast first responses.

## 3. How real schedulers work

- **Linux CFS/EEVDF**: tracks how much CPU each task has had (virtual runtime, weighted by `nice`) and picks the one that is furthest behind. `nice` values (-20 to 19) change the weight, not a strict priority.
- **Real-time classes** (`SCHED_FIFO`, `SCHED_RR`) always preempt normal tasks and are for deadlines (audio, control loops).
- **Multicore:** per-CPU run queues, **load balancing** and **CPU affinity** (keeping a task on one core keeps its cache warm).
- **I/O-bound vs CPU-bound:** tasks that often block get boosted so interactive apps stay responsive.
- **Priority inversion:** a high-priority task waits for a lock held by a low-priority one that a medium task keeps preempting. Fix: **priority inheritance** (the 1997 Mars Pathfinder reset bug was exactly this).

## 4. Two real-world examples

### Example 1: Keeping a laptop responsive during a build
A compile job (CPU-bound) and a text editor (I/O-bound: it mostly waits for keystrokes) share the CPU. The scheduler sees the editor sleep a lot, so when a key arrives it runs promptly, ahead of the compiler. Running the build under `nice -n 10` tells the scheduler it is less important still.

### Example 2: Kubernetes CPU limits
A container with a CPU limit of `500m` is throttled by the kernel's bandwidth control: it may use 50 ms of CPU per 100 ms period, then waits for the next period even if cores are idle. Latency spikes in tight limits are scheduling effects, not slow code.

## 5. Tips, tricks and pitfalls

- Optimizing average waiting time (SJF) and fairness (RR) conflict; pick the metric that matches the product.
- Starvation needs a deliberate fix (aging); do not assume priority means eventual service.
- A larger time quantum improves throughput but hurts interactivity.
- Measure context switches (`vmstat`, `pidstat -w`) before blaming the scheduler.
- Too many threads add switching overhead without more parallelism: size pools by core count and workload type.

## 6. Check yourself

1. Define waiting, turnaround and response time.
2. What is the convoy effect and which algorithm suffers from it?
3. Why is SJF optimal for average waiting time but impractical?
4. How does the Round Robin quantum affect behavior?
5. What is starvation and how does aging fix it?
6. What is priority inversion and how is it solved?

<details>
<summary>Answers</summary>

1. Waiting = time in the ready queue; turnaround = finish minus arrival; response = first run minus arrival.
2. Short jobs stuck behind one long job; FCFS.
3. Running the shortest jobs first minimizes the total time other jobs wait. The OS cannot know burst lengths ahead of time (only estimate them, for example by exponential averaging of previous bursts), and long jobs may starve.
4. Tiny `q`: fair and responsive but dominated by context-switch overhead. Huge `q`: degenerates into FCFS.
5. Starvation is a task never getting the CPU because others always outrank it. Aging gradually raises the priority of waiting tasks.
6. A high-priority task blocked on a lock held by a low-priority task that is preempted by medium tasks. Priority inheritance temporarily raises the lock holder's priority.

</details>

[Exercises](exercises.md) · [Summary](summary.md)
