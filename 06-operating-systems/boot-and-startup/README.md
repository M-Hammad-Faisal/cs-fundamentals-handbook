# Boot and Startup

What happens between pressing the power button and a login prompt.

## Detailed lessons

- [The boot process and bootloaders](01-boot-process-and-bootloaders.md): firmware (BIOS/UEFI), MBR and GPT (build and parse real ones), bootloaders, the kernel and initramfs, init and systemd (as a dependency graph), Secure Boot and measured boot, troubleshooting

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Stage | Does | Examples |
|-------|------|----------|
| Firmware | POST, find a boot device | BIOS, UEFI |
| Bootloader | pick an OS, load kernel and initramfs | GRUB, Windows Boot Manager, systemd-boot |
| Kernel | memory, drivers, scheduler, mount root | Linux, NT, XNU |
| Init (PID 1) | start services in dependency order | systemd, launchd |

Back to [operating systems](../README.md).
