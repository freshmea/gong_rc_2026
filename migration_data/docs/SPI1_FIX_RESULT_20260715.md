# SPI1 fix and reboot verification - 2026-07-15

## Outcome

SPI1 is now routed to the Xavier NX 40-pin header and POP `Cds(7)` works.

## Changes applied

1. Preserved the existing boot configuration and active DTB.
2. Ran NVIDIA Jetson-IO with header function `1=spi1`.
3. Generated `/boot/kernel_tegra194-p3668-0000-p3509-0000-user-custom.dtb`.
4. Added the `JetsonIO` extlinux entry and made it the default.
5. Rebooted the Jetson and waited for SSH to return.

The generated DTB was inspected before reboot. It contains `spi1` functions for
CS0, CS1, SCK, MISO, and MOSI.

## Backup

Backup directory on both the Jetson and migration workspace:

`migration_data/raw/backups/spi_dtb_20260715_125735`

It contains:

- `extlinux.conf.before` and `extlinux.conf.after`
- original `kernel_tegra194-p3668-0000-p3509-0000.dtb.before`
- generated `kernel_tegra194-p3668-0000-p3509-0000-user-custom.dtb`
- before/after checksums
- Jetson-IO output and pre-change enabled-function report

The original base DTB was not overwritten. The new extlinux entry points to the
separate user-custom DTB.

## Post-reboot verification

- Boot time: `2026-07-15 13:00:52 KST`
- Kernel: `5.10.216-tegra`
- `DEFAULT JetsonIO`: PASS
- Jetson-IO enabled function: `spi1 (19,21,23,24,26)`: PASS
- SPI1 SCK/MISO/MOSI/CS0/CS1 pinctrl: `function spi1`, HOG: PASS
- `/dev/spidev0.0`: present as `root:gpio 0660`
- `spidev` module automatic boot load: PASS

### MCP3208 raw values

Representative post-reboot ranges:

- channel 0: 5-6
- channel 1: 4-6
- channel 2: 14-1037
- channel 3: 0-33
- channel 4: 3651-3662
- channel 5: 4-6
- channel 6: 5-6
- channel 7 (Cds): 1565-1759

The exact light-sensor value changes with ambient light; the important result
is that the migrated system no longer returns zero for every transaction.

### POP API

- `Cds(7)` construction: PASS
- 32 raw reads: min 1581, max 1774, mean 1690.8
- `Cds.readAverage()` pseudo lux: 726
- Final marker: `CDS_POP_TEST=PASS`

### Regression checks

- `jupyter-gong-rc`: active
- `nvargus-daemon`: active
- `nvfancontrol`: active
- I2C bus 1 still detects `0x5c`, `0x5e`, and mux `0x70`
- I2C bus 8 still detects `0x0a`, `0x57`, `0x68`, and mux `0x70`

## Evidence and tests

- Before report: `migration_data/raw/reports/spi_192.168.0.34.txt`
- Known-good report: `migration_data/raw/reports/spi_192.168.0.46.txt`
- After report: `migration_data/raw/reports/spi_192.168.0.34_after_spi1.txt`
- Raw ADC test: `migration_data/tests/test_cds_spi.py`
- POP API test: `migration_data/tests/test_cds_pop.py`
- Reproducible Jetson-IO setup: `migration_data/scripts/enable_spi1_jetson_io.sh`

## Rollback

The old boot selection can be restored without deleting the generated DTB:

```bash
BACKUP=/home/soda/gong_rc_2026/migration_data/raw/backups/spi_dtb_20260715_125735
sudo cp -a "$BACKUP/extlinux.conf.before" /boot/extlinux/extlinux.conf
sudo sync
sudo reboot
```
