# File Systems in Depth: Inodes, Links, Permissions and Durability

**Prerequisites:** [what is an OS](../00-what-is-an-operating-system.md), [binary and bytes](../../00-foundations/computer-basics/binary-and-data-representation.md). **You will learn:** how a file system turns raw disk blocks into files and folders (**blocks, inodes, directories, free-space bitmaps**) by building a tiny one; how **hard links, symbolic links, permissions and timestamps** really work (with real `os` calls); why a power cut can lose data and how **`fsync`, atomic rename and journaling** protect it; and the main **I/O models**.

## 1. In plain words

A disk (or SSD) is a huge array of fixed-size **blocks** (commonly 4 KB) with no idea what a "file" is. The **file system** is the software layer that organizes those blocks so you can have **named files in folders**, find them quickly, grow and delete them, and survive crashes.

Analogy: a library. The shelves are the blocks. The **catalog** (an index card per book saying which shelves hold its pages) is the **inode**. The **folder structure** is a special kind of book that lists *names and card numbers*.

## 2. The building blocks

| Piece | What it holds |
|-------|---------------|
| **Data blocks** | the actual file contents (and directory contents) |
| **Inode** (index node) | a file's **metadata**: size, owner, permissions, timestamps, link count, and **which blocks hold the data**. It does **not** contain the file's name |
| **Directory** | a file whose content is a table of `(name -> inode number)` entries |
| **Bitmap / free list** | which blocks and inodes are free |
| **Superblock** | the file system's own header: block size, counts, where things start |

Key insight: **the name lives in the directory, not the file.** That is why one file can have several names (hard links), and why renaming is cheap.

```text
directory "/home/ana" (inode 12)        inode 57                    data blocks
 +-----------------------+     +--------------------------+       +------+  +------+
 | notes.txt   -> 57     | --> | size 6000, owner ana,    | ----> | blk 9 |  | blk 4 |
 | photo.jpg   -> 88     |     | links 1, blocks [9, 4]   |       +------+  +------+
 +-----------------------+     +--------------------------+
```

## 3. Build a tiny file system

A model with the same moving parts (all in memory, but following the real structure):

```python
BLOCK_SIZE = 16                                           # tiny blocks so files span several of them

class Inode:
    def __init__(self, kind):
        self.kind = kind                                  # "file" or "dir"
        self.size = 0
        self.blocks = []                                  # indexes of data blocks
        self.links = 0                                    # how many directory entries point here

class TinyFS:
    def __init__(self, num_blocks=32):
        self.disk = [b""] * num_blocks                    # the "disk"
        self.free_blocks = set(range(num_blocks))         # the free-space map
        self.inodes = {}
        self.next_inode = 1
        self.root = self._new_inode("dir")
        self.inodes[self.root].links = 1
        self.inodes[self.root].entries = {}               # a directory's content: name -> inode number

    def _new_inode(self, kind):
        number, self.next_inode = self.next_inode, self.next_inode + 1
        self.inodes[number] = Inode(kind)
        if kind == "dir":
            self.inodes[number].entries = {}
        return number

    def _lookup(self, path):
        """Walk the path component by component, like the kernel does; return the inode number."""
        number = self.root
        for part in [p for p in path.split("/") if p]:
            inode = self.inodes[number]
            if inode.kind != "dir" or part not in inode.entries:
                raise FileNotFoundError(path)
            number = inode.entries[part]
        return number

    def _split(self, path):
        parent_path, _, name = path.rstrip("/").rpartition("/")
        return self._lookup(parent_path or "/"), name

    def mkdir(self, path):
        parent, name = self._split(path)
        number = self._new_inode("dir")
        self.inodes[number].links = 1
        self.inodes[parent].entries[name] = number

    def write(self, path, data: bytes):
        parent, name = self._split(path)
        number = self.inodes[parent].entries.get(name)
        if number is None:                                # create
            number = self._new_inode("file")
            self.inodes[number].links = 1
            self.inodes[parent].entries[name] = number
        inode = self.inodes[number]
        self.free_blocks.update(inode.blocks)             # overwriting frees the old blocks
        inode.blocks = []
        chunks = [data[i:i + BLOCK_SIZE] for i in range(0, len(data), BLOCK_SIZE)]
        if len(chunks) > len(self.free_blocks):
            raise OSError("No space left on device")
        for chunk in chunks:
            block = min(self.free_blocks)                 # first free block (real systems try to keep blocks contiguous)
            self.free_blocks.remove(block)
            self.disk[block] = chunk
            inode.blocks.append(block)
        inode.size = len(data)

    def read(self, path):
        inode = self.inodes[self._lookup(path)]
        return b"".join(self.disk[b] for b in inode.blocks)

    def link(self, existing, new_path):                   # hard link: another name for the SAME inode
        number = self._lookup(existing)
        parent, name = self._split(new_path)
        self.inodes[parent].entries[name] = number
        self.inodes[number].links += 1

    def unlink(self, path):                               # rm: remove a name; free the data only when no names remain
        parent, name = self._split(path)
        number = self.inodes[parent].entries.pop(name)
        inode = self.inodes[number]
        inode.links -= 1
        if inode.links == 0:
            self.free_blocks.update(inode.blocks)
            del self.inodes[number]

    def listdir(self, path):
        return sorted(self.inodes[self._lookup(path)].entries)

fs = TinyFS()
fs.mkdir("/docs")
fs.write("/docs/hello.txt", b"Hello, file systems! This spans several blocks.")
print(fs.listdir("/docs"), fs.read("/docs/hello.txt"))
# ['hello.txt'] b'Hello, file systems! This spans several blocks.'

inode = fs.inodes[fs._lookup("/docs/hello.txt")]
print(inode.size, inode.blocks, inode.links)             # 47 [0, 1, 2] 1       (47 bytes in three 16-byte blocks)
```

