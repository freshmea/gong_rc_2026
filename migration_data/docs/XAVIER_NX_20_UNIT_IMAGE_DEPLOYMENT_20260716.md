# Xavier NX 20-unit image backup and deployment guide

Date: 2026-07-16

## Confirmed reference platform

```text
Model: NVIDIA Jetson Xavier NX Developer Kit
JetPack: 5.1.6-b5
L4T: R35.6.4
Root device: /dev/mmcblk0p1
Boot storage: 58.3 GiB SD card, GPT, 22 partitions
Root filesystem: ext4, 57.6 GiB, about 25 GiB available at inspection time
Bootloader slots: A and B normal
```

This guide is for the same Xavier NX Developer Kit and carrier board revision. Do not write this image to Orin, Xavier NX eMMC production modules, custom carrier boards, or different storage layouts.

## Recommended deployment model

For these SD-card developer kits, use:

1. Freeze and validate vehicle 34 as the golden reference.
2. Back up the entire powered-off SD card as a compressed raw image.
3. Bring every target's QSPI/boot firmware to L4T R35.6.4.
4. Write the golden SD image to an equal-size or larger SD card.
5. Generate a unique hostname, machine ID, and SSH host keys on first boot.
6. Run the migration health tests before accepting the vehicle.

A raw SD image contains the root filesystem and all 22 SD partitions, but it does **not** contain the QSPI soldered to the Jetson module. QSPI and the SD image must therefore be kept on the same L4T release.

## A. Freeze the golden vehicle

On vehicle 34:

```bash
sudo systemctl stop jupyter-gong-rc.service
tmux list-sessions
sudo systemctl is-active nvargus-daemon.service
dpkg-query -W nvidia-l4t-core nvidia-jetpack gong-rc-pop
/home/soda/venvs/gong-rc/bin/python -c \
  'import pop, torch, torchvision; print(pop.__version__, torch.__version__, torchvision.__version__)'
```

Close notebooks, stop camera/motor programs, and confirm no training or package installation is running. Keep the Wi-Fi profile and Jupyter password if all classroom vehicles intentionally share them. Remove private tokens, browser credentials, and unrelated SSH private keys before imaging.

Shut down cleanly:

```bash
sudo poweroff
```

Wait until activity LEDs and the fan stop, disconnect power, and remove the SD card. Offline capture avoids an inconsistent filesystem image.

## B. Capture the SD image on an Ubuntu host

Install the tools:

```bash
sudo apt update
sudo apt install zstd util-linux coreutils
```

Insert the golden SD card through a reader and identify it carefully:

```bash
lsblk -p -o NAME,SIZE,MODEL,SERIAL,TYPE,FSTYPE,MOUNTPOINT
```

Do not guess the device name. In the example below `/dev/sdX` means the whole SD card, not `/dev/sdX1` and not the host OS disk.

Use the supplied protected backup script:

```bash
sudo ./backup_xavier_nx_sd.sh /dev/sdX \
  xavier-nx-gong-rc-jp516-20260716.img.zst --yes-read-whole-disk
```

The script refuses the host root disk, mounted media, non-block devices, and existing output files. It creates:

```text
xavier-nx-gong-rc-jp516-20260716.img.zst
xavier-nx-gong-rc-jp516-20260716.img.zst.size
xavier-nx-gong-rc-jp516-20260716.img.zst.sha256
```

Verify before removing the master SD card:

```bash
zstd --test xavier-nx-gong-rc-jp516-20260716.img.zst
sha256sum -c xavier-nx-gong-rc-jp516-20260716.img.zst.sha256
```

Keep two copies of the image on different physical disks. Never use the only golden SD card as a production target.

### Card-size requirement

The reference disk contains 122,204,160 sectors (62,568,529,920 bytes). Every target card must expose at least this many bytes. Nominally identical 64GB cards can differ slightly; using the same manufacturer and model is strongly recommended.

## C. Match QSPI to JetPack 5.1.6 / L4T R35.6.4

Use a native x86_64 Ubuntu host with the Jetson Linux R35.6.4 BSP. WSL/USB forwarding is not recommended for a 20-unit production process.

Prepare the matching BSP and sample rootfs as described by NVIDIA, then:

```bash
cd Linux_for_Tegra
sudo ./tools/l4t_flash_prerequisites.sh
```

For each Xavier NX Developer Kit, remove the SD card, connect the recovery USB cable, enter Force Recovery mode, and verify NVIDIA recovery USB with `lsusb -d 0955:7e19`. Flash QSPI only:

