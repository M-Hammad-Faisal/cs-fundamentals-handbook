# What Is an Operating System?

**Prerequisites:** [how computers work](../00-foundations/computer-basics/how-computers-work.md), [stack and heap memory](../00-foundations/computer-basics/memory-stack-heap.md). **You will learn:** what an OS does and why it exists, the **kernel**, **user mode versus kernel mode**, **system calls** (and how to watch them), how a computer **boots**, and the map of this part of the handbook.

## 1. In plain words

Your laptop has one CPU (with a few cores), some memory, a disk, a network card. Dozens of programs want to use them **at the same time** and none of them should be able to crash or spy on the others. The **operating system (OS)** is the manager that makes this work. It does three jobs:

1. **Share** the hardware fairly (CPU time, memory, disk, network) among programs.
2. **Protect** programs from each other and the system from programs.
3. **Hide** hardware messiness behind simple ideas: a **file** instead of disk sectors, a **process** instead of raw CPU registers, **memory** that looks private and huge.

Analogy: a hotel. Guests (programs) have private rooms (address spaces) and share facilities (CPU, disk). The front desk (kernel) enforces rules and gives keys; guests ask politely for services (system calls) rather than walking into the kitchen.

## 2. The layers

```text
  Your programs   (browser, editor, Python script)
  ----------------------------------------------
  Libraries       (libc, Python's os module)
  ----------------------------------------------
  System calls    (open, read, write, fork, mmap ...)   <- the doorway into the kernel
  ----------------------------------------------
  KERNEL          (scheduler, memory manager, file systems, drivers, network stack)
  ----------------------------------------------
  Hardware        (CPU, RAM, disk, NIC)
```

The **kernel** is the always-running core of the OS. "Windows", "macOS" and "Linux" are operating systems; **Linux** by itself is strictly a kernel (distributions like Ubuntu add tools around it).

## 3. User mode versus kernel mode

The CPU has (at least) two privilege levels:

| Mode | Who runs there | What it may do |
|------|----------------|----------------|
| **User mode** | your programs | ordinary computation; cannot touch hardware or other programs' memory |
| **Kernel mode** | the kernel | everything: talk to devices, change memory mappings, halt the machine |

A program that tries something forbidden (dividing by zero, touching memory it does not own) triggers a **trap** into the kernel, which usually kills just that program (`Segmentation fault`). This is why one buggy app does not take down the whole computer.

## 4. System calls: asking the kernel for help

A program in user mode cannot read a file itself. It makes a **system call** (syscall): a controlled jump into the kernel, which does the work and returns the result. Everyday functions wrap syscalls:

| You write (Python) | Syscall underneath | Meaning |
|--------------------|--------------------|---------|
| `open("a.txt")` | `open` / `openat` | get a file descriptor |
| `f.read()` | `read` | copy bytes from the file into your memory |
| `print("hi")` | `write` | write bytes to descriptor 1 (stdout) |
| `subprocess.run([...])` | `fork`+`exec` (or `posix_spawn`) | start a new process |
| `time.sleep(1)` | `nanosleep` | ask to be woken later |
| `socket.socket()` | `socket` | create a network endpoint |
| `os.getpid()` | `getpid` | who am I? |

You can call the thin wrappers directly with Python's `os` module, which maps almost one-to-one to Unix syscalls:

```python
import os

pid = os.getpid()                                   # syscall: getpid
fd = os.open("/tmp/os_demo.txt", os.O_WRONLY | os.O_CREAT | os.O_TRUNC)     # syscall: open -> a small integer
written = os.write(fd, b"hello kernel\n")           # syscall: write
os.close(fd)                                        # syscall: close
print(isinstance(pid, int), fd >= 3, written)       # True True 13

fd = os.open("/tmp/os_demo.txt", os.O_RDONLY)
print(os.read(fd, 100))                             # b'hello kernel\n'
os.close(fd)
os.remove("/tmp/os_demo.txt")
```

Why `fd >= 3`? Every process starts with three **file descriptors** already open: `0` = stdin, `1` = stdout, `2` = stderr. The first file you open gets the next free number.

### Watching syscalls (optional, Linux/macOS)

```bash
strace -c python3 -c "print('hi')"       # Linux: count syscalls
sudo dtruss -c python3 -c "print('hi')"  # macOS equivalent (needs sudo)
```

A trivial Python program makes hundreds of syscalls just to start. Each costs roughly a microsecond or less, so **many small reads are slower than one big read** (the reason for buffering):

```python
import os, time

path = "/tmp/os_syscall_cost.bin"
with open(path, "wb") as f:
    f.write(os.urandom(2_000_000))

def read_all(chunk):
    fd, total = os.open(path, os.O_RDONLY), 0
    while True:
        data = os.read(fd, chunk)               # one syscall per chunk
        if not data:
            break
        total += len(data)
    os.close(fd)
    return total

t = time.perf_counter(); read_all(1); tiny = time.perf_counter() - t
t = time.perf_counter(); read_all(64_000); big = time.perf_counter() - t
print(tiny > 20 * big)                              # True   (2,000,000 syscalls versus about 32)
os.remove(path)
```

