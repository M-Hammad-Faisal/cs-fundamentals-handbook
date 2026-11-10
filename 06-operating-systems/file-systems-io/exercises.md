# File Systems and I/O: Exercises

1. Create a file, make a hard link and a symlink to it, delete the original name, and explain what still works and why.
2. Write `atomic_write(path, data)` and explain what could go wrong without `fsync` and without the rename.
3. Write a function that counts lines in a multi-gigabyte file using constant memory.
4. A server throws `OSError: [Errno 24] Too many open files`. List three causes and how you would diagnose.
5. Explain why `df` says the disk is full after you delete a huge log file, and how to recover the space.
6. Using `selectors`, write a tiny server that echoes uppercase text from several clients in one thread.
7. Compare blocking thread-per-connection with an event loop for 10,000 mostly idle connections.
8. Why are databases built around sequential appends (WAL) rather than random writes?

<details>
<summary>Solutions</summary>

**1.**
```python
import os, tempfile
d = tempfile.mkdtemp(); a = os.path.join(d, "a"); open(a, "w").write("x")
os.link(a, a + ".hard"); os.symlink(a, a + ".sym"); os.remove(a)
print(os.path.exists(a + ".hard"), os.path.exists(a + ".sym"))   # True False
```
The hard link is another name for the same inode, so the data survives. The symlink holds the old path, which no longer exists.

**2.** See the lesson. Without `fsync` the data may only be in the page cache when power fails, leaving a zero-length or partial file. Without the rename, a crash during writing leaves the original truncated or half-overwritten.

**3.**
```python
def count_lines(path):
    n = 0
    with open(path, "rb") as f:
        for _ in f:
            n += 1
    return n
```
Iterating the file object reads buffered chunks, so memory stays constant.

**4.** Causes: descriptor leaks (files or sockets not closed, missing `with`), too many concurrent connections for the `ulimit -n` value, a library or loop opening files repeatedly. Diagnose with `lsof -p <pid> | wc -l`, `ls /proc/<pid>/fd`, check `ulimit -n`, and watch whether the count grows over time.

**5.** The process still has the file open, so the inode and its blocks remain allocated. Find it with `lsof +L1`, then restart the process or truncate the file through its open descriptor (`: > /proc/<pid>/fd/<n>`). To avoid it, truncate or use log rotation signals instead of `rm`.

**6.**
```python
import selectors, socket
sel = selectors.DefaultSelector()
srv = socket.socket(); srv.bind(("127.0.0.1", 0)); srv.listen(); srv.setblocking(False)
sel.register(srv, selectors.EVENT_READ)
def serve_once():
    for key, _ in sel.select(timeout=1):
        if key.fileobj is srv:
            c, _ = srv.accept(); c.setblocking(False); sel.register(c, selectors.EVENT_READ)
        else:
            data = key.fileobj.recv(1024)
            if data: key.fileobj.sendall(data.upper())
            else: sel.unregister(key.fileobj); key.fileobj.close()
```
Call `serve_once()` in a loop.

**7.** Thread-per-connection costs a stack (about MBs of address space) plus context switching for each connection, and most threads sit blocked. An event loop keeps one small state object per connection and only runs code for the few that are ready, so memory and CPU stay low. Threads are simpler for CPU-heavy per-request work.

**8.** Sequential appends are fast on both HDD and SSD, and a log gives crash recovery and atomic commits (`fsync` once per batch). The database applies changes to its data pages later in the background, so random writes are batched and deferred.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [File Systems in Depth](01-file-systems-in-depth.md)
