# CPU Scheduling: Exercises

Use `fcfs`, `sjf`, `srtf`, `round_robin` and `avg` from the lesson.

1. Compute by hand the average waiting time for FCFS and SJF on `P1(0,6) P2(0,8) P3(0,7) P4(0,3)` (arrival, burst). Verify with the simulator.
2. Run Round Robin with `q = 1, 2, 4, 100` on `[("A",0,5),("B",0,3),("C",0,8)]`. What happens as `q` grows?
3. Give a workload where SRTF is strictly better than non-preemptive SJF.
4. Explain why a CPU-bound task and an I/O-bound task sharing a CPU should favor the I/O-bound one.
5. Add **turnaround time** and **response time** to the simulator for Round Robin.
6. Describe how aging prevents starvation in a priority scheduler, with a small numeric example.
7. A service has `500m` CPU limit and a request needing 80 ms of CPU. Estimate its latency when it arrives at the start of a period versus mid-throttle.

<details>
<summary>Solutions</summary>

**1.** FCFS order P1,P2,P3,P4 gives waits 0, 6, 14, 21: average 10.25. SJF order P4,P1,P3,P2 gives waits 0, 3, 9, 16: average 7.0.

**2.** As `q` grows the waiting times converge to FCFS (with `q=100` it is exactly FCFS: waits 0, 5, 8, average 4.33); `q=1` interleaves tightly (best response, most switches).
```python
jobs = [("A",0,5),("B",0,3),("C",0,8)]
for q in (1, 2, 4, 100):
    print(q, round(avg(round_robin(jobs, q)), 2))
```

**3.** `A(0,8)`, `B(1,4)`: non-preemptive SJF runs A to completion, so B waits 7 (average wait (0+7)/2 = 3.5). SRTF preempts at time 1 because B's 4 is less than A's remaining 7: B waits 0 and A waits 4 (average 2.0).

**4.** The I/O-bound task uses the CPU in short bursts and then blocks; running it immediately keeps the devices and the user busy, and it barely delays the CPU-bound task. Doing the reverse leaves devices idle (poor utilization) and the UI laggy.

**5.** Record each job's first-run time and finish time: turnaround = finish - arrival; response = first_run - arrival. Add `first = {}` and set `first.setdefault(n, t)` just before `t += run`.

**6.** Each time a task waits a full period, add 1 to its priority. A priority-1 task waiting against a stream of priority-5 tasks reaches priority 5 after 4 periods and then runs. Without aging it would never run.

**7.** The limit gives 50 ms of CPU per 100 ms period. The request needs 80 ms: it runs 50 ms, is throttled for the remaining 50 ms of the period, then runs 30 ms in the next period: latency roughly 130 ms instead of 80 ms. If the quota was already spent, it also waits for the next period first.

</details>

[Lesson](README.md) · [Summary](summary.md)
