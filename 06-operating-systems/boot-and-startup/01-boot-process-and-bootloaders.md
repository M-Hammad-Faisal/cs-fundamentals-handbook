# The Boot Process and Bootloaders

**Prerequisites:** [what is an operating system](../00-what-is-an-operating-system.md), [binary and hexadecimal](../../00-foundations/computer-basics/binary-and-data-representation.md), [how a computer runs programs](../../00-foundations/computer-basics/how-computers-work.md), [file systems](../file-systems-io/01-file-systems-in-depth.md). **You will learn:** exactly what happens between pressing the power button and seeing a login screen: **firmware (BIOS/UEFI)**, the **power-on self-test**, the **bootloader**, the **kernel**, **`initramfs`** and **`init`/`systemd`**; how disks are described by **MBR** and **GPT** partition tables (you will build and parse real ones from bytes); how **Secure Boot** and **measured boot** create a chain of trust (simulated with hashes); and how to **troubleshoot** a machine that will not start.

## 1. The chicken-and-egg problem

An operating system lives on disk, but the CPU can only run programs that are in memory, and memory is empty at power-on (RAM forgets everything when power is lost). Something must **bootstrap** the system: a tiny program, stored in non-volatile memory, that loads a slightly bigger program, which loads a bigger one, until the whole OS is running. ("Booting" comes from "pulling yourself up by your bootstraps".)

```text
power on
  -> FIRMWARE (BIOS or UEFI, in flash memory on the motherboard)
       tests hardware (POST), initializes devices, finds a boot disk
  -> BOOTLOADER (GRUB, Windows Boot Manager, systemd-boot, macOS boot.efi)
       lets you choose an OS, loads the kernel (and initramfs) into RAM
  -> KERNEL (Linux, Windows NT, XNU)
       sets up memory management, drivers, scheduler; mounts the root file system
  -> INIT / SERVICE MANAGER (PID 1: systemd, launchd, Windows Session Manager)
       starts services, networking, login screen, your desktop or shell
```

Each stage hands control to the next and trusts it, which is why booting is a security-critical path (section 7).

## 2. Stage 1: firmware

When the CPU is reset it starts executing at a **fixed address** (on x86 the *reset vector* near the top of the first megabyte, today mapped to the firmware chip). The firmware does:

1. **POST (power-on self-test):** checks CPU, RAM and essential hardware; a failure gives **beep codes** or LEDs (the screen is not even initialized yet).
2. **Initializes hardware:** memory controller, PCI buses, keyboard, display, storage controllers.
3. **Finds a boot device** using the configured boot order (disk, USB, network/PXE) and **runs the first code it finds there**.

| | **BIOS** (legacy, 1980s) | **UEFI** (modern, 2010s) |
|---|--------------------------|--------------------------|
| Mode | 16-bit real mode | 32/64-bit, with a driver model |
| Reads | the **first 512-byte sector (MBR)** of the disk | files from a small **EFI System Partition (ESP, FAT32)**: `\EFI\BOOT\BOOTX64.EFI` |
| Partition tables | MBR (disks up to 2 TiB, 4 primary partitions) | **GPT** (huge disks, 128 partitions by default) |
| Security | none | **Secure Boot** (signature checks) |
| Settings | cryptic text menu | graphical, network capable, boot entries stored in NVRAM |
| Modern PCs | emulated as "CSM/legacy mode" | the default |

## 3. Stage 2: disks, the MBR and the bootloader

### The Master Boot Record (MBR)

On a BIOS system, the firmware loads **sector 0** (512 bytes) of the boot disk into memory at address `0x7C00` and jumps to it. Those 512 bytes are laid out like this:

```text
offset 0   - 445   446 bytes   boot code (stage-1 bootloader, a tiny machine-code program)
offset 446 - 509    64 bytes   partition table: four 16-byte entries
offset 510 - 511     2 bytes   boot signature 0x55 0xAA (BIOS refuses sectors without it)
```

Each 16-byte **partition entry**:

```text
byte 0      boot flag: 0x80 = active (bootable), 0x00 = not
bytes 1-3   CHS address of the first sector (obsolete)
byte 4      partition type: 0x83 Linux, 0x07 NTFS/exFAT, 0x0B/0x0C FAT32, 0x82 swap, 0xEE GPT protective, 0x05 extended
bytes 5-7   CHS of the last sector (obsolete)
bytes 8-11  LBA of the first sector (little-endian, 32 bits)
bytes 12-15 number of sectors (little-endian, 32 bits)
```

Let us build a genuine MBR from scratch and parse it back:

