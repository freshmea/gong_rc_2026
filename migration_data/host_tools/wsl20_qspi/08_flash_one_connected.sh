#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: sudo $0 UNIT_ID --yes-flash-qspi" >&2
  exit 2
}

[[ $# -eq 2 && "$2" == "--yes-flash-qspi" ]] || usage
[[ $EUID -eq 0 ]] || { echo "Run with sudo." >&2; exit 1; }
UNIT_ID="$1"
[[ "$UNIT_ID" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "Invalid unit ID." >&2; exit 1; }

ROOT="${JETSON_WORK_ROOT:-/home/aa/jetson-r35.6.4}"
FLASHER="$ROOT/06_flash_qspi_lane.sh"
LANE="$ROOT/lanes/lane1"
[[ -x "$FLASHER" ]] || { echo "Missing flasher: $FLASHER" >&2; exit 1; }

declare -a devices
for directory in /sys/bus/usb/devices/*; do
  [[ -r "$directory/idVendor" && -r "$directory/idProduct" ]] || continue
  if [[ "$(cat "$directory/idVendor")" == "0955" \
        && "$(cat "$directory/idProduct")" == "7e19" ]]; then
    devices+=("$(basename "$directory")")
  fi
done

if [[ ${#devices[@]} -ne 1 ]]; then
  echo "Expected exactly one attached Xavier NX APX device; found ${#devices[@]}." >&2
  "$ROOT/05_list_recovery_devices.sh" >&2 || true
  exit 1
fi

USB_INSTANCE="${devices[0]}"
echo "ONE_UNIT unit=$UNIT_ID usb=$USB_INSTANCE lane=lane1"
exec "$FLASHER" "$LANE" "$USB_INSTANCE" "$UNIT_ID" --yes-flash-qspi
