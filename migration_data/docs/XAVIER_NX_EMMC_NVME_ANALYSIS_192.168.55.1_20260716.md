# Xavier NX eMMC + NVMe vehicle analysis

Date: 2026-07-16  
Target: `192.168.55.1`  
Hostname: `sovereigntys`

## Conclusion

This vehicle is not an SD-root Xavier NX. It has a 16 GB on-module eMMC and a 256 GB-class NVMe SSD. Boot starts from the JetPack 4-era eMMC configuration and the custom `setssdroot.service` switches the live root filesystem to the NVMe SSD.

## Observed hardware and software

```text
Model: NVIDIA Jetson Xavier NX Developer Kit
Kernel: 4.9.140-tegra
L4T: R32.4.3
nvidia-l4t-core: 32.4.3-20200625213407
nvidia-l4t-bootloader: 32.4.3-20200625213407
```

Internal eMMC:

```text
Device: /dev/mmcblk0
Type: MMC
Name: DG4016
Capacity: 14.7 GiB (16 GB nominal)
APP: /dev/mmcblk0p1, 14 GiB
```

External NVMe:

```text
Device: /dev/nvme0n1
Capacity: 238.5 GiB (256 GB nominal)
Live root: /dev/nvme0n1p1
Root size: 238 GiB
Used: 22 GiB
Available: 207 GiB
```

No SD device was detected.

## Current boot chain

```text
QSPI / boot firmware
  -> eMMC boot partitions and eMMC APP
  -> kernel command line root=/dev/mmcblk0p1
  -> setssdroot.service
  -> /sbin/setssdroot.sh
  -> systemctl switch-root /nvmeroot
  -> live root /dev/nvme0n1p1
```

The active service is:

```text
setssdroot.service enabled, active, exited
Description: Change rootfs to SSD in M.2 key M slot (nvme0n1p1)
```

Its script mounts `/dev/nvme0n1p1` on `/nvmeroot` and calls `systemctl switch-root`. This is a custom legacy root-on-NVMe mechanism, not the preferred R35.6.4 initrd-flash layout.

## Hardware configuration that must be recreated

The current extlinux default is:

```text
DEFAULT FE-PI Audio Z V2
FDT /boot/tegra194-p3668-all-p3509-0000-fe-pi-audio-z-v2.dtb
```

The R32 binary DTB must not be copied directly into R35.6.4 because the kernel/device-tree generation changes from the 4.9/R32 stack to the 5.10/R35 stack. Recreate the FE-PI Audio Z V2 configuration from its overlay/source or through the R35 Jetson-IO flow and revalidate ALSA.

## Migration decision

Do not use the SD-model QSPI-only wrapper for this vehicle. Do not attempt an in-place `apt` release upgrade from R32 to R35.

Recommended target:

```text
Board config: jetson-xavier-nx-devkit-emmc
Release: JetPack 5.1.6 / L4T R35.6.4
Internal media: eMMC boot support / recovery root
Primary root: NVMe using official l4t_initrd_flash layout and PARTUUID
Boot order overlay: BootOrderNvme.dtbo
```

The legacy `setssdroot.service` and `/sbin/setssdroot.sh` should not be migrated. R35.6.4 should be flashed with the official external-root mechanism so that the boot configuration directly selects the NVMe root.

Provisional command shape, to be finalized after backup and NVMe partition sizing:

```bash
sudo ADDITIONAL_DTB_OVERLAY_OPT="BootOrderNvme.dtbo" \
  ./tools/kernel_flash/l4t_initrd_flash.sh \
  --external-device nvme0n1p1 \
  -c ./tools/kernel_flash/flash_l4t_external.xml \
  --network usb0 \
  --showlogs \
  jetson-xavier-nx-devkit-emmc \
  external
```

Because `--external-only` is intentionally omitted, the official tool prepares both the internal and external sides of the boot configuration. The external XML and APP size must be adjusted for the 256 GB SSD before executing this command.

## Required backup before flashing

1. Image the complete eMMC, including its GPT and boot-related partitions.
2. Image or file-back up the complete NVMe root.
3. Archive `/boot`, `/etc`, `/home`, package inventories, service definitions, udev rules, hardware settings and course data.
4. Preserve `setssdroot.service`, `/sbin/setssdroot.sh`, `/etc/setssdroot.conf`, and the current extlinux/DTB only as migration evidence.
5. Record NVMe model, serial, sector count and health.
6. Recreate and validate FE-PI audio, camera, SPI, I2C, PWM/buzzer, motors and Jupyter after R35.6.4 installation.

## Status

Analysis complete. No flash, package installation, service change, or reboot was performed.
