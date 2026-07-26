#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Run as root" >&2
  exit 1
fi

install -d -m 0755 /etc/modules-load.d
printf 'spidev\n' >/etc/modules-load.d/gong-rc-spidev.conf
chmod 0644 /etc/modules-load.d/gong-rc-spidev.conf

modprobe spidev
udevadm settle

test -c /dev/spidev0.0
ls -l /dev/spidev0.0
echo "SPI_SPIDEV_SETUP=PASS"