### Hard links and deletion

```python
fs.link("/docs/hello.txt", "/docs/alias.txt")            # a second name for the same inode
alias_inode = fs._lookup("/docs/alias.txt")
print(fs.listdir("/docs"), fs.inodes[alias_inode].links)      # ['alias.txt', 'hello.txt'] 2
fs.unlink("/docs/hello.txt")                              # remove one name: the data is still reachable
print(fs.read("/docs/alias.txt")[:5], len(fs.free_blocks))      # b'Hello' 29
fs.unlink("/docs/alias.txt")                              # the last name: now the blocks are freed
print(len(fs.free_blocks), alias_inode in fs.inodes)      # 32 False
```

Deleting a file really means **removing a name and decrementing the link count**; the data is freed only when the count reaches zero (and no process still has the file open). That is why you can delete a log file that a process is still writing to and the disk space does **not** come back until the process closes it or exits.

### Running out of space and fragmentation

```python
full = TinyFS(num_blocks=4)                               # a very small disk: 4 blocks of 16 bytes
full.write("/a", b"x" * 40)                               # needs 3 blocks
try:
    full.write("/b", b"y" * 40)                           # needs 3 more: only 1 free
except OSError as e:
    print(e)                                              # No space left on device
```

**Fragmentation:** after many creates and deletes a file's blocks end up scattered (hard disks slow down because the head must move; SSDs do not mind). **Allocation strategies** real file systems use: contiguous, linked blocks, indexed (inode with direct pointers plus indirect blocks for big files), and **extents** (store "start block + length" ranges, as ext4, XFS and NTFS do).

## 4. How big can a file be? Direct and indirect pointers

Classic ext2-style inodes keep 12 **direct** block pointers, then pointers to an **indirect block** (a block full of more pointers), a **double indirect** block and a **triple indirect** block.

```python
def max_file_size(block_size=4096, pointer_size=4, direct=12):
    per_block = block_size // pointer_size                # pointers that fit in one block
    blocks = direct + per_block + per_block ** 2 + per_block ** 3
    return blocks * block_size

print(round(max_file_size() / 2**40, 3))                  # 4.004   (about 4 TiB with 4 KiB blocks)
print(12 * 4096, 12 * 4096 + 1024 * 4096)                 # 49152 4243456    (direct only = 48 KiB; with one indirect block = about 4 MiB)
```

Small files need only direct pointers (fast); huge files pay a few extra block reads. Modern systems use extent trees instead, which describe long runs compactly.

## 5. Real file systems from Python: stat, links, permissions