```bash
sudo ./flash.sh jetson-xavier-nx-devkit-qspi internal
```

This establishes the R35.6.4 boot firmware without touching microSD storage. For the 20-unit parallel-lane procedure, USB-instance safety checks, and acceptance rules, follow `QSPI_L4T_35.6.4_20_UNIT_PLAN_20260716.md`. Do not use an R36/JetPack 6 BSP with this Xavier NX image.

## D. Restore the golden image to each SD card

Identify the target card again with `lsblk`, then run:

```bash
sudo ./restore_xavier_nx_sd.sh \
  xavier-nx-gong-rc-jp516-20260716.img.zst \
  /dev/sdX --yes-really-erase
```

This is destructive. The script checks that the target is not the host root disk, is not mounted, and is at least as large as the source image.

After completion:

```bash
sync
sudo eject /dev/sdX
```

Insert the card into its target vehicle and boot.

## E. Create a unique identity on first boot

All raw clones initially have the same hostname, machine ID, and SSH server keys. This must be corrected before several clones share a LAN.

Temporarily connect only one new clone at a time. Run, for example:

```bash
sudo ./personalize_cloned_vehicle.sh gong-rc-01
sudo reboot
```

Use `gong-rc-01` through `gong-rc-20`, or your asset identifiers. The script preserves the `soda` user, course files, Jupyter password, Wi-Fi profile, and POP installation. It changes only machine identity and SSH host keys.

After reboot, remove the old SSH host-key entry on the administration PC when the reused IP causes a warning:

```bash
ssh-keygen -R <vehicle-ip>
```

Prefer DHCP reservations keyed to each Jetson's unique Ethernet/Wi-Fi MAC address. Do not clone one fixed IPv4 address onto 20 simultaneously connected vehicles.

## F. Acceptance test per vehicle

Record the serial number, MAC addresses, assigned IP, hostname, and SD card serial in an inventory table. Then run:

```bash
hostnamectl
ip -br link
ip -br address
systemctl is-active jupyter-gong-rc.service nvargus-daemon.service
dpkg-query -W gong-rc-pop nvidia-l4t-core nvidia-jetpack
python3 /home/soda/gong_rc_2026/migration_data/tests/test_pop_import.py
```

From the migration folder, also run the applicable hardware tests for SPI/CDS, I2C, audio recording/playback, camera, buzzer, motors, LiDAR, and the A31 camera/AI integration test. Motor tests require the vehicle to be raised so wheels cannot contact the floor.

Acceptance criteria:

- SSH opens Zsh and automatically attaches `tmux main`.
- `VIRTUAL_ENV=/home/soda/venvs/gong-rc` and `ROS_DISTRO=foxy` are present.
- Jupyter is reachable at `<vehicle-ip>:8888` with the agreed password.
- POP reports `0.4.1` and torchvision image extension imports without warning.
- Camera, CDS/SPI, I2C, buzzer, ALSA input/output, LiDAR, and motor drivers pass.
- Hostname, machine ID, SSH host fingerprint, MAC addresses, and IP are unique.

## G. NVIDIA full backup/restore alternative

When QSPI and all storage partitions must be captured and restored together, use the matching R35.6.4 BSP's supported backup/restore tool while the Jetson is in Force Recovery mode:

```bash
cd Linux_for_Tegra
sudo ./tools/backup_restore/l4t_backup_restore.sh -b jetson-xavier-nx-devkit
sudo ./tools/backup_restore/l4t_backup_restore.sh -r jetson-xavier-nx-devkit
```

Before production use, read the exact `tools/backup_restore/README_backup_restore.txt` shipped inside the R35.6.4 BSP. It is the authority for the available options and Workflow 3 mass-flash procedure. Validate backup and restore on one spare vehicle before connecting multiple recovery devices.

NVIDIA distinguishes an APP clone from a full backup: `flash.sh -G` clones only the root filesystem partition, whereas the backup/restore tool covers all partitions and QSPI. For this SD developer-kit fleet, the offline whole-SD method is easier to audit, while the NVIDIA full backup is preferred when boot firmware must be included in one supported workflow.

## Rollback

Keep the original SD card from every vehicle until its clone passes acceptance. Rollback is:

1. Power off.
2. Reinstall the labeled original SD card.
3. If QSPI was changed and the old image is JetPack 4, reflash the matching old QSPI/BSP before expecting that old SD image to boot.

An old SD card is not by itself a complete QSPI rollback.
