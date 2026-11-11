# Containers: Exercises

These problems go with the [Containers lesson](README.md). Try each one before opening its solution.

The code parts need only the standard library; the namespace experiments need Linux (or a Linux container) and are described in words.

## Problems

1. **Exit codes.** A container exits with code 137, another with 143, another with 0. Say what each means, and compute the signal name for `137 - 128` in Python.
2. **Parse cgroup limits.** A cgroup v2 `memory.max` file contains either the word `max` or a number of bytes; `cpu.max` contains `"<quota> <period>"` in microseconds. Write `describe_memory(text)` and `cpus_allowed(text)` returning human-readable results.
3. **Content addressing.** Layers are named by the SHA-256 of their bytes. Store three layers (two identical) in a dictionary keyed by digest and show that identical content is stored once.
4. **Which Dockerfile lines create layers?** Write `count_layers(dockerfile_text)` that counts the instructions that add a filesystem layer (`RUN`, `COPY`, `ADD`).
5. **Cache invalidation.** Given the lines of a Dockerfile and the name of a changed instruction, write `rebuilt(lines, changed_index)` returning which lines must be rebuilt. Why should dependency installation come before copying the source code?
6. **Review a Dockerfile.** List at least five problems in: `FROM ubuntu:latest` / `RUN apt-get update && apt-get install -y python3 curl` / `COPY . /app` / `ENV API_KEY=abc123` / `CMD python3 /app/main.py` (run as root).
7. **Namespaces and cgroups.** For each of "container cannot see other processes", "container is limited to 256 MB", "container has its own hostname", "container cannot use more than half a CPU", say whether it is a namespace or a cgroup feature, and which one.
8. **Container or virtual machine?** Give two situations where you would choose a VM over a container for isolation, and two where a container is better.
9. **Data.** You run a database in a container and remove the container: where did the data go? Name two ways to keep it.

<details>
<summary>Solutions</summary>

**1.**
```python
import signal
print(137 - 128, signal.Signals(137 - 128).name, signal.Signals(143 - 128).name)
# 9 SIGKILL SIGTERM
```
`137` = killed by `SIGKILL` (9), most often the out-of-memory killer or `docker kill`; `143` = terminated by `SIGTERM` (15), a normal graceful stop (`docker stop`); `0` = the main process finished successfully. Exit codes above 128 mean "killed by signal (code minus 128)".

**2.**
```python
def describe_memory(text):
    text = text.strip()
    if text == "max":
        return "no memory limit"
    n = int(text)
    return f"{n / 2**20:.0f} MiB limit"

def cpus_allowed(text):
    quota, period = text.split()
    return None if quota == "max" else int(quota) / int(period)

print(describe_memory("268435456"), "|", describe_memory("max"), "|", cpus_allowed("50000 100000"), cpus_allowed("200000 100000"), cpus_allowed("max 100000"))
# 256 MiB limit | no memory limit | 0.5 2.0 None
```

**3.**
```python
import hashlib

store = {}
for layer in [b"base os files", b"python runtime", b"base os files"]:
    store.setdefault(hashlib.sha256(layer).hexdigest()[:12], layer)
print(len(store), "distinct layers stored for 3 uploaded")
# 2 distinct layers stored for 3 uploaded
```
Two images that share a base layer store and download it once.

**4.**
```python
def count_layers(dockerfile_text):
    instructions = [line.split()[0].upper() for line in dockerfile_text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    return sum(1 for i in instructions if i in {"RUN", "COPY", "ADD"})

print(count_layers("FROM python:3.13-slim\n# comment\nWORKDIR /app\nCOPY req.txt .\nRUN pip install -r req.txt\nCOPY . .\nCMD [\"python\", \"app.py\"]"))
# 3
```
`FROM` supplies the base image's layers; `WORKDIR`, `ENV`, `CMD` and `EXPOSE` only change metadata.

**5.**
```python
def rebuilt(lines, changed_index):
    return lines[changed_index:]                      # a changed instruction invalidates its own layer and EVERY later one

lines = ["FROM python:3.13-slim", "COPY requirements.txt .", "RUN pip install -r requirements.txt", "COPY . ."]
print(rebuilt(lines, 3))
print(rebuilt(lines, 1))
# ['COPY . .']
# ['COPY requirements.txt .', 'RUN pip install -r requirements.txt', 'COPY . .']
```
Source code changes constantly and dependencies rarely. Copying only `requirements.txt` first means editing code invalidates just the last layer; the slow `pip install` layer comes from the cache.

**6.** (1) `latest` tag is unpinned: builds are not reproducible. (2) Ubuntu is a large base; use a slim image. (3) `apt-get` without `--no-install-recommends` and without cleaning `/var/lib/apt/lists` bloats the image; the `update` and `install` are right to share one `RUN`. (4) `COPY . /app` copies everything including `.git` and `.env` unless a `.dockerignore` excludes them, and defeats layer caching. (5) `ENV API_KEY=abc123` bakes a secret into the image and its metadata; pass secrets at run time. (6) Runs as root; add a non-root `USER`. (7) Shell-form `CMD` runs through a shell so signals may not reach the app; use the exec form `CMD ["python3", "/app/main.py"]`. (8) No dependency pinning or health check.

**7.** Cannot see other processes: **namespace** (PID). Limited to 256 MB: **cgroup** (memory). Own hostname: **namespace** (UTS). At most half a CPU: **cgroup** (CPU quota). Namespaces change what a process *sees*; cgroups limit what it can *use*.

**8.** VM: running untrusted code from unknown customers (a stronger boundary: separate kernel behind a hypervisor); needing a different operating system or kernel version. Container: fast start and high density for many small services of the same OS; reproducible developer and CI environments.

**9.** A container's writable layer is discarded when the container is removed, so the data is gone. Keep it with a **volume** (`-v dbdata:/var/lib/postgresql/data`) or a **bind mount** of a host directory (or a managed database outside the container).

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Containers, Namespaces and cgroups](01-containers-and-namespaces.md)