```python
import os, stat, tempfile

folder = tempfile.mkdtemp()
original = os.path.join(folder, "original.txt")
with open(original, "w") as f:
    f.write("some data")

info = os.stat(original)
print(info.st_size, info.st_nlink, stat.S_ISREG(info.st_mode))      # 9 1 True       (size, link count, "is a regular file")
print(info.st_ino > 0, info.st_blksize >= 512)                      # True True      (every file has an inode number)

# Hard link: a second name for the SAME inode
hard = os.path.join(folder, "hard.txt")
os.link(original, hard)
print(os.stat(original).st_ino == os.stat(hard).st_ino, os.stat(original).st_nlink)     # True 2
os.remove(original)                                                  # the data survives under the other name
print(open(hard).read(), os.stat(hard).st_nlink)                     # some data 1

# Symbolic link: a tiny file containing a PATH; it can dangle
sym = os.path.join(folder, "sym.txt")
os.symlink(hard, sym)
print(os.path.islink(sym), open(sym).read())                         # True some data
os.remove(hard)
print(os.path.islink(sym), os.path.exists(sym))                      # True False   (the link remains but points at nothing)
```

| | Hard link | Symbolic (soft) link |
|---|-----------|----------------------|
| What it is | another directory entry for the same inode | a small file that stores a path |
| Survives deleting the original name | **yes** | no (becomes dangling) |
| Crosses file systems | no | yes |
| Can point to a directory | normally no | yes |

### Permissions (the Unix mode bits)

Each file has an owner, a group and a **mode**: read/write/execute for owner, group and others, written in octal (`755`, `644`).

```text
rwxr-xr-x  = 111 101 101 = octal 755     owner can read/write/execute; group and others can read and execute
rw-r--r--  = 110 100 100 = octal 644     the usual setting for a data file
```

```python
script = os.path.join(folder, "run.sh")
with open(script, "w") as f:
    f.write("#!/bin/sh\necho ok\n")
os.chmod(script, 0o644)
print(oct(stat.S_IMODE(os.stat(script).st_mode)), os.access(script, os.X_OK))      # 0o644 False
os.chmod(script, 0o755)
print(oct(stat.S_IMODE(os.stat(script).st_mode)), os.access(script, os.X_OK))      # 0o755 True
print(stat.filemode(os.stat(script).st_mode))                                      # -rwxr-xr-x
```

For **directories** the bits mean: `r` = list names, `w` = create/delete entries, `x` = enter ("search") the directory.

Security habits: files holding secrets should be `0o600`; never `chmod 777`; create temp files with `tempfile` (unpredictable names, safe mode).

### Timestamps

```python
t = os.stat(script)
print(t.st_mtime >= t.st_ctime - 1, t.st_atime > 0)       # True True   (mtime = content modified, ctime = inode changed, atime = last accessed)
```

`ctime` is **not** creation time on Unix: it is the last metadata change (it moves when you `chmod` or rename).

## 6. Durability: why files are lost and how to prevent it

When you write, data first goes into the OS **page cache** in RAM; the kernel flushes it to disk later (seconds). A crash or power cut in between **loses the write**, and a crash in the middle of overwriting a file can leave a **half-written (corrupt) file**.

Tools:

- **`flush()`** pushes Python's buffer to the OS; **`os.fsync(fd)`** asks the OS to push to the disk and **wait** (slow, about milliseconds).
- **Atomic replace:** write the new content to a temporary file, `fsync` it, then **rename** it over the old one. `rename` is atomic on POSIX: readers see either the old file or the complete new one, never a mix.

```python
def atomic_write(path, data: bytes):
    directory = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=directory)        # a temp file in the SAME folder (rename must stay on one file system)
    try:
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(data)
            tmp.flush()
            os.fsync(tmp.fileno())                        # data is on disk before the swap
        os.replace(tmp_path, path)                        # atomic swap (also works on Windows)
    except BaseException:
        os.unlink(tmp_path)
        raise

config = os.path.join(folder, "config.json")
atomic_write(config, b'{"version": 1}')
atomic_write(config, b'{"version": 2}')
print(open(config, "rb").read())                          # b'{"version": 2}'
print(sorted(os.listdir(folder)))                         # ['config.json', 'run.sh', 'sym.txt']   (no temp files left behind)
```

How slow is a real `fsync`? Often 1-10 ms on SSDs, far more on hard disks, which is why databases batch commits (**group commit**).

