# File Systems and I/O

## 1. The concept

A **file system** turns raw disk blocks into named files in directories. The OS exposes it through a small, uniform API (`open`, `read`, `write`, `close`) that also works for pipes, sockets and devices: "everything is a file" on Unix.

## 2. How a file system works

### Layers

```text
application:  open("a.txt"), read, write
   |
VFS (virtual file system): one interface over ext4, XFS, APFS, NTFS, NFS, tmpfs ...
   |
page cache: recently used file data kept in RAM
   |
block layer + device driver  ->  SSD / HDD
```

### Inodes, directories and links

A file's metadata (size, owner, permissions, timestamps, pointers to data blocks) lives in an **inode**. The **name** is not in the inode: a **directory** is a table mapping names to inode numbers.

- **Hard link:** another name for the same inode (the file is freed when its link count reaches 0 *and* nothing has it open).
- **Symlink:** a tiny file holding a path; it can dangle if the target disappears.

```python
import os, tempfile

d = tempfile.mkdtemp()
a = os.path.join(d, "a.txt")
with open(a, "w") as f:
    f.write("hello")

b = os.path.join(d, "b.txt")
s = os.path.join(d, "s.txt")
os.link(a, b)                      # hard link: second name for the same inode
os.symlink(a, s)                   # symlink: a file that stores a path
print(os.stat(a).st_ino == os.stat(b).st_ino, os.stat(a).st_nlink)   # True 2
os.remove(a)
print(open(b).read(), os.path.exists(s))                             # hello False  (symlink dangles)
```

### Allocation and layout

| Strategy | Idea | Trade-off |
|----------|------|-----------|
| Contiguous | File in one run of blocks | Fast, external fragmentation |
| Linked | Each block points to the next | No fragmentation, slow random access (FAT) |
| Indexed (inode) | Inode holds block pointers, with indirect blocks | Good random access (Unix) |
| Extents | Store (start, length) runs | Compact, used by ext4, XFS, NTFS |

### Journaling and crash safety

A crash mid-update can leave the file system inconsistent. **Journaling** (ext4, NTFS, XFS) writes intended changes to a log first, then applies them; after a crash it replays or discards the log. **Copy-on-write** file systems (ZFS, Btrfs, APFS) never overwrite live data and add checksums and snapshots.

### The page cache and durability

`write()` normally lands in the **page cache**, not on disk, so the program continues fast and the OS flushes later. If power fails first, data is lost. `fsync(fd)` forces the file's data to stable storage. Writing a config safely means writing a temp file, `fsync`, then an **atomic rename**:

```python
import os, tempfile
d = tempfile.mkdtemp()
def atomic_write(path, data: bytes):
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())       # force data to disk
    os.replace(tmp, path)          # atomic rename: readers see old or new, never half
atomic_write(os.path.join(d, "config.json"), b'{"v": 2}')
print(open(os.path.join(d, "config.json")).read())
```

## 3. File descriptors

A process refers to open files by small integers, **file descriptors**: 0 = stdin, 1 = stdout, 2 = stderr. Each descriptor points to an open file description holding the current **offset**. `fork` duplicates descriptors (parent and child share offsets), and redirection like `cmd > out.txt` works by swapping descriptor 1 before running the program. Each process has a limit (`ulimit -n`); leaking descriptors eventually causes "Too many open files".

```python
import os, tempfile
d = tempfile.mkdtemp()
fd = os.open(os.path.join(d, "raw.bin"), os.O_RDWR | os.O_CREAT)
os.write(fd, b"0123456789")
os.lseek(fd, 3, os.SEEK_SET)       # move the offset
print(os.read(fd, 4))              # b'3456'
os.close(fd)
```

## 4. I/O models

| Model | Behavior | Use |
|-------|----------|-----|
| **Blocking** | Thread sleeps until data is ready | Simple code, one thread per connection |
| **Non-blocking** | Call returns immediately ("would block") | Needs polling |
| **Multiplexing** (`select`, `poll`, `epoll`, `kqueue`) | One thread waits on many descriptors | Servers with many idle connections |
| **Async I/O** (`io_uring`, IOCP) | Submit work, get completion later | High-performance servers, disks |

The **C10K problem** (10,000 concurrent connections) is why event-driven servers (nginx, Node.js, asyncio) replaced thread-per-connection designs. `asyncio` is built on exactly the multiplexing below.

