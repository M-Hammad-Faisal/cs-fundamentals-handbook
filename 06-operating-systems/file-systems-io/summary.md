# File Systems and I/O: One-Page Summary

- **Layers:** app, VFS, page cache, block layer, device.
- **Inode** = metadata + block pointers; **directory** = name to inode map. **Hard link** = extra name for an inode; **symlink** = stored path (can dangle). Space is freed at link count 0 and no open handles.
- **Allocation:** contiguous, linked, indexed (inode), extents.
- **Crash safety:** journaling (log then apply) or copy-on-write (ZFS, Btrfs, APFS).
- **Durability:** `write` goes to the page cache; `fsync` forces it to disk. Safe overwrite = temp file, `fsync`, atomic `os.replace`.
- **File descriptors:** 0 stdin, 1 stdout, 2 stderr; offset lives in the open file description; leaks cause "Too many open files".
- **I/O models:** blocking, non-blocking, multiplexing (`select`/`epoll`/`kqueue`), async (`io_uring`/IOCP). Event loops solve C10K.
- **Performance:** buffer I/O, stream big files, prefer sequential access; databases use write-ahead logs.
- **Pitfalls:** deleted-but-open files, check-then-open races, `/tmp` symlink attacks, assuming NFS behaves like local disk.

[Lesson](README.md) · [Exercises](exercises.md)
