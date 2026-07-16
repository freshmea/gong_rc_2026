# Xavier NX QSPI pilot from Ubuntu 20.04 WSL

Date: 2026-07-16  
Windows host WSL distribution: `Ubuntu-20.04-Jetson`  
WSL user: `aa`  
Workspace: `/home/aa/jetson-r35.6.4`

## Purpose

Prepare a reproducible L4T R35.6.4 QSPI-only flashing environment on the classroom Windows notebook and run the first Xavier NX Developer Kit pilot without writing a microSD card.

## Host baseline

```text
Architecture: x86_64
Distribution: Ubuntu 20.04.4 LTS
Initial available space: about 917 GB
usbipd-win: 5.3.0
WSL distribution name: Ubuntu-20.04-Jetson
```

The Windows `usbipd` registry already contained a persisted APX device. The pilot was attached to `Ubuntu-20.04-Jetson` with auto-attach enabled by the operator.

## Official R35.6.4 files

Download directory:

```text
/home/aa/jetson-r35.6.4/downloads
```

Files and locally calculated SHA-256:

```text
3361faf48a8dea6fe15e9120b994d87e46b90c2aad0ed4dd3f8b7cdd65c7ad49  jetson_linux_r35.6.4_aarch64.tbz2
e268cec67d566dfe73fe5d6585a665dc3bf530ca6b5d6ae54029fd00b5d7bf73  tegra_linux_sample-root-filesystem_r35.6.4_aarch64.tbz2
```

Both bzip2 archives passed a complete `tar -tjf` readability check.

## Prepared environment

The following operations completed:

1. Installed host flash dependencies.
2. Extracted the R35.6.4 BSP and Ubuntu sample rootfs.
3. Ran `apply_binaries.sh`.
4. Ran `tools/l4t_flash_prerequisites.sh`.
5. Verified `jetson-xavier-nx-devkit-qspi.conf`.
6. Created four independent BSP lanes.

Verification:

```text
DISTRO=Ubuntu 20.04.4 LTS
ARCH=x86_64
LANE_1=PASS
LANE_2=PASS
LANE_3=PASS
LANE_4=PASS
WORKSPACE=PASS
```

Lane paths:

```text
/home/aa/jetson-r35.6.4/lanes/lane1
/home/aa/jetson-r35.6.4/lanes/lane2
/home/aa/jetson-r35.6.4/lanes/lane3
/home/aa/jetson-r35.6.4/lanes/lane4
```

Separate lanes are required for parallel operation because NVIDIA flash tools write temporary files inside `Linux_for_Tegra/bootloader`.

## Pilot connection

The operator removed the microSD card, entered Force Recovery, attached APX through `usbipd`, and verified:

```text
USB_INSTANCE=1-1
VID_PID=0955:7e19
SERIAL=unknown
```

The USB instance reported inside WSL must be used. The documentation example `1-2.3` was not valid for this physical connection.

## Command executed

```bash
cd /home/aa/jetson-r35.6.4
sudo ./06_flash_qspi_lane.sh \
  /home/aa/jetson-r35.6.4/lanes/lane1 \
  1-1 \
  gong-rc-pilot \
  --yes-flash-qspi
```

The wrapper verified all of the following before starting:

- exact R35.6.4 rootfs marker
- QSPI-only Xavier NX board configuration
- NVIDIA vendor ID `0955`
- Xavier NX APX product ID `7e19`
- WSL USB instance `1-1`
- explicit destructive-operation confirmation flag

## Live execution status

Log:

```text
/home/aa/jetson-r35.6.4/lanes/lane1/qspi-logs/gong-rc-pilot_1-1_20260716_115815.log
```

During execution, the last observed intermediate state was:

```text
tegradevflash_v2 --instance 1-1 --pt flash.xml.bin --create
Erasing spi: 0 .........
```

The device subsequently completed flashing and the wrapper printed:

```text
QSPI_FLASH=PASS unit=gong-rc-pilot log=/home/aa/jetson-r35.6.4/lanes/lane1/qspi-logs/gong-rc-pilot_1-1_20260716_115815.log
```

## One-at-a-time workflow for subsequent vehicles

1. Finish and validate the current vehicle before connecting another.
2. Power off and label the vehicle.
3. Remove its SD card.
4. Enter Force Recovery and attach APX to `Ubuntu-20.04-Jetson`.
5. Run `./05_list_recovery_devices.sh` and use the USB instance it reports.
6. Reuse lane1 sequentially, changing only the unit ID and current USB instance.
7. Require `QSPI_FLASH=PASS` and archive the log/checksum.
8. Power off, insert that vehicle's cloned SD card, cold boot twice, and run acceptance tests.

For the safer auto-detect path, when exactly one APX device is attached:

```bash
sudo ./08_flash_one_connected.sh gong-rc-01 --yes-flash-qspi
```

The next vehicle must use a new asset ID such as `gong-rc-02`; this keeps log attribution unambiguous.

## Post-flash acceptance

After a successful flash, power off before inserting the R35.6.4 golden SD card. Then boot and record:

```bash
head -n 1 /etc/nv_tegra_release
dpkg-query -W nvidia-l4t-core nvidia-l4t-bootloader nvidia-jetpack
sudo nvbootctrl dump-slots-info
sudo nvbootctrl verify
```

Also validate SSH/Zsh/tmux, Jupyter, POP, camera, SPI/CDS, I2C, audio, buzzer, LiDAR, and motors according to the migration test matrix.

## Final result

**QSPI flash: PASS**

```text
Unit: gong-rc-pilot
USB instance: 1-1
Target: t186ref / Xavier NX Developer Kit QSPI
End time: 2026-07-16 12:02:35 KST
Log: /home/aa/jetson-r35.6.4/lanes/lane1/qspi-logs/gong-rc-pilot_1-1_20260716_115815.log
Log SHA-256: 8612c32da45e5aea66ea4b05cab78a31a4ef47faa22535c268a7b53b4cc0f7eb
```

The final NVIDIA output included:

```text
Coldbooting the device
Bootloader version 01.00.0000
*** The target t186ref has been flashed successfully. ***
```

The line `Reset the board to boot from internal eMMC` is generic NVIDIA `flash.sh` output. This pilot is the Xavier NX Developer Kit SD-card variant; it does not mean that a usable Ubuntu root filesystem was written to an internal eMMC. The completed operation updated QSPI boot firmware only.

Next state:

1. Completely power off the Jetson.
2. Detach or unplug the Force Recovery USB connection and remove the recovery jumper.
3. Insert a verified **full Xavier NX system image** whose root filesystem is JetPack 5.1.6 / L4T R35.6.4 (Ubuntu 20.04).
4. Power on normally and complete the post-flash acceptance checks above.

A generic Ubuntu 20.04 ISO, a file-level copy of Ubuntu, or a JetPack 4-era SD image must not be used. If cloning the migrated pilot SD, restore the entire raw disk image, including its partition table, rather than copying individual files.

Cold boot and hardware acceptance remain pending until the golden SD card is inserted and tested.