```python
import selectors, socket

def echo_once():
    sel = selectors.DefaultSelector()
    server = socket.socket()
    server.bind(("127.0.0.1", 0)); server.listen(); server.setblocking(False)
    sel.register(server, selectors.EVENT_READ)
    clients = [socket.create_connection(server.getsockname()) for _ in range(3)]
    for i, c in enumerate(clients):
        c.sendall(f"msg{i}".encode())
    seen, conns = [], []
    while len(seen) < 3:
        for key, _ in sel.select(timeout=2):
            if key.fileobj is server:
                conn, _ = server.accept(); conn.setblocking(False)
                sel.register(conn, selectors.EVENT_READ); conns.append(conn)
            else:
                data = key.fileobj.recv(100)
                if data: seen.append(data.decode())
                sel.unregister(key.fileobj)
    for c in clients + conns + [server]: c.close()
    return sorted(seen)
print(echo_once())
```

### Buffering

Reading and writing in bigger chunks cuts system calls, which cost far more than function calls. Python's file objects buffer for you; line buffering or flushing after every write is much slower.

```python
import os, tempfile, time
d = tempfile.mkdtemp()
import time
p = os.path.join(d, "big.txt")
t = time.perf_counter()
with open(p, "w", buffering=1 << 16) as f:
    for i in range(200_000): f.write("x\n")
buffered = time.perf_counter() - t
t = time.perf_counter()
with open(p, "w", buffering=1) as f:               # line buffered: flush every line
    for i in range(200_000): f.write("x\n")
line = time.perf_counter() - t
print(buffered < line)
```

### Seek time and access patterns

HDDs are slow at **random** access (milliseconds of seek) and good at sequential; SSDs have no seek penalty but still prefer larger, aligned, sequential writes and wear out with heavy random writes. Databases use **append-only logs** and sequential I/O for this reason.

## 5. Two real-world examples

### Example 1: Why your editor saves via rename
Many editors and databases write a new file next to the old one, `fsync` it, then `rename` it over the original. Because rename is atomic, a crash leaves either the complete old file or the complete new one, never a half-written file. This is the atomic-write pattern shown above.

### Example 2: Log rotation and deleted-but-open files
A disk is full, so someone deletes a 50 GB log, but `df` still shows it full. The server still has the file open, and the inode (with its blocks) is only freed when the last descriptor closes. `lsof +L1` finds such files; restarting the process (or truncating instead of deleting) frees the space. It is a direct consequence of "names point to inodes".

## 6. Tips, tricks and pitfalls

- Use `with open(...)` so descriptors close even on errors; specify `encoding="utf-8"` for text.
- Do not assume `write` means durable; use `fsync` where data loss matters, and understand its cost.
- Use `pathlib` and `os.replace` for atomic overwrites; avoid check-then-open races (`if exists: open`) and use exceptions or `O_EXCL`.
- Stream large files (iterate lines or read chunks) instead of reading all at once.
- Beware symlink attacks when writing to shared directories like `/tmp`; use `tempfile`.
- Watch for descriptor leaks and the `ulimit -n` limit in servers.
- Network file systems (NFS) have different caching and locking guarantees from local disks.

## 7. Check yourself

1. What is stored in an inode, and where is the file's name stored?
2. Hard link versus symlink?
3. Why does `write` not guarantee the data is on disk, and what does `fsync` do?
4. How do you replace a config file so a crash never leaves it half-written?
5. What are file descriptors 0, 1 and 2?
6. Why do `epoll`-based servers handle many connections with few threads?
7. Why can a deleted file still use disk space?
8. What does journaling protect against?

<details>
<summary>Answers</summary>

1. Metadata (size, owner, permissions, timestamps, block pointers). The name lives in a directory entry that maps name to inode number.
2. A hard link is another directory entry for the same inode (survives deleting the original name; same file system only). A symlink stores a path and breaks if the target is removed.
3. Data goes to the page cache first and is flushed later. `fsync` blocks until the data (and needed metadata) reaches stable storage.
4. Write to a temp file in the same directory, `fsync`, then `os.replace` it over the target (atomic rename).
5. stdin, stdout, stderr.
6. They block on a readiness API for many sockets at once and only do work for those that are ready, instead of dedicating a blocked thread to each connection.
7. The inode and blocks are freed only when the link count is zero and no process still has the file open.
8. Inconsistent file system metadata after a crash or power loss: the journal lets the system replay or roll back incomplete updates.

</details>

[Exercises](exercises.md) · [Summary](summary.md)
