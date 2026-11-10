# Containers, Namespaces and cgroups

**Prerequisites:** [processes in practice](../processes-threads/01-processes-in-practice.md), [what is an OS](../00-what-is-an-operating-system.md) (kernel, system calls), [file systems](../file-systems-io/01-file-systems-in-depth.md), [boot process](../boot-and-startup/01-boot-process-and-bootloaders.md). **You will learn:** what a **container** really is (an ordinary process with a restricted *view* and restricted *resources*, not a tiny virtual machine); the two Linux features that build it, **namespaces** (what a process can *see*) and **cgroups** (what it can *use*); how **images and layers** work (copy-on-write, content-addressed digests); how containers differ from **virtual machines**; the **security** model and its limits; and the commands you will use (**Docker**, `unshare`). Parts that need Linux are shown as reference commands; everything else runs as **models and real resource-limit experiments** on any system.

## 1. In plain words

Imagine renting a hotel room: you get a door that opens only to your room, a number of hours of hot water, and a minibar limit. Other guests are in the same building (the same plumbing and electrical system) but cannot see into your room or use your allowance. A **container** is that for a program:

- It runs on the **same kernel** as everything else on the machine (no second operating system).
- The kernel gives it an **isolated view**: its own process IDs, network interfaces, hostname, mounted file system and users (**namespaces**).
- The kernel **limits what it can consume**: memory, CPU time, number of processes, disk bandwidth (**control groups, cgroups**).
- It is started from an **image**: a packaged, read-only file system containing the program and its dependencies.

So a container is **just a process** (or a few) that the kernel has been told to treat specially. That is why it **starts in milliseconds** and **uses almost no extra memory**: nothing is "booted" ([boot lesson](../boot-and-startup/01-boot-process-and-bootloaders.md)).

```text
VIRTUAL MACHINES                          CONTAINERS
 app  app  app                             app  app  app
 libs libs libs                            libs libs libs
 guest OS | guest OS | guest OS            --------------------------
 ------------------------------            container runtime (Docker, containerd, runc)
 hypervisor (virtual hardware)             ------------------------------------------
 ------------------------------            HOST OPERATING SYSTEM KERNEL (shared)
 host hardware                             host hardware
```

| | **Virtual machine** | **Container** |
|---|---------------------|---------------|
| Isolation boundary | hypervisor and virtual hardware (very strong) | kernel features (strong, but a shared kernel) |
| Contains | a full OS with its own kernel | only the app and its libraries |
| Startup | seconds to minutes | milliseconds to seconds |
| Size | gigabytes | megabytes to a few hundred MB |
| Density | tens per host | hundreds to thousands per host |
| Different OS kernel? | yes (run Windows on Linux) | no (a Linux container needs a Linux kernel) |
| Best for | strong tenant isolation, different OSes | packaging, microservices, CI, dense hosting |

(On macOS and Windows, Docker Desktop quietly runs a small **Linux VM** and puts your containers inside it, which is why "Docker on a Mac" works at all.)

## 2. Namespaces: what a process can see

A **namespace** wraps a global kernel resource so a group of processes sees **its own private instance** of it. Linux has these:

| Namespace | Isolates | Effect inside the container |
|-----------|----------|------------------------------|
| **PID** | process IDs | the first process is PID 1; it cannot see host processes |
| **NET** | network devices, IPs, routing, ports, firewall rules | its own `eth0`, its own `localhost`, its own port 80 |
| **MNT** | mount points | its own root file system (`/`), not the host's |
| **UTS** | hostname and domain | `hostname` can differ from the host |
| **IPC** | System V IPC and POSIX message queues | cannot talk to host processes through shared memory |
| **USER** | user and group IDs | **root inside** can map to an **unprivileged user outside** |
| **CGROUP** | the view of cgroup hierarchy | cannot see or change the host's limits |
| **TIME** (newer) | boot and monotonic clocks | independent offsets |

On Linux you can see which namespaces a process belongs to (two processes in the same namespace show the same number):

