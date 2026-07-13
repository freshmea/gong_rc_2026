#!/usr/bin/env bash
# Read-only GPIO and CAN inventory. Does not export pins or change CAN state.
set -u

echo '=== GPIO chips ==='
find /dev -maxdepth 1 -name 'gpiochip*' -printf '%M %u:%g %p\n' 2>/dev/null | sort || true
if command -v gpioinfo >/dev/null 2>&1; then
  gpioinfo 2>/dev/null | sed -n '1,160p' || true
fi

echo '=== CAN links ==='
ip -details link show type can 2>/dev/null || true
find /sys/class/net -maxdepth 1 -name 'can*' -printf '%f -> %l\n' 2>/dev/null || true

echo '=== Board support ==='
test -f /home/soda/.config/hanback/board_config.py &&
  echo 'PASS: Hanback board_config.py present' ||
  echo 'WARN: Hanback board_config.py missing'
test -f /home/soda/.config/hanback/can_enable.sh &&
  echo 'PASS: Hanback can_enable.sh present' ||
  echo 'WARN: Hanback can_enable.sh missing'

python3 - <<'PY'
import importlib
for name in ('Jetson.GPIO', 'RPi.GPIO'):
    module = importlib.import_module(name)
    print('PASS: import', name, getattr(module, '__version__', 'unknown'))
PY