```python
import struct

SECTOR = 512

def build_mbr(partitions, boot_code=b""):
    """partitions: list of (bootable, type_code, first_lba, sector_count), at most 4."""
    code = boot_code.ljust(446, b"\x00")
    table = b""
    for bootable, ptype, lba, count in partitions:
        # status, CHS start (3 bytes, unused), type, CHS end (3 bytes, unused), LBA start, sector count
        table += struct.pack("<B3sB3sII", 0x80 if bootable else 0, b"\x00\x00\x00", ptype, b"\x00\x00\x00", lba, count)
    table = table.ljust(64, b"\x00")
    return code + table + b"\x55\xAA"

def parse_mbr(sector):
    if len(sector) != SECTOR or sector[510:512] != b"\x55\xAA":
        raise ValueError("not a valid MBR (missing 0x55AA signature)")
    names = {0x83: "Linux", 0x82: "Linux swap", 0x07: "NTFS/exFAT", 0x0B: "FAT32", 0x0C: "FAT32 (LBA)", 0xEE: "GPT protective", 0x00: "empty"}
    entries = []
    for i in range(4):
        status, _, ptype, _, lba, count = struct.unpack("<B3sB3sII", sector[446 + i * 16: 446 + (i + 1) * 16])
        if ptype:
            entries.append({"index": i + 1, "bootable": status == 0x80, "type": names.get(ptype, hex(ptype)),
                            "start_sector": lba, "sectors": count, "size_mib": count * SECTOR / 2**20})
    return entries

mbr = build_mbr([(True, 0x83, 2048, 4_194_304),            # a 2 GiB Linux partition starting at 1 MiB (sector 2048: the usual alignment)
                 (False, 0x82, 4_196_352, 1_048_576),      # 512 MiB swap
                 (False, 0x07, 5_244_928, 8_388_608)])      # 4 GiB NTFS data partition
print(len(mbr), mbr[-2:].hex())                             # 512 55aa
for e in parse_mbr(mbr):
    print(e)
# {'index': 1, 'bootable': True, 'type': 'Linux', 'start_sector': 2048, 'sectors': 4194304, 'size_mib': 2048.0}
# {'index': 2, 'bootable': False, 'type': 'Linux swap', 'start_sector': 4196352, 'sectors': 1048576, 'size_mib': 512.0}
# {'index': 3, 'bootable': False, 'type': 'NTFS/exFAT', 'start_sector': 5244928, 'sectors': 8388608, 'size_mib': 4096.0}

try:
    parse_mbr(b"\x00" * 512)
except ValueError as e:
    print(e)                                                # not a valid MBR (missing 0x55AA signature)
```

**The limits that killed MBR:** 32-bit sector numbers with 512-byte sectors cap a disk at `2^32 * 512` bytes:

```python
print(2**32 * 512 / 2**40, "TiB maximum disk size with MBR")        # 2.0 TiB maximum disk size with MBR
```

and only four primary partitions (people used an "extended" partition as a workaround).

You can look at the real MBR of a disk image or device (on Linux, needs privileges): `sudo dd if=/dev/sda bs=512 count=1 | xxd | tail -5` ends with `55aa`.

### Why 446 bytes of code are not enough: multi-stage bootloaders

446 bytes cannot read a file system or show a menu. So the bootloader is split:

1. **Stage 1** (in the MBR): just knows where on disk to find stage 1.5/2 and loads it using BIOS disk calls.
2. **Stage 2** (e.g. GRUB's `core.img`, a few hundred KB in the gap before the first partition): understands file systems, displays the **boot menu**, reads its config, loads the **kernel** and the **initramfs** into RAM, passes it **kernel command-line parameters** (`root=/dev/sda1 quiet`) and jumps to the kernel.

### GPT and UEFI

**GPT (GUID Partition Table)** replaces MBR: 64-bit sector addresses (disks up to 8 ZiB), up to 128 partitions, **a backup copy at the end of the disk**, and **CRC32 checksums** so corruption is detected. Layout:

```text
LBA 0    protective MBR (a single 0xEE partition so old tools do not think the disk is empty)
LBA 1    GPT header: signature "EFI PART", revision, header size, CRC32, current/backup LBA, first/last usable LBA, disk GUID, partition-entries start, count, size and entries CRC
LBA 2+   partition entries (128 bytes each: type GUID, unique GUID, first LBA, last LBA, attributes, name in UTF-16)
...      partitions ...
last     backup partition entries and a backup GPT header
```

```python
import zlib, uuid

def build_gpt_header(entries_crc, num_entries=128, entry_size=128, total_sectors=2_097_152):
    header = struct.pack("<8sIIIIQQQQ16sQIII",
                         b"EFI PART", 0x00010000, 92, 0, 0,                 # signature, revision 1.0, header size 92, CRC placeholder, reserved
                         1, total_sectors - 1,                               # this header's LBA, backup header's LBA (last sector)
                         34, total_sectors - 34,                             # first and last usable LBA
                         uuid.UUID("12345678-1234-5678-1234-567812345678").bytes_le,      # disk GUID
                         2, num_entries, entry_size, entries_crc)            # where entries start, how many, each size, CRC of the entries
    crc = zlib.crc32(header) & 0xFFFFFFFF                                    # CRC is computed with the CRC field zeroed
    return header[:16] + struct.pack("<I", crc) + header[20:]

def check_gpt_header(raw):
    signature = raw[:8]
    stored = struct.unpack("<I", raw[16:20])[0]
    zeroed = raw[:16] + b"\x00\x00\x00\x00" + raw[20:92]
    return {"signature": signature.decode(), "crc_valid": (zlib.crc32(zeroed) & 0xFFFFFFFF) == stored,
            "usable_lba": struct.unpack("<QQ", raw[40:56])}

header = build_gpt_header(entries_crc=0xDEADBEEF)
print(len(header), check_gpt_header(header))
# 92 {'signature': 'EFI PART', 'crc_valid': True, 'usable_lba': (34, 2097118)}

damaged = bytearray(header); damaged[48] ^= 0x01                              # flip one bit in the first-usable-LBA field
print(check_gpt_header(bytes(damaged))["crc_valid"])                          # False   corruption detected: firmware falls back to the backup header
```

On a UEFI machine there is **no 446-byte limit**: the firmware itself understands FAT32, reads the **EFI System Partition**, and runs a normal program (`BOOTX64.EFI` or `grubx64.efi`) written in C. Boot entries ("Ubuntu", "Windows Boot Manager") are stored in firmware **NVRAM**; `efibootmgr -v` lists them on Linux.

## 4. Stage 3: the kernel starts

The bootloader leaves the kernel image (compressed, e.g. `vmlinuz`) and the **initramfs** in memory. The kernel then:

1. **Decompresses itself** and switches the CPU to its full operating mode (64-bit, paging on): [virtual memory](../memory-virtual-memory/01-paging-and-address-translation.md) comes alive.
2. Initializes **interrupts, the scheduler, memory management**, detects CPUs and devices, parses the **command line**.
3. Mounts the **initramfs** (a small temporary root file system in RAM) and runs `/init` in it. The initramfs holds the **drivers needed to reach the real root disk** (an NVMe controller, RAID, LVM, disk encryption: prompting for the passphrase happens here). Without it, the kernel could not read the disk that contains the drivers for reading the disk.
4. **Switches root** to the real root file system (`pivot_root`/`switch_root`) and executes the first user-space program as **PID 1**.

You can see the kernel command line and boot messages on Linux:

```python
import os, platform

if os.path.exists("/proc/cmdline"):
    print(open("/proc/cmdline").read().strip())             # e.g. BOOT_IMAGE=/vmlinuz root=UUID=... ro quiet splash
else:
    print(platform.system(), platform.release()[:20])        # Darwin 27.2.0   (macOS: `sysctl kern.bootargs`, `log show --boot`)
```

On Linux: `dmesg | less` (kernel ring buffer), `journalctl -b` (everything from this boot), `systemd-analyze blame` (which services slowed startup), `systemd-analyze critical-chain`.

## 5. Stage 4: init and the service manager

The kernel starts exactly one user program, **PID 1**, which launches everything else and adopts orphaned processes ([processes in practice](../processes-threads/01-processes-in-practice.md)). Modern Linux uses **systemd**; macOS uses **launchd**; older Unix used **SysV init** scripts.

**systemd** reads **unit files** describing services and their **dependencies**, builds a dependency graph and starts independent units **in parallel**: a [topological order](../../02-data-structures/graphs/02-graph-algorithms.md) over a DAG, exactly the algorithm you implemented. A simplified model:

```python
from collections import deque

UNITS = {                                                   # unit -> units it must wait for
    "local-fs.target": [],
    "network.target": ["local-fs.target"],
    "sshd.service": ["network.target"],
    "database.service": ["local-fs.target", "network.target"],
    "webapp.service": ["database.service", "network.target"],
    "multi-user.target": ["sshd.service", "webapp.service"],
}

def startup_waves(units):
    """Group units into parallel 'waves': everything in a wave can start together."""
    waiting = {u: set(deps) for u, deps in units.items()}
    started, waves = set(), []
    while waiting:
        ready = sorted(u for u, deps in waiting.items() if deps <= started)
        if not ready:
            raise ValueError("dependency cycle: boot would hang")
        waves.append(ready)
        started.update(ready)
        for u in ready:
            del waiting[u]
    return waves

for i, wave in enumerate(startup_waves(UNITS), 1):
    print(f"wave {i}: {wave}")
# wave 1: ['local-fs.target']
# wave 2: ['network.target']
# wave 3: ['database.service', 'sshd.service']
# wave 4: ['webapp.service']
# wave 5: ['multi-user.target']
```

Both `database.service` and `sshd.service` start at the same time in wave 3, which is why systemd boots faster than strictly sequential init scripts. When the dependencies converge on **`multi-user.target`** (or `graphical.target` for a desktop), the system is "up". A **runlevel/target** is simply "which set of services to reach".

Useful commands: `systemctl status ssh`, `systemctl list-units --failed`, `systemctl enable --now nginx`, `journalctl -u myapp -f`, `systemctl get-default`.

## 6. Other platforms and special cases

| Situation | What differs |
|-----------|--------------|
| **macOS (Apple silicon)** | a ROM (**iBoot**) verifies and loads the kernel from a signed volume; no user-configurable bootloader menu |
| **Windows** | UEFI loads **Windows Boot Manager**, which loads `winload`, the NT kernel and the Session Manager (`smss.exe`) |
| **Network boot (PXE)** | firmware downloads a boot program over DHCP/TFTP: used to install or run diskless machines |
| **Cloud virtual machines** | the hypervisor provides virtual UEFI/BIOS; **cloud-init** configures the instance at first boot (hostname, SSH keys) |
| **Containers** | **no boot at all**: a container shares the host kernel and starts directly at its entry process ([containers lesson](../containers/01-containers-and-namespaces.md)) |
| **Embedded and microcontrollers** | often the CPU jumps straight to code in on-chip flash; a small bootloader may allow firmware updates |
| **Dual boot** | the bootloader (GRUB, rEFInd) lists several operating systems and chain-loads the one you choose |

## 7. Secure Boot and measured boot: a chain of trust

If an attacker replaces the bootloader or kernel with malware (a **bootkit**), it runs *before* the operating system and its antivirus, with total control. Two defenses:

**Secure Boot (UEFI):** each stage **verifies a digital signature** on the next stage before running it. The firmware trusts a key database (Microsoft's, the OEM's, or your own); the bootloader verifies the kernel; the kernel verifies its modules. An unsigned or tampered component is refused.

**Measured boot (TPM):** each stage **hashes** the next stage and records the measurement in a tamper-resistant chip, the **TPM**, by **extending** a **Platform Configuration Register (PCR)**: `PCR_new = H(PCR_old || H(component))`. A PCR can only be extended, never set, so its final value is a fingerprint of the *exact sequence* of everything that booted. Disk-encryption keys can be released only when the PCRs match a known-good value, and a remote server can ask the machine to prove its boot state (**attestation**).

```python
import hashlib

def extend(pcr: bytes, component: bytes) -> bytes:
    return hashlib.sha256(pcr + hashlib.sha256(component).digest()).digest()      # PCR_new = H(PCR_old || H(component))

def measured_boot(components):
    pcr = b"\x00" * 32                                       # PCRs start at all zeros on power-up
    for c in components:
        pcr = extend(pcr, c)
    return pcr.hex()

good = [b"firmware v1.2", b"bootloader grub-2.12", b"kernel 6.8.0", b"initramfs 6.8.0"]
tampered = [b"firmware v1.2", b"bootloader grub-2.12 + bootkit", b"kernel 6.8.0", b"initramfs 6.8.0"]
reordered = [b"bootloader grub-2.12", b"firmware v1.2", b"kernel 6.8.0", b"initramfs 6.8.0"]

reference = measured_boot(good)
print(reference[:16])                                        # 895ce33b6b540d1e   (a fixed fingerprint of this exact boot chain)
print(measured_boot(good) == reference, measured_boot(tampered) == reference, measured_boot(reordered) == reference)
# True False False       any change, even the ORDER of components, changes the final PCR value
```

(A real TPM has several PCRs, uses SHA-256 or SHA-1 banks, and the firmware reports each measurement in an event log.) Secure Boot **blocks** bad code; measured boot **records** what ran so it can be **checked**. They complement each other.

## 8. Troubleshooting a machine that will not boot

Follow the stages in order and ask "which stage was the last to succeed?":

| Symptom | Likely stage | Things to try |
|---------|--------------|---------------|
| No display, beeps or LEDs | firmware/POST | reseat RAM, remove peripherals, reset CMOS/firmware |
| "No bootable device" / "Missing operating system" | firmware or bootloader | boot order, boot USB, repair the bootloader (`grub-install`, `bcdboot`), check the ESP exists |
| GRUB prompt (`grub>` or `grub rescue>`) | bootloader lost its config or partition | `ls`, `set root=...`, boot manually, then `update-grub` |
| "Kernel panic: unable to mount root fs" | kernel/initramfs | wrong `root=`, missing driver in initramfs, regenerate it (`update-initramfs -u`) |
| Hangs on a service or very slow startup | init system | `systemd-analyze blame`, `journalctl -b -p err`, boot with `systemd.unit=rescue.target` |
| Login loop, desktop crashes | user space | check `.profile`/session logs, try another user |
| Disk errors | storage | `fsck` from a rescue USB, check SMART health |

**Rescue tools:** a live USB (boot a working system from a stick), single-user/rescue mode, the kernel option `init=/bin/bash` (last resort), `chroot` into the broken install from the live system to repair it.

## 9. Two real-world examples

**Example 1: A server that would not boot after an update.** After `apt upgrade` installed a new kernel, the machine dropped to `initramfs>` because the new initramfs lacked the RAID driver. The fix, from a rescue shell: boot the old kernel entry from GRUB, run `update-initramfs -u -k all`, reboot. Knowing that the **initramfs holds the drivers for the root disk** pointed straight to the cause.

**Example 2: Why BitLocker (or LUKS with a TPM) asks for a recovery key after a firmware update.** The update changed a measured component, so the PCR values no longer match the ones the disk key was sealed to; the TPM refuses to release the key, treating the changed boot chain as potentially hostile. That is **measured boot working as designed**.

## 10. Common mistakes

- Thinking the OS "starts the computer": firmware and the bootloader run first.
- Mixing up BIOS/MBR and UEFI/GPT tooling (installing a legacy bootloader on a UEFI-only disk).
- Deleting or reformatting the **EFI System Partition** (or forgetting to mount it when repairing).
- Editing `/etc/fstab` or the bootloader config without a rescue plan.
- Forgetting to regenerate the **initramfs** after changing storage, encryption or RAID setup.
- Disabling Secure Boot permanently instead of enrolling the right keys.
- Cloning an MBR disk to a smaller or larger one without fixing the partition table and bootloader.

## 11. Practice

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
2. ```python
   one = build_mbr([(True, 0x0C, 2048, 1_048_576)])
   print(parse_mbr(one))
   # [{'index': 1, 'bootable': True, 'type': 'FAT32 (LBA)', 'start_sector': 2048, 'sectors': 1048576, 'size_mib': 512.0}]
   ```
3. `2^32 * 512` bytes is 2 TiB; with 4096-byte sectors it is 16 TiB.
4. If the primary header or table at the start of the disk is damaged, the firmware or tools can restore from the backup copy and the checksums tell them which copy is good.
5. Wave 4 would hold `sshd.service` together with `webapp.service`, after `database.service` (wave 3):
   ```python
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

## 12. Check yourself

1. List the stages from power-on to a login prompt.
2. What is in the first 512 bytes of a BIOS boot disk?
3. How do UEFI and GPT differ from BIOS and MBR?
4. What is the initramfs for?
5. What does PID 1 do, and how does systemd start things faster than sequential scripts?
6. How does measured boot detect a tampered bootloader?

<details>
<summary>Answers</summary>

1. Firmware (POST, find boot device), bootloader, kernel (and initramfs), init/service manager (PID 1), services and login.
2. The MBR: 446 bytes of boot code, a 64-byte table of four partition entries and the 2-byte `55 AA` signature.
3. UEFI runs 32/64-bit firmware that reads files from a FAT32 EFI System Partition and supports Secure Boot; GPT supports disks over 2 TiB, up to 128 partitions, checksums and a backup table; BIOS runs the 512-byte MBR code and MBR is limited to 2 TiB and four primary partitions.
4. A small temporary root file system in RAM containing the drivers and scripts needed to find, unlock and mount the real root file system.
5. It is the first user process; it starts all services and adopts orphans. systemd builds a dependency graph and starts independent units in parallel.
6. Each stage's hash is folded into a TPM register with `H(old || H(component))`; changing any component (or the order) changes the final value, which no longer matches the expected fingerprint.

</details>

[Back to operating systems](../README.md)