```python
import os

if os.path.isdir("/proc/self/ns"):
    for name in sorted(os.listdir("/proc/self/ns")):
        print(f"{name:18} {os.readlink('/proc/self/ns/' + name)}")             # e.g. pid  pid:[4026531836]
else:
    print("no /proc/self/ns here (not Linux); on Linux run: ls -l /proc/self/ns")      # no /proc/self/ns here (not Linux); on Linux run: ls -l /proc/self/ns
```

### Creating namespaces yourself (Linux, reference)

The kernel API is three system calls: **`clone`** (create a process with new namespaces), **`unshare`** (move the current process into new ones) and **`setns`** (join an existing one). The `unshare` command wraps it:

```bash
# Linux only: run a shell in new PID, mount, UTS and network namespaces (needs root, or --user --map-root-user)
sudo unshare --fork --pid --mount-proc --uts --net bash
hostname container-demo        # changes the hostname only inside this namespace
ps aux                         # shows just bash (PID 1) and ps: the host's processes are invisible
ip link                        # only a loopback device: no network until you wire one up
exit
```

Docker, Podman and Kubernetes do exactly this (plus mounts and cgroups) through a small program called **`runc`**.

### A model of PID namespaces

The same process has **two PIDs**: one the host sees and one inside its namespace. A tiny translation table makes the idea concrete:

```python
class PidNamespace:
    """Maps host PIDs to the PIDs a process sees inside this namespace (1, 2, 3, ...)."""
    def __init__(self, name):
        self.name, self.host_to_inner = name, {}

    def spawn(self, host_pid):
        inner = len(self.host_to_inner) + 1
        self.host_to_inner[host_pid] = inner                    # the first process in a namespace is PID 1
        return inner

    def visible(self):
        return sorted(self.host_to_inner.values())

host = {"processes": [1, 812, 4242, 4243, 9001]}                # what the host sees
web = PidNamespace("web")
for host_pid in (4242, 4243):                                   # the container's processes
    web.spawn(host_pid)
db = PidNamespace("db")
db.spawn(9001)

print("host sees      :", host["processes"])                    # host sees      : [1, 812, 4242, 4243, 9001]
print("web container  :", web.visible(), dict(web.host_to_inner))
# web container  : [1, 2] {4242: 1, 4243: 2}
print("db container   :", db.visible(), dict(db.host_to_inner))
# db container   : [1] {9001: 1}
```

The host can see and signal everything; each container sees only its own, numbered from 1. **PID 1 is special**: it adopts orphans and must reap zombies ([processes lesson](../processes-threads/01-processes-in-practice.md)); a container whose PID 1 is a naive script can leak zombies, which is why `docker run --init` adds a tiny init process.

## 3. cgroups: what a process can use

**Control groups (cgroups)** let the kernel **account for and limit** resources used by a group of processes:

| Controller | Limits |
|-----------|--------|
| `memory` | RAM (exceed it and the **OOM killer** terminates a process in the group) |
| `cpu` | CPU time share or a hard quota (for example 0.5 of a core) |
| `pids` | the number of processes (stops **fork bombs**) |
| `io` | disk read/write bandwidth and operations |
| `devices` | which device files may be accessed |

On Linux they are exposed as a **file tree** (`/sys/fs/cgroup`): create a directory, write numbers into files, put process IDs into `cgroup.procs`.

```bash
# Linux reference (cgroup v2): limit a group to 100 MB of RAM
sudo mkdir /sys/fs/cgroup/demo
echo $((100*1024*1024)) | sudo tee /sys/fs/cgroup/demo/memory.max
echo $$ | sudo tee /sys/fs/cgroup/demo/cgroup.procs        # move this shell (and its children) into the group

# Docker does the same with flags:
docker run --memory=100m --cpus=0.5 --pids-limit=100 myimage
```

### Feeling resource limits on any Unix system

