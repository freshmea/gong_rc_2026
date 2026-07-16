# Jetson Xavier NX R35.6.4 QSPI workspace for WSL

WSL distribution: `Ubuntu-20.04-Jetson`  
Linux path: `/home/aa/jetson-r35.6.4`  
Windows path: `\\wsl.localhost\Ubuntu-20.04-Jetson\home\aa\jetson-r35.6.4`

## One-time preparation

In Ubuntu-20.04-Jetson:

```bash
cd /home/aa/jetson-r35.6.4
./01_install_host_dependencies.sh
./02_download_r3564.sh
./03_prepare_bsp_and_lanes.sh
./04_verify_workspace.sh
```

The download script resumes partial downloads and records local SHA-256 hashes. The preparation script extracts the exact R35.6.4 BSP and sample rootfs, applies NVIDIA binaries, and creates four isolated flash lanes.

## Attach a Recovery device from Windows

Open Administrator PowerShell:

```powershell
cd \\wsl.localhost\Ubuntu-20.04-Jetson\home\aa\jetson-r35.6.4
.\windows_attach_apx.ps1
```

The script detects a connected `0955:7e19` APX device, shares it, and attaches it specifically to `Ubuntu-20.04-Jetson`. Use `-AutoAttach` only if the device disconnects during flashing; do not leave automatic attachment enabled when using the Jetson RNDIS network after reboot.

Verify in WSL:

```bash
./05_list_recovery_devices.sh
```

## Single-device pilot

Remove the SD card, enter Force Recovery, attach APX to WSL, and note the USB instance printed by script 05. Example:

```bash
sudo ./06_flash_qspi_lane.sh \
  /home/aa/jetson-r35.6.4/lanes/lane1 \
  1-2.3 gong-rc-pilot --yes-flash-qspi
```

Do not continue to batch mode until the pilot boots the golden SD card and passes cold-boot and hardware checks.

## Four-device batch

Copy and edit the inventory template:

```bash
cp batch4.tsv.example batch4.tsv
nano batch4.tsv
```

Each non-comment line is:

```text
unit_id<TAB>usb_instance<TAB>lane_number
```

Run:

```bash
sudo ./07_flash_batch4.sh batch4.tsv --yes-flash-batch
```

Logs are stored independently under every lane's `qspi-logs` directory. Never run two flash processes from the same lane directory.

## Important limitations

- Native Ubuntu 20.04 remains the recommended production host. This WSL workspace is convenient for pilot and recovery work but depends on `usbipd` forwarding.
- Only use Xavier NX Developer Kit recovery USB ID `0955:7e19`.
- `jetson-xavier-nx-devkit-qspi` writes QSPI only. Never substitute `jetson-xavier-nx-devkit` when a valuable SD card is inserted.
- Keep all SD cards removed during QSPI-only flashing.
- A successful host log, cold boot, serial UEFI version, and hardware acceptance test are required before marking a unit complete.