## 5. What happens when the computer starts (boot)

1. **Firmware** (BIOS or UEFI) runs from a chip, tests the hardware and finds a boot device.
2. The **bootloader** (GRUB, Windows Boot Manager) loads the kernel from disk into memory.
3. The **kernel** initializes memory management, drivers and the scheduler, then mounts the root file system.
4. The kernel starts the first user process, **`init`** (PID 1; `systemd` on many Linux systems, `launchd` on macOS), which starts everything else: services, the login screen, your shell.

Every process is a **descendant of PID 1**. If a parent dies, PID 1 adopts its children (orphans).

```python
import os
print(os.getppid() > 0)                             # True   (my parent process exists: shell, IDE, or init)
```

## 6. Kinds of kernels (a quick map)

| Design | Idea | Example |
|--------|------|---------|
| **Monolithic** | all OS services run in kernel mode: fast, but a driver bug can crash everything | Linux |
| **Microkernel** | only the bare minimum in the kernel; services run as user processes: safer, more messaging | QNX, MINIX, seL4 |
| **Hybrid** | a mix | Windows NT, macOS (XNU) |
| **Unikernel / containers** | containers *share one kernel* with isolated views; unikernels bundle app and kernel | Docker, MirageOS |

## 7. Things the OS manages: your map for this part

| Resource | OS abstraction | Lesson |
|----------|----------------|--------|
| CPU | **process / thread**, **scheduler** | [processes and threads](processes-threads/README.md), [scheduling](scheduling/README.md) |
| Memory | **virtual address space**, paging | [memory and virtual memory](memory-virtual-memory/README.md) |
| Coordination | locks, semaphores, deadlock avoidance | [concurrency and deadlocks](concurrency-deadlocks/README.md) |
| Disk | **files**, directories, file systems | [file systems and I/O](file-systems-io/README.md) |
| Network | **sockets** | [networking](../07-networking/README.md) |

## 8. Two real-world examples

**Example 1: Why an app can crash without crashing the computer.** The kernel gave the app its own address space; touching an unmapped address makes the CPU trap, and the kernel ends only that process. On a system without such protection (old DOS), one bad pointer froze everything.

**Example 2: Containers.** Docker does not boot a second OS. Containers are ordinary processes with isolated views of files, processes and the network provided by kernel features (namespaces, cgroups). That is why a container starts in milliseconds while a virtual machine (which boots its own kernel) takes seconds.

## 9. Common mistakes

- Thinking "the OS" is the same as "the kernel" or the desktop.
- Believing programs talk to hardware directly (they ask the kernel).
- Assuming syscalls are free (they are cheap, not free; batch your I/O).
- Forgetting that `fork`, signals and `/proc` behave differently on Windows.

## 10. Practice

1. List three resources an OS shares between programs and one way it protects them.
2. In your own words: why does the CPU have a kernel mode?
3. Using `os.open`/`os.write`, write the line `abc` to `/tmp/x.txt` and read it back with `os.read`.
4. Which file descriptor numbers does every process start with, and what are they?
5. Why is reading a 1 MB file one byte at a time slow?
6. What is PID 1 and what does it do?

<details>
<summary>Solutions</summary>

1. CPU time, memory, disk (or network). Protection: separate virtual address spaces plus user/kernel mode, so a program cannot read another's memory.
2. So only trusted kernel code can touch hardware and memory mappings; an ordinary program's mistake is trapped instead of corrupting the machine.
3. ```python
   import os
   fd = os.open("/tmp/x.txt", os.O_WRONLY | os.O_CREAT | os.O_TRUNC); os.write(fd, b"abc"); os.close(fd)
   fd = os.open("/tmp/x.txt", os.O_RDONLY); print(os.read(fd, 10)); os.close(fd); os.remove("/tmp/x.txt")      # b'abc'
   ```
4. 0 (stdin), 1 (stdout), 2 (stderr).
5. Each byte costs a syscall (a switch into the kernel); a million syscalls versus a handful for large reads.
6. The first user process started by the kernel; it launches services and adopts orphaned processes.

</details>

## 11. Check yourself

1. What are the three jobs of an operating system?
2. What is the difference between user mode and kernel mode?
3. What is a system call and why does it exist?
4. What is the sequence from power-on to your shell?
5. How do containers differ from virtual machines?

<details>
<summary>Answers</summary>

1. Share hardware, protect programs from each other, and provide simple abstractions (files, processes, virtual memory).
2. User mode is restricted (no direct hardware access); kernel mode can do anything. Programs reach the kernel only through controlled entry points.
3. A controlled request from a user program to the kernel (open a file, create a process), so only the kernel performs privileged work.
4. Firmware, bootloader, kernel start-up, PID 1 (init), services, login/shell.
5. Containers share the host kernel and isolate views using namespaces and cgroups; VMs run a full separate kernel on virtualized hardware.

</details>

Next: [processes and threads](processes-threads/README.md) · Back to [OS overview](README.md)
