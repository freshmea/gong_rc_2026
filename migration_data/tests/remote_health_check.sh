#!/usr/bin/env bash
# Non-destructive baseline test for the old image and post-migration comparison.
set -u

pass=0
warn=0
fail=0

ok() { printf 'PASS  %s\n' "$1"; pass=$((pass + 1)); }
warning() { printf 'WARN  %s\n' "$1"; warn=$((warn + 1)); }
bad() { printf 'FAIL  %s\n' "$1"; fail=$((fail + 1)); }
check_command() { command -v "$1" >/dev/null 2>&1 && ok "command: $1" || warning "missing command: $1"; }

printf 'Jetson migration health check: %s\n' "$(date --iso-8601=seconds 2>/dev/null || date)"

[ -r /etc/os-release ] && ok '/etc/os-release readable' || bad '/etc/os-release missing'
[ -r /etc/nv_tegra_release ] && ok 'Jetson L4T release present' || bad 'Jetson L4T release missing'
[ "$(uname -m)" = aarch64 ] && ok 'architecture aarch64' || bad "unexpected architecture: $(uname -m)"

for cmd in bash zsh python3 pip3 jupyter tmux tar curl wget i2cdetect aplay arecord; do check_command "$cmd"; done

[ -e /dev/i2c-0 ] && ok '/dev/i2c-0 present' || warning '/dev/i2c-0 absent'
[ -e /dev/i2c-1 ] && ok '/dev/i2c-1 present' || warning '/dev/i2c-1 absent'
[ -e /dev/i2c-8 ] && ok '/dev/i2c-8 present' || warning '/dev/i2c-8 absent'

if aplay -l >/dev/null 2>&1; then ok 'ALSA playback device enumerated'; else warning 'no ALSA playback device'; fi
if arecord -l >/dev/null 2>&1; then ok 'ALSA capture device enumerated'; else warning 'no ALSA capture device'; fi

if find /dev -maxdepth 1 \( -name 'video*' -o -name 'ttyUSB*' -o -name 'rplidar' \) | grep -q .; then
  ok 'camera or serial/LiDAR device node present'
else
  warning 'no camera or serial/LiDAR device node present'
fi

[ -f /etc/udev/rules.d/rplidar.rules ] && ok 'RPLidar udev rule present' || warning 'RPLidar udev rule absent'
[ -d /home/soda/catkin_ws/src/RPLidar_Hector_SLAM ] && ok 'RPLidar/Hector source present' || warning 'RPLidar/Hector source absent'
[ -d /home/soda/Project/python/notebook/gong_rc_2026 ] && ok '2026 class notebooks present' || bad '2026 class notebooks absent'

if python3 - <<'PY'
import importlib
import sys
required = ['numpy', 'cv2', 'pyaudio', 'rplidar', 'RPi.GPIO', 'pop']
failures = 0
for name in required:
    try:
        module = importlib.import_module(name)
        print('PYTHON_IMPORT_PASS %s %s' % (name, getattr(module, '__version__', 'unknown')))
    except BaseException as exc:
        failures += 1
        print('PYTHON_IMPORT_FAIL %s %s: %s' % (name, type(exc).__name__, exc))
sys.exit(1 if failures else 0)
PY
then
  ok 'required Python hardware modules import'
else
  bad 'one or more required Python hardware modules failed to import'
fi

printf '\nSUMMARY pass=%d warn=%d fail=%d\n' "$pass" "$warn" "$fail"
[ "$fail" -eq 0 ]

