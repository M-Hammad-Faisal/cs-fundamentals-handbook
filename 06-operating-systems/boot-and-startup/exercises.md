# Boot and Startup: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## The Boot Process and Bootloaders

1. How many bytes of the MBR hold the partition table, and how many entries fit? Why does the table end with `55 AA`?
2. Build an MBR with one bootable FAT32-LBA partition (type `0x0C`) starting at sector 2048 with 1,048,576 sectors, then parse it and report its size in MiB.
3. How large can a partition be if its sector count is a 32-bit number and the sector size is 512 bytes? What about 4096-byte sectors?
4. Why does GPT store a backup header at the end of the disk?
5. Give the boot order of services for `UNITS` if `sshd.service` also required `database.service`.
6. What is the difference between Secure Boot and measured boot?
7. A VM boots straight to a shell, with no bootloader menu. Name two reasons that can be true.
8. Why can the kernel not simply mount the root file system without an initramfs on some systems?

<details>
<summary>Solutions</summary>

1. 64 bytes, four 16-byte entries. The two-byte signature `0x55AA` marks a sector as bootable: BIOS refuses to run a first sector without it, a cheap sanity check against random data.
2. ```python no-run
   one = build_mbr([(True, 0x0C, 2048, 1_048_576)])
   print(parse_mbr(one))
   # [{'index': 1, 'bootable': True, 'type': 'FAT32 (LBA)', 'start_sector': 2048, 'sectors': 1048576, 'size_mib': 512.0}]
   ```
3. `2^32 * 512` bytes is 2 TiB; with 4096-byte sectors it is 16 TiB.
4. If the primary header or table at the start of the disk is damaged, the firmware or tools can restore from the backup copy and the checksums tell them which copy is good.
5. Wave 4 would hold `sshd.service` together with `webapp.service`, after `database.service` (wave 3):
   ```python no-run
   units2 = dict(UNITS); units2["sshd.service"] = ["network.target", "database.service"]
   for i, wave in enumerate(startup_waves(units2), 1): print(i, wave)
   # 1 ['local-fs.target']
   # 2 ['network.target']
   # 3 ['database.service']
   # 4 ['sshd.service', 'webapp.service']
   # 5 ['multi-user.target']
   ```
6. Secure Boot **prevents** unsigned or tampered code from running by verifying signatures at each stage; measured boot **records** hashes of each stage into the TPM so a later check (disk-key release, remote attestation) can detect what ran.
7. The VM may use **direct kernel boot** (the hypervisor loads the kernel and initramfs itself and skips firmware and bootloader), or the bootloader's menu timeout is 0 / hidden. Containers skip booting entirely.
8. The drivers and tools needed to reach the root disk (a storage controller, RAID, LVM, encryption) may live *on* that disk; the initramfs, loaded into RAM by the bootloader, carries them so the kernel can reach the real root file system.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [The Boot Process and Bootloaders](01-boot-process-and-bootloaders.md)
