#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="${REMOTE_HOST:-192.168.0.34}"
USER_NAME="${REMOTE_USER:-soda}"
PASSWORD="${REMOTE_PASSWORD:?Set REMOTE_PASSWORD before running}"
HOSTKEY="${REMOTE_HOSTKEY:-SHA256:mHxNTNfeG7wgldciHKI0cq5J9fSkswLQVY25+ceIXTI}"
PLINK="${PLINK:-/mnt/c/Program Files/PuTTY/plink.exe}"
mkdir -p "$ROOT/reports/baseline_tests"

base=("$PLINK" -ssh -batch -hostkey "$HOSTKEY" -pw "$PASSWORD" "$USER_NAME@$HOST")
run_test() {
  local script="$1"
  local report="$2"
  echo "running $script"
  "${base[@]}" "LC_ALL=C /bin/bash -s" < "$ROOT/tests/$script" > "$ROOT/reports/baseline_tests/$report" 2>&1 || true
}

run_test remote_health_check.sh health.txt
run_test test_jupyter_tmux.sh jupyter_tmux.txt
run_test test_audio.sh audio_inventory.txt
run_test test_camera.sh camera_inventory.txt
run_test test_gpio_can.sh gpio_can_inventory.txt

{ printf '%s\n' "$PASSWORD"; cat "$ROOT/tests/test_i2c_inventory.sh"; } |
  "${base[@]}" "IFS= read -r p; printf '%s\\n' \"\$p\" | sudo -S -p '' true; sudo -n LC_ALL=C /bin/bash -s" \
  > "$ROOT/reports/baseline_tests/i2c.txt" 2>&1 || true

"${base[@]}" "LC_ALL=C /bin/bash -s -- /dev/rplidar" \
  < "$ROOT/tests/test_lidar.sh" > "$ROOT/reports/baseline_tests/lidar.txt" 2>&1 || true

echo "baseline tests complete"