The same *idea* exists per process as **resource limits** (`ulimit`, the `resource` module). They are not cgroups (a cgroup limits a whole group; `rlimit` limits one process), but they show the key behavior: **the kernel enforces a ceiling and the process fails in a defined way when it reaches it.** We run the experiments in child processes so our own program is unaffected.

```python
import subprocess, sys, signal

# 1. Limit the number of open files: the process gets an error when it hits the ceiling.
code_files = '''
import resource, tempfile
resource.setrlimit(resource.RLIMIT_NOFILE, (40, 40))              # at most 40 open files for this process
handles = []
try:
    while True:
        handles.append(tempfile.TemporaryFile())
except OSError as e:
    print("stopped after", len(handles), "files:", e.strerror)
'''
result = subprocess.run([sys.executable, "-c", code_files], capture_output=True, text=True)
print(result.stdout.strip())                                      # stopped after 22 files: Too many open files   (the exact count varies by system: stdin/out/err and the interpreter already use some of the 40)
print("Too many open files" in result.stdout)                     # True

# 2. Limit CPU time: the kernel sends SIGXCPU when the budget is spent.
code_cpu = '''
import resource
resource.setrlimit(resource.RLIMIT_CPU, (1, 2))                   # soft limit 1 s of CPU time, hard limit 2 s
while True:
    pass                                                          # busy loop
'''
result = subprocess.run([sys.executable, "-c", code_cpu])
print(result.returncode == -signal.SIGXCPU)                       # True   the process was killed by SIGXCPU after about 1 second of CPU time
```

A cgroup applies the same enforcement idea (exceed memory: killed; exceed CPU quota: **throttled**, i.e. paused until the next period) to a whole container.

**Practical consequences you will meet:**

- A container killed with **exit code 137** ran out of memory (128 + signal 9, the OOM killer).
- A container that is slow but not failing may be **CPU-throttled** by its quota.
- Memory limits must be set **below** what the host has, and runtimes inside (the JVM, Python workers) must **read the cgroup limit**, not the host's RAM, or they size themselves too large.

## 4. Isolating the file system: from `chroot` to images

The mount namespace gives a container its own **root file system**. The oldest ancestor of the idea is **`chroot`**, "change root": make a directory look like `/` to a process, so `..` cannot climb out. A model of the check involved:

```python
import os, tempfile

class Jail:
    def __init__(self, root):
        self.root = os.path.realpath(root)

    def resolve(self, path):
        """Where does `path` (as the jailed process sees it) live on the real disk?"""
        inside = os.path.normpath("/" + path)                   # normalizing '..' against a virtual '/' cannot climb above the root
        real = os.path.realpath(os.path.join(self.root, inside.lstrip("/")))
        if real != self.root and not real.startswith(self.root + os.sep):
            raise PermissionError(f"{path!r} escapes the jail")  # e.g. a symlink pointing outside
        return real

jail_dir = tempfile.mkdtemp()
os.makedirs(os.path.join(jail_dir, "etc"))
open(os.path.join(jail_dir, "etc", "hello.txt"), "w").write("inside the jail")
os.symlink("/etc", os.path.join(jail_dir, "escape"))              # a symlink that points OUT of the jail
jail = Jail(jail_dir)

print(jail.resolve("/etc/hello.txt").endswith("etc/hello.txt"))   # True
print(jail.resolve("/../../etc/hello.txt").endswith("etc/hello.txt"))    # True   '..' just stays at the jail's root
try:
    jail.resolve("/escape/passwd")
except PermissionError as e:
    print("blocked:", e)                                          # blocked: '/escape/passwd' escapes the jail
```

