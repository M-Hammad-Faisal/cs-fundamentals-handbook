# Boot and Startup: One-Page Summary

## Quick reference

| Stage | Does | Examples |
|-------|------|----------|
| Firmware | POST, find a boot device | BIOS, UEFI |
| Bootloader | pick an OS, load kernel and initramfs | GRUB, Windows Boot Manager, systemd-boot |
| Kernel | memory, drivers, scheduler, mount root | Linux, NT, XNU |
| Init (PID 1) | start services in dependency order | systemd, launchd |

## Questions worth remembering

- **List the stages from power-on to a login prompt.** Firmware (POST, find boot device), bootloader, kernel (and initramfs), init/service manager (PID 1), services and login.
- **What is in the first 512 bytes of a BIOS boot disk?** The MBR: 446 bytes of boot code, a 64-byte table of four partition entries and the 2-byte `55 AA` signature.
- **How do UEFI and GPT differ from BIOS and MBR?** UEFI runs 32/64-bit firmware that reads files from a FAT32 EFI System Partition and supports Secure Boot; GPT supports disks over 2 TiB, up to 128 partitions, checksums and a backup table; BIOS runs the 512-byte MBR code and MBR is limited to 2 TiB and four primary partitions.
- **What is the initramfs for?** A small temporary root file system in RAM containing the drivers and scripts needed to find, unlock and mount the real root file system.
- **What does PID 1 do, and how does systemd start things faster than sequential scripts?** It is the first user process; it starts all services and adopts orphans. systemd builds a dependency graph and starts independent units in parallel.
- **How does measured boot detect a tampered bootloader?** Each stage's hash is folded into a TPM register with `H(old || H(component))`; changing any component (or the order) changes the final value, which no longer matches the expected fingerprint.

Practice problems with solutions are in the **Practice** section of each lesson.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [The Boot Process and Bootloaders](01-boot-process-and-bootloaders.md)
