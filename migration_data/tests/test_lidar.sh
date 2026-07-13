#!/usr/bin/env bash
set -u
device="${1:-/dev/rplidar}"

echo "LiDAR device: $device"
if [ ! -e "$device" ]; then
  echo 'SKIP: LiDAR device node is not present'
  exit 0
fi
ls -l "$device"
udevadm info --query=all --name="$device" 2>/dev/null || true

python3 - "$device" <<'PY'
import sys
from rplidar import RPLidar

device = sys.argv[1]
lidar = RPLidar(device, timeout=2)
try:
    print('INFO', lidar.get_info())
    print('HEALTH', lidar.get_health())
    print('PASS: RPLidar serial protocol responded')
finally:
    try:
        lidar.stop()
    except Exception:
        pass
    try:
        lidar.stop_motor()
    except Exception:
        pass
    lidar.disconnect()
PY