`chroot` alone is **not a security boundary** (a root process can break out, and it isolates nothing but paths). Containers combine the **mount namespace** (`pivot_root` into the image's file system) with all the other namespaces, cgroups, dropped privileges and system-call filters.

## 5. Images and layers

A container image is a **stack of read-only layers**. Each layer is a set of file changes (add/modify/delete). Running a container adds a thin **writable layer** on top, using **copy-on-write**: reading falls through the stack from the top; writing a file copies it into the writable layer first; deleting records a **whiteout** marker that hides the file below.

```text
 writable container layer   <- your changes live here (discarded when the container is removed)
 layer 4: COPY app.py       <- read-only, shared by every container from this image
 layer 3: RUN pip install flask
 layer 2: RUN apt-get install python3
 layer 1: base OS files (e.g. debian)
```

```python
import hashlib, json

class Layered:
    """A union file system: read top-down, copy-on-write, whiteouts for deletes."""
    WHITEOUT = object()

    def __init__(self, image_layers):
        self.image_layers = image_layers                          # list of dicts, bottom to top (read-only, shared)
        self.writable = {}                                        # this container's private layer

    def read(self, path):
        for layer in [self.writable] + self.image_layers[::-1]:   # search from the top down
            if path in layer:
                value = layer[path]
                if value is self.WHITEOUT:
                    raise FileNotFoundError(path)                 # deleted in an upper layer
                return value
        raise FileNotFoundError(path)

    def write(self, path, content):
        self.writable[path] = content                             # never touches the shared layers below

    def delete(self, path):
        self.read(path)                                           # must exist
        self.writable[path] = self.WHITEOUT

base = {"/etc/os-release": "debian", "/bin/python": "python-3.12", "/etc/motd": "welcome"}
deps = {"/lib/flask": "flask-3.0"}
app = {"/app/main.py": "print('hi')"}
image = [base, deps, app]

c1, c2 = Layered(image), Layered(image)                           # two containers from ONE image
c1.write("/etc/motd", "hello from container 1")
c1.delete("/bin/python")
print(c1.read("/etc/motd"), "|", c2.read("/etc/motd"))             # hello from container 1 | welcome   (c2 is unaffected)
try:
    c1.read("/bin/python")
except FileNotFoundError:
    print("c1 deleted python:", c2.read("/bin/python"))           # c1 deleted python: python-3.12      (still there for c2)
print(base["/etc/motd"], len(c1.writable), len(c2.writable))        # welcome 2 0     the shared image is untouched; only c1 stored changes
```

Why this matters:

- **Fast start and tiny cost per container**: nothing is copied until a file is written.
- **Shared storage**: 100 containers from one image share its layers on disk; only their writable layers differ.
- **Fast builds and pulls**: layers are **cached and reused**; changing the last Dockerfile line rebuilds only the top layer, and pulling an image downloads only layers you do not have.
- **Ephemeral by default**: the writable layer vanishes with the container; keep data in **volumes** (directories mounted from outside) so it survives.

### Content addressing: layers are named by their hash

Layers and images are identified by the **SHA-256 digest of their content** (`sha256:ab12...`). The same content always has the same name, so identical layers are stored once and a modified layer is immediately detectable (the same idea as Git objects and the [measured boot](../boot-and-startup/01-boot-process-and-bootloaders.md) chain):

```python
def digest(layer: dict) -> str:
    canonical = json.dumps(layer, sort_keys=True).encode()
    return "sha256:" + hashlib.sha256(canonical).hexdigest()[:16]

print(digest(base) == digest(dict(reversed(list(base.items())))))      # True    same files, same digest regardless of order
print(digest(base) == digest({**base, "/etc/motd": "tampered"}))       # False   any change gives a different name

def image_id(layers):                                                  # an image is identified by the chain of its layers
    h = hashlib.sha256()
    for layer in layers:
        h.update(digest(layer).encode())
    return h.hexdigest()[:12]

print(image_id([base, deps, app]) == image_id([base, deps, app]), image_id([base, deps, app]) == image_id([base, deps, {"/app/main.py": "print('bye')"}]))
# True False
```

## 6. A Dockerfile and the everyday commands (reference)

A **Dockerfile** is a recipe; each instruction usually creates a layer. Put things that change **rarely** first (so the cache is reused) and things that change **often** last:

```dockerfile
FROM python:3.12-slim                 # base image (layer 1..n)
WORKDIR /app
COPY requirements.txt .               # copy only the dependency list first ...
RUN pip install --no-cache-dir -r requirements.txt     # ... so this slow layer is cached until requirements change
COPY . .                              # your code changes often: keep it last
USER 10001                            # do not run as root inside the container
EXPOSE 8000
CMD ["python", "-m", "http.server", "8000"]
```

```bash
docker build -t myapp:1.0 .                    # build an image from the Dockerfile in this directory
docker run --rm -p 8080:8000 --memory=200m --cpus=1 myapp:1.0     # run it, publish port 8000 as 8080, with limits
docker ps                                      # running containers
docker logs -f <container>                     # follow its output
docker exec -it <container> sh                 # a shell inside a running container (joins its namespaces)
docker stop <container>                        # SIGTERM, then SIGKILL after 10 seconds: handle SIGTERM!
docker run -v mydata:/var/lib/data myapp:1.0   # a named volume: data outlives the container
docker image ls; docker system df              # images and disk usage
```

Tools around it: **Docker Compose** (several containers described in one YAML file), **Kubernetes** (scheduling, scaling and healing containers across many machines), **Podman** (daemonless, rootless alternative), **containerd/CRI-O** (the lower-level runtimes Kubernetes uses).

## 7. Security: what containers do and do not protect against

Containers share the **host kernel**, so a kernel vulnerability can let a process escape. Layers of defense:

| Mechanism | What it does |
|-----------|--------------|
| **User namespaces / rootless** | "root" inside the container is a harmless unprivileged user outside |
| **Capabilities** | root's powers are split into ~40 pieces; containers drop most of them (no raw network, no mounting) |
| **seccomp** | a **system-call filter**: the process may only make an allowed list of syscalls (blocks risky ones like `reboot`) |
| **AppArmor / SELinux** | mandatory access control policies restricting files and operations |
| **Read-only root file system, no privileged mode** | limits what a compromised process can change |
| **Image scanning, minimal base images, signed images** | reduce vulnerabilities and supply-chain risk |

Habits: **do not run as root**, never use `--privileged` casually or mount the Docker socket into a container, pin image versions (not `latest`), keep images small (fewer packages, fewer holes), scan them, and never bake secrets into an image (they stay in the layers and in `docker history`). For **hostile multi-tenant** workloads use stronger isolation: **microVMs** (Firecracker, used by AWS Lambda) or **gVisor/Kata** sandboxes, which add a VM or a user-space kernel between the container and the host kernel.

## 8. Two real-world examples

**Example 1: "It works on my machine."** The app needs Python 3.12 and a specific OpenSSL; the laptop has 3.9. The team ships an **image** containing the exact runtime and libraries, so development, CI and production run the identical filesystem. Environment drift disappears, and onboarding becomes `docker compose up`.

**Example 2: A noisy neighbor on a shared server.** A memory leak in one service slowly consumed the host's RAM and the kernel's OOM killer picked the *database* as the victim. After putting every service in a container with `--memory` limits, the leaking service is now killed (exit code 137) and restarted by the orchestrator, while the database never notices: **cgroups turned a host-wide outage into a contained failure.**

## 9. Common mistakes

- Treating a container as a lightweight VM: it has no separate kernel, so a Linux container cannot run a different kernel or kernel modules.
- Running as root inside the container, or using `--privileged` "to make it work".
- Storing data in the container's writable layer and losing it on removal (use volumes).
- A naive PID 1 that ignores `SIGTERM` (the container takes 10 seconds to stop) or never reaps zombies (use `--init` or an exec-form `CMD`).
- Not setting memory and CPU limits, then letting one container starve the rest.
- Huge images (a full OS, build tools, caches left in layers): use slim bases and **multi-stage builds**.
- Copying secrets into the build (they persist in layers); use runtime secrets or build secrets.
- Using the `latest` tag in production (non-reproducible deployments).
- Expecting namespaces to hide everything: the host kernel, CPU model and clock behavior are shared.

## 10. Practice

1. Name the two kernel features that make a container, and say which controls what a process *sees* and which controls what it *uses*.
2. A container is killed with exit code 137. What most likely happened, and what two actions might you take?
3. Why does starting a container take milliseconds while booting a VM takes seconds?
4. Use `PidNamespace` to model a container with three processes with host PIDs 700, 701, 705 and print the inner PIDs.
5. Using the `Layered` model, create a container, delete `/etc/motd`, then write it again with new content. What does `read` return and what is in the writable layer?
6. Why does the order of Dockerfile instructions affect build speed?
7. Why is `chroot` alone not enough to sandbox a hostile process?
8. What happens to data written inside a container's file system when the container is removed, and how do you keep it?

<details>
<summary>Solutions</summary>

1. **Namespaces** (what a process can *see*: PIDs, network, mounts, hostname, users) and **cgroups** (what it can *use*: memory, CPU, processes, I/O).
2. 137 is 128 + 9: the process was killed with `SIGKILL`, almost always by the kernel's **OOM killer** because it exceeded its memory limit (or the host ran out). Raise the limit (or reduce the app's memory use / fix the leak), and make sure the application reads the cgroup limit; also add monitoring and a restart policy.
3. A container is an ordinary process started with namespaces and cgroup settings on the already-running host kernel; a VM must boot a whole guest operating system (firmware, bootloader, kernel, init).
4. ```python
   ns = PidNamespace("demo")
   print([ns.spawn(pid) for pid in (700, 701, 705)], dict(ns.host_to_inner))
   # [1, 2, 3] {700: 1, 701: 2, 705: 3}
   ```
