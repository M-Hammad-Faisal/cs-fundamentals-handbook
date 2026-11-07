# CPU Scheduling: One-Page Summary

- **Metrics:** waiting = time in ready queue; turnaround = finish - arrival; response = first run - arrival; throughput; utilization.
- **FCFS:** simple; convoy effect. **SJF:** optimal average wait, needs burst estimates, starves long jobs. **SRTF:** preemptive SJF. **RR:** quantum `q`; small = overhead, large = FCFS. **Priority:** starvation, fix with aging. **MLFQ:** adapts by demoting CPU hogs.
- **Example:** jobs 24, 3, 3 at time 0: FCFS avg wait 17, SJF 3, RR(q=4) 5.67.
- **Linux:** fair-share by virtual runtime (CFS/EEVDF), `nice` weights, real-time classes, per-CPU queues, affinity.
- **Priority inversion** is fixed by priority inheritance.
- **Containers:** CPU limits throttle per period, causing latency spikes.

[Lesson](README.md) · [Exercises](exercises.md)