```python
import time

path = os.path.join(folder, "fsync_test.bin")
with open(path, "wb") as f:
    t0 = time.perf_counter()
    for _ in range(20):
        f.write(b"x" * 1024); f.flush()
    buffered = time.perf_counter() - t0
    t0 = time.perf_counter()
    for _ in range(20):
        f.write(b"x" * 1024); f.flush(); os.fsync(f.fileno())
    synced = time.perf_counter() - t0
print(synced > buffered)                                  # True   (forcing to disk is much slower than leaving data in the page cache)
```

### Journaling: surviving a crash in the middle of an update

Creating a file touches several structures (the directory, the inode, the bitmap, the data). A crash after some but not all of those writes leaves the file system **inconsistent**. Older systems ran a slow full check (`fsck`) after a crash.

**Journaling** (ext4, NTFS, XFS, APFS) first writes a short **log** of the intended changes to a dedicated area, marks it committed, then applies them. After a crash the system **replays the committed log entries and discards incomplete ones**, restoring consistency in seconds. **Copy-on-write file systems** (ZFS, Btrfs, APFS) never overwrite live data and switch to the new version atomically.

```python
class JournaledStore:
    """A toy 'write-ahead log': intent is logged and committed BEFORE the real data changes."""
    def __init__(self):
        self.data, self.log = {}, []
    def put(self, key, value, crash_before_apply=False):
        self.log.append(("commit", key, value))          # 1) log the intent durably
        if crash_before_apply:
            return                                        # simulated power failure after the log write
        self.data[key] = value                            # 2) apply to the real structure
        self.log.clear()                                  # 3) checkpoint: the log entry is no longer needed
    def recover(self):
        for _, key, value in self.log:                    # replay committed but unapplied operations
            self.data[key] = value
        self.log.clear()

store = JournaledStore()
store.put("a", 1)
store.put("b", 2, crash_before_apply=True)                # crash!
print(store.data)                                         # {'a': 1}          (b is missing right after the crash)
store.recover()
print(store.data)                                         # {'a': 1, 'b': 2}  (the journal replay restored it)
```

Databases use the same **write-ahead logging** idea (see [databases](../../05-databases/README.md)).

## 7. I/O models: how a program waits for data

| Model | How it works | Example |
|-------|--------------|---------|
| **Blocking** | the call does not return until the data is ready; the thread sleeps | `f.read()`, `sock.recv()` |
| **Non-blocking** | the call returns immediately ("not ready yet"); you must try again | `sock.setblocking(False)` |
| **I/O multiplexing** | ask the OS to tell you **which of many descriptors are ready** (`select`, `poll`, `epoll`, `kqueue`) | `selectors`, event loops |
| **Asynchronous** | start the operation; the OS notifies you when it is **done** | Linux `io_uring`, Windows IOCP |

Event loops (`asyncio`, Node.js, nginx) are built on multiplexing: one thread watches thousands of sockets and handles whichever is ready.

```python
import selectors, socket

a, b = socket.socketpair()                                # two connected sockets (like a pipe)
sel = selectors.DefaultSelector()
sel.register(a, selectors.EVENT_READ)

print(sel.select(timeout=0.05))                           # []    nothing readable yet: select reports "not ready" instead of blocking forever
b.send(b"ping")
ready = sel.select(timeout=0.5)
print(len(ready), a.recv(10))                             # 1 b'ping'

a.setblocking(False)
try:
    a.recv(10)                                            # non-blocking read with no data
except BlockingIOError:
    print("would block")                                  # would block
sel.unregister(a); a.close(); b.close()
```

**Buffered vs unbuffered:** Python's `open()` buffers (about 8 KB) to cut system calls; `os.read/os.write` are direct. Use larger sequential reads, or `mmap` for random access to big files.

## 8. Choosing and inspecting file systems

| File system | Where | Notable |
|-------------|-------|---------|
| **ext4** | most Linux | journaling, extents, solid default |
| **XFS** | servers | great with huge files and parallel I/O |
| **Btrfs / ZFS** | NAS, advanced Linux/BSD | copy-on-write, snapshots, checksums |
| **NTFS** | Windows | journaling, ACL permissions |
| **APFS** | macOS/iOS | copy-on-write, snapshots, encryption |
| **FAT32 / exFAT** | USB sticks, cameras | simple, portable, no permissions, FAT32 max file 4 GB |
| **tmpfs / procfs** | RAM-based and virtual | `/tmp` in RAM; `/proc` shows live kernel info |

