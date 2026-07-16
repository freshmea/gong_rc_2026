#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: sudo $0 BSP_DIR USB_INSTANCE UNIT_ID --yes-flash-qspi" >&2
  echo "Example USB_INSTANCE: 1-2.3" >&2
  exit 2
}

[[ $# -eq 4 ]] || usage
BSP_DIR="$(readlink -f "$1")"
USB_INSTANCE="$2"
UNIT_ID="$3"
[[ "$4" == "--yes-flash-qspi" ]] || usage
[[ $EUID -eq 0 ]] || { echo "Run with sudo." >&2; exit 1; }
[[ "$USB_INSTANCE" =~ ^[0-9]+-[0-9]+([.][0-9]+)*$ ]] || { echo "Invalid USB instance." >&2; exit 1; }
[[ "$UNIT_ID" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "Invalid unit ID." >&2; exit 1; }
[[ -x "$BSP_DIR/flash.sh" ]] || { echo "Missing flash.sh in $BSP_DIR" >&2; exit 1; }
[[ -f "$BSP_DIR/jetson-xavier-nx-devkit-qspi.conf" ]] || { echo "Missing QSPI-only board config." >&2; exit 1; }

RELEASE_FILE="$BSP_DIR/rootfs/etc/nv_tegra_release"
[[ -r "$RELEASE_FILE" ]] || { echo "Missing BSP release marker: $RELEASE_FILE" >&2; exit 1; }
grep -q '# R35 (release), REVISION: 6.4' "$RELEASE_FILE" || {
  echo "Refusing a BSP that is not L4T R35.6.4." >&2
  exit 1
}

USB_SYSFS="/sys/bus/usb/devices/$USB_INSTANCE"
[[ -r "$USB_SYSFS/idVendor" && -r "$USB_SYSFS/idProduct" ]] || {
  echo "USB recovery device not found at $USB_INSTANCE." >&2
  exit 1
}
VENDOR="$(cat "$USB_SYSFS/idVendor")"
PRODUCT="$(cat "$USB_SYSFS/idProduct")"
[[ "$VENDOR" == "0955" && "$PRODUCT" == "7e19" ]] || {
  echo "Expected NVIDIA Xavier NX recovery 0955:7e19, found $VENDOR:$PRODUCT." >&2
  exit 1
}

LOG_DIR="$BSP_DIR/qspi-logs"
mkdir -p "$LOG_DIR"
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$LOG_DIR/${UNIT_ID}_${USB_INSTANCE//./-}_$STAMP.log"

echo "UNIT_ID=$UNIT_ID"
echo "USB_INSTANCE=$USB_INSTANCE"
echo "BSP=$BSP_DIR"
echo "LOG=$LOG_FILE"
echo "WARNING: QSPI on $UNIT_ID will now be overwritten."

cd "$BSP_DIR"
set +e
./flash.sh --usb-instance "$USB_INSTANCE" \
  jetson-xavier-nx-devkit-qspi internal 2>&1 | tee "$LOG_FILE"
STATUS=${PIPESTATUS[0]}
set -e

if [[ $STATUS -ne 0 ]]; then
  echo "QSPI_FLASH=FAIL exit=$STATUS log=$LOG_FILE" >&2
  exit "$STATUS"
fi

sha256sum "$LOG_FILE" > "$LOG_FILE.sha256"
echo "QSPI_FLASH=PASS unit=$UNIT_ID log=$LOG_FILE"
