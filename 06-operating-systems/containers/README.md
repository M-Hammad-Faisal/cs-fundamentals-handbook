# Containers

A container is an ordinary process with a restricted view (namespaces) and restricted resources (cgroups), started from a layered image.

## Detailed lesson

- [Containers, namespaces and cgroups](01-containers-and-namespaces.md): namespaces, cgroups, real resource-limit experiments, a jail model, copy-on-write image layers with content addressing, Dockerfile and Docker commands, security

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Question | Answer |
|----------|--------|
| What isolates what a process *sees*? | namespaces (PID, NET, MNT, UTS, IPC, USER) |
| What limits what it *uses*? | cgroups (memory, CPU, pids, I/O) |
| Exit code 137? | killed by `SIGKILL`, usually the OOM killer |
| Where does data go when a container is removed? | the writable layer is discarded: use volumes |
| Container vs VM? | shared kernel and fast start, versus its own kernel behind a hypervisor |

Back to [operating systems](../README.md).
