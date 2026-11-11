# Containers: One-Page Summary

- A **container** is an ordinary process (tree) with a restricted view and restricted resources, started from a layered image. It shares the host kernel, so it starts in milliseconds.
- **Namespaces** limit what it **sees**: PID (processes), NET (network), MNT (mounts), UTS (hostname), IPC, USER (user ids).
- **cgroups** limit what it **uses**: memory, CPU, process count, I/O. Over the memory limit: the process is killed (exit code 137, `OOMKilled`).
- **Images:** a stack of read-only layers addressed by the hash of their content (identical layers are stored once) plus a thin writable layer per container (copy-on-write). Removing the container discards that layer: persist data with **volumes**.
- **Dockerfile:** `FROM` base, `COPY`/`RUN`/`ADD` create layers, `ENV`/`CMD`/`ENTRYPOINT` set metadata. Order for the cache: rarely changing steps first (dependencies), changing steps last (source code).
- **Everyday commands:** `docker build -t name .`, `docker run --rm -p 8080:80 name`, `docker ps`, `docker logs`, `docker exec -it id sh`, `docker stop`.
- **Security:** a container is **not** a VM-grade boundary. Run as non-root, drop capabilities, read-only root filesystem, pin and scan base images, never bake secrets into layers, keep the host kernel patched.
- **Container versus VM:** shared kernel and fast start versus own kernel behind a hypervisor and stronger isolation.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Containers, Namespaces and cgroups](01-containers-and-namespaces.md)