```bash
df -h .                 # space used and free on the file system holding the current folder
ls -li                  # -i shows inode numbers: names sharing a number are hard links
stat file.txt           # the full inode information
```

## 9. Two real-world examples

**Example 1: Log rotation.** `logrotate` renames `app.log` to `app.log.1` (a cheap directory operation: same inode, new name) and signals the program to reopen a fresh `app.log`. Until it does, the program keeps writing into the renamed file through its open descriptor.

**Example 2: Safe editors and package installs.** Editors and tools like `pip` write new content to a temp file and `rename` it into place, so a crash or full disk never leaves a half-written file. Backup tools (`rsync --link-dest`, Time Machine) use hard links so unchanged files in each snapshot cost no extra space.

## 10. Common mistakes

- Thinking a file's name is inside the file (it is in the directory).
- Using `open(path, "w")` to update an important file in place, then crashing mid-write (use atomic replace).
- Assuming `write()` means the data is on disk (it is in the page cache until flushed or `fsync`ed).
- Forgetting that deleting a file others still hold open does not free the space.
- Setting `chmod 777` instead of fixing the owner or group.
- Putting the temp file on a different file system than the target (then `rename` is not atomic).
- Ignoring `ENOSPC` (disk full) and `EMFILE` (too many open files): always close files, preferably with `with`.

## 11. Practice

1. In the `TinyFS` model, a 100-byte file needs how many 16-byte blocks? How many bytes are wasted (internal fragmentation)?
2. Why does a hard link not take extra disk space for the data?
3. After `os.symlink(a, b)` and then deleting `a`, what does `os.path.exists(b)` return, and why?
4. What octal mode is `rw-r-----`?
5. Why is `os.replace` (rename) used for atomic updates, and why must the temp file be in the same directory?
6. What problem does journaling solve?
7. Which I/O model lets one thread serve 10 000 sockets, and which system calls provide it?

<details>
<summary>Solutions</summary>

1. `ceil(100 / 16) = 7` blocks, `7 * 16 - 100 = 12` bytes wasted.
   ```python
   fs2 = TinyFS(); fs2.write("/f", b"z" * 100)
   inode2 = fs2.inodes[fs2._lookup("/f")]
   print(len(inode2.blocks), len(inode2.blocks) * BLOCK_SIZE - inode2.size)      # 7 12
   ```
2. A hard link is just another directory entry pointing to the same inode, which owns the blocks; only a name is added.
3. `False`: the symlink stores a path; after the target is gone the path resolves to nothing (a dangling link).
4. `640` (`rw-` = 6, `r--` = 4, `---` = 0).
   ```python
   print(oct(0b110_100_000))                                   # 0o640
   ```
5. Rename is atomic on POSIX: observers see the old or the new file only. It is atomic only within one file system, and the same directory guarantees that.
6. Crashes between related metadata updates leaving the file system inconsistent: the journal lets recovery replay or discard whole operations quickly.
7. I/O multiplexing (an event loop) using `epoll` (Linux), `kqueue` (BSD/macOS) or `select`/`poll`; `io_uring` offers true asynchronous I/O on Linux.

</details>

## 12. Check yourself

1. What is stored in an inode, and what is not?
2. What happens to a file's data when you delete its last name?
3. Difference between hard and symbolic links?
4. Why can a crash lose data you "wrote", and how do you prevent it?
5. What does a journal do after a crash?
6. What is the difference between blocking, non-blocking and multiplexed I/O?

<details>
<summary>Answers</summary>

1. Metadata (size, owner, permissions, timestamps, link count, block locations); not the file's name (that is in the directory).
2. With the link count at zero and no open handles, the inode and its blocks are freed.
3. A hard link is another name for the same inode (same file system, survives deletion of the other name); a symlink is a file holding a path (can cross file systems, can dangle).
4. Writes sit in the page cache until flushed; use `flush` + `os.fsync`, and atomic replace (temp file + rename) for whole-file updates.
5. Replays committed log entries and discards incomplete ones, restoring consistency without a full scan.
6. Blocking waits until ready; non-blocking returns immediately with "not ready"; multiplexing waits on many descriptors at once and reports which are ready.

</details>

[Back to file systems and I/O](README.md)
