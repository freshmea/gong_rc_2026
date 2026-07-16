#!/usr/bin/env bash
set -euo pipefail

found=0
for directory in /sys/bus/usb/devices/*; do
  [[ -r "$directory/idVendor" && -r "$directory/idProduct" ]] || continue
  vendor="$(cat "$directory/idVendor")"
  product="$(cat "$directory/idProduct")"
  if [[ "$vendor" == "0955" && "$product" == "7e19" ]]; then
    found=1
    instance="$(basename "$directory")"
    serial="unknown"
    [[ -r "$directory/serial" ]] && serial="$(cat "$directory/serial")"
    printf 'USB_INSTANCE=%s VID_PID=%s:%s SERIAL=%s\n' \
      "$instance" "$vendor" "$product" "$serial"
  fi
done

if [[ $found -eq 0 ]]; then
  echo "No Xavier NX APX 0955:7e19 is attached to this WSL distribution." >&2
  exit 1
fi
