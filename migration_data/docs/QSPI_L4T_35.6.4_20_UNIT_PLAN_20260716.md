# Xavier NX 20-unit QSPI alignment plan for L4T 35.6.4

Date: 2026-07-16

## Recommendation

Use one native Ubuntu 20.04 x86_64 host and four isolated BSP working directories. Flash QSPI only on four Xavier NX Developer Kits in parallel, then repeat for five batches.

Do not use WSL for the production batch. Recovery USB disconnection, `usbipd` reattachment, and RNDIS transitions make it harder to distinguish a real flash failure from a host forwarding problem.

## Why QSPI-only parallel lanes

The R35.6.4 BSP contains these different board configurations:

- `jetson-xavier-nx-devkit`: QSPI plus microSD
- `jetson-xavier-nx-devkit-qspi`: QSPI only
- `jetson-xavier-nx-devkit-emmc`: QSPI plus eMMC production module

The fleet currently uses the Xavier NX Developer Kit SD-card configuration. Using the QSPI-only configuration with the SD card physically removed prevents accidental destruction of the golden SD image.

Four independent `flash.sh` lanes are preferred for the first fleet rollout because each process reads its attached module's EEPROM. An initrd massflash package is faster at large scale but embeds board identity inputs such as BOARDID, BOARDSKU, FAB, and BOARDREV. Use it only after confirming that all 20 modules and carrier boards are identical and after a two-board pilot.

## Host preparation

Requirements:

- Native Ubuntu 20.04 x86_64
- At least 50 GB free disk space
- Four reliable USB ports or a powered industrial USB hub
- Four known-good data-capable micro-USB cables
- Stable power for every Jetson; do not power the Jetsons from the USB hub
- NVIDIA Jetson Linux R35.6.4 Driver Package and matching sample root filesystem

Prepare one canonical BSP:

```bash
mkdir -p ~/nvidia/r35.6.4
cd ~/nvidia/r35.6.4

tar xf Jetson_Linux_R35.6.4_aarch64.tbz2
sudo tar xpf Tegra_Linux_Sample-Root-Filesystem_R35.6.4_aarch64.tbz2 \
  -C Linux_for_Tegra/rootfs

cd Linux_for_Tegra
sudo ./apply_binaries.sh
sudo ./tools/l4t_flash_prerequisites.sh
```

Confirm that these files exist before proceeding:

```bash
test -x flash.sh
test -f jetson-xavier-nx-devkit-qspi.conf
grep -F 'REVISION: 6.4' rootfs/etc/nv_tegra_release
```

Freeze this directory after preparation. Do not let SDK Manager replace it with another release.

## Pilot on one spare vehicle

1. Label the module and its original SD card.
2. Power off and remove the SD card.
3. Connect recovery micro-USB and independent power.
4. Enter Force Recovery mode: hold FC REC to GND, power/reset the board, then release the jumper.
5. Confirm recovery USB:

```bash
lsusb -d 0955:7e19
```

6. Flash only QSPI:

```bash
cd ~/nvidia/r35.6.4/Linux_for_Tegra
sudo ./flash.sh jetson-xavier-nx-devkit-qspi internal 2>&1 | \
  tee qspi-pilot.log
```

7. Require command exit code 0 and a successful completion line in the log.
8. Power off, insert a copy of the golden L4T 35.6.4 SD card, and boot.
9. Verify camera, SPI/I2C, audio, Jupyter, POP, and one cold reboot before approving the batch process.

The QSPI-only command must not be replaced by `jetson-xavier-nx-devkit`, because that configuration also flashes the microSD card.

## Four parallel lanes

Create separate working directories. Multiple `flash.sh` processes must not share one `Linux_for_Tegra/bootloader` directory because they create temporary images and logs there.

```bash
cd ~/nvidia/r35.6.4
for lane in 1 2 3 4; do
  cp -a Linux_for_Tegra "Linux_for_Tegra_lane${lane}"
done
```

Put four labeled vehicles in recovery mode and identify their physical USB paths:

```bash
grep -H 7e19 /sys/bus/usb/devices/*/idProduct
```

Example output:

```text
/sys/bus/usb/devices/1-2.1/idProduct:7e19
/sys/bus/usb/devices/1-2.2/idProduct:7e19
/sys/bus/usb/devices/1-2.3/idProduct:7e19
/sys/bus/usb/devices/1-2.4/idProduct:7e19
```

Run one command in each tmux pane using its own BSP directory and USB instance:

```bash
sudo ./flash_qspi_xavier_nx_lane.sh \
  ~/nvidia/r35.6.4/Linux_for_Tegra_lane1 1-2.1 gong-rc-01 \
  --yes-flash-qspi
```

Repeat with lanes 2 through 4. The wrapper refuses a non-R35.6.4 rootfs, an invalid USB path, a device whose USB vendor/product is not NVIDIA Xavier NX recovery mode, or a missing QSPI-only configuration.

After all four report `QSPI_FLASH=PASS`, power them off, insert their cloned/personalized SD cards, boot, and run acceptance checks. Do not start the next batch until the four current logs are archived.

## Acceptance check

On each booted vehicle:

```bash
head -n 1 /etc/nv_tegra_release
dpkg-query -W nvidia-l4t-core nvidia-l4t-bootloader nvidia-jetpack
sudo nvbootctrl dump-slots-info
sudo nvbootctrl verify
```

Required:

- rootfs and bootloader packages are `35.6.4`
- both bootloader slots report `normal`
- the device cold-boots twice without falling back to another slot
- the serial boot log identifies the expected Jetson UEFI build from the R35.6.4 flash
- the per-unit host flash log ends successfully

`nvbootctrl` can report `Current version: 0.0.1` on some freshly flashed JetPack 5 systems even when the UEFI build is current. Vehicle 34 currently shows this value while its installed bootloader and core packages are 35.6.4 and both slots are normal. Therefore, do not use that single field as the only acceptance criterion; retain the host flash log and capture the serial UEFI version during the pilot.

## Time and throughput

Use four lanes first. A batch consists of recovery wiring, approximately a few minutes of QSPI flashing, power-down, SD insertion, and boot validation. Five batches process 20 vehicles while keeping cable and asset tracking manageable. More than four simultaneous devices usually saves less time than it costs in cable mix-ups and log attribution unless a fixed production jig is available.

## When to use initrd massflash

NVIDIA's supported factory method is `l4t_initrd_flash.sh --massflash N`. Consider it only after inventory confirms one BOARDID/BOARDSKU/FAB/BOARDREV across the fleet. Generate the offline package from the exact R35.6.4 BSP and follow the bundled `tools/kernel_flash/README_initrd_flash.txt`; do not reuse a package generated by R35.5 or R36.

For a 20-unit classroom fleet, use batches of four or five rather than attempting 20 recovery USB connections at once. Test the massflash package on two spare units and compare their serial boot logs before using it on the remaining fleet.

## Rollback

QSPI is not restored by replacing the SD card. If a target must return to JetPack 4, flash that exact older BSP's QSPI-only configuration before inserting the old SD card. Keep these together in the archive:

- R35.6.4 BSP package checksums
- every per-unit QSPI flash log
- the golden SD image and checksum
- old BSP/QSPI recovery package
- vehicle serial number, USB path, hostname, MAC addresses, and operator result