5. ```python
   c = Layered(image)
   c.delete("/etc/motd")
   c.write("/etc/motd", "new message")
   print(c.read("/etc/motd"), c.writable)                        # new message {'/etc/motd': 'new message'}
   ```
   The later write replaces the whiteout in the writable layer, so the file is visible again with the new content; the shared base layer still holds `welcome`.
6. Each instruction creates a cached layer; when one changes, every layer *after* it must be rebuilt. Put rarely changing steps (installing dependencies) before frequently changing ones (copying source code) so rebuilds reuse the cache.
7. `chroot` only changes how paths resolve. It does not isolate processes, the network, users or resources, and a process with root privileges can often escape it; containers add the other namespaces, cgroups, dropped capabilities and seccomp filters.
8. It is discarded with the writable layer. Use **volumes** or bind mounts (`docker run -v name:/path`) or an external database/object store for anything that must survive.

</details>

## 11. Check yourself

1. What is a container, in one sentence?
2. List five namespaces and what each isolates.
3. What do cgroups limit, and what happens when a memory limit is exceeded?
4. How do image layers and copy-on-write save space and time?
5. How do containers differ from virtual machines in isolation and cost?
6. Name three defenses that make containers safer.

<details>
<summary>Answers</summary>

1. An ordinary process (or group) on the host kernel, given an isolated view (namespaces) and resource limits (cgroups), started from a packaged image.
2. PID (process IDs), NET (network stack), MNT (mounts/root file system), UTS (hostname), IPC (inter-process communication), USER (user and group IDs), CGROUP, TIME.
3. Memory, CPU time or share, process count, I/O bandwidth and device access; exceeding a memory limit triggers the OOM killer for that group (exit code 137).
4. Layers are read-only and shared by all containers and images that use them; a container stores only its own changes in a thin writable layer (copy-on-write), and builds and pulls reuse cached layers.
5. VMs have a separate guest kernel behind a hypervisor (stronger isolation, heavier, slower to start); containers share the host kernel (lighter and faster, with a larger attack surface if the kernel is vulnerable).
6. Run as non-root (user namespaces/rootless), drop capabilities, apply seccomp and AppArmor/SELinux profiles, use a read-only root file system, scan and minimize images, avoid `--privileged`.

</details>

[Back to operating systems](../README.md)
