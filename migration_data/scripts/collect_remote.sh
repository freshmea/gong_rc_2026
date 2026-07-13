#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="${REMOTE_HOST:-192.168.0.34}"
USER_NAME="${REMOTE_USER:-soda}"
PASSWORD="${REMOTE_PASSWORD:?Set REMOTE_PASSWORD before running}"
HOSTKEY="${REMOTE_HOSTKEY:-SHA256:mHxNTNfeG7wgldciHKI0cq5J9fSkswLQVY25+ceIXTI}"
PLINK="${PLINK:-/mnt/c/Program Files/PuTTY/plink.exe}"
REDACTOR="$ROOT/scripts/redact_sensitive.py"

mkdir -p "$ROOT/raw/reports" "$ROOT/raw/configs/home" "$ROOT/artifacts" "$ROOT/reports" "$ROOT/docs"

plink_base=("$PLINK" -ssh -batch -hostkey "$HOSTKEY" -pw "$PASSWORD" "$USER_NAME@$HOST")

echo "[1/7] collecting system inventory"
"${plink_base[@]}" "LC_ALL=C /bin/bash -s" < "$ROOT/scripts/remote_inventory.sh" \
  | python3 "$REDACTOR" > "$ROOT/raw/reports/system_inventory.txt"

echo "[2/7] collecting privileged read-only hardware inventory"
privileged_command='dmesg | grep -Ei "gpio|i2c|spi|tty|usb|can|mttcan|lidar|video|camera|audio|snd" | sed -n "1,500p"; for b in 0 1 8; do if [ -e /dev/i2c-$b ]; then echo "===== I2C BUS $b ====="; i2cdetect -y -r $b; fi; done'
printf '%s\n' "$PASSWORD" | "${plink_base[@]}" "sudo -S -p '' /bin/bash -c '$privileged_command'" \
  | python3 "$REDACTOR" > "$ROOT/raw/reports/privileged_hardware_inventory.txt"

echo "[3/7] collecting redacted shell and application configuration"
remote_files=(
  .bashrc .zshrc .profile .bash_logout .tmux.conf .python_history .zsh_history
  .jupyter/jupyter_notebook_config.py .jupyter/custom/custom.css
  .ipython/profile_default/ipython_config.py .ipython/profile_default/ipython_kernel_config.py
)
for relative in "${remote_files[@]}"; do
  safe_name="${relative//\//__}"
  safe_name="${safe_name#.}"
  if "${plink_base[@]}" "test -f '/home/soda/$relative'"; then
    "${plink_base[@]}" "cat -- '/home/soda/$relative'" \
      | python3 "$REDACTOR" > "$ROOT/raw/configs/home/$safe_name"
  fi
done

echo "[4/7] copying class notebooks and known-working code"
"${plink_base[@]}" "tar -C /home/soda -czf - --exclude='*/.ipynb_checkpoints' Project/python/notebook camera_api.py" \
  > "$ROOT/artifacts/class_notebooks_and_code.tar.gz"
mkdir -p "$ROOT/artifacts/class_notebooks_and_code"
tar -xzf "$ROOT/artifacts/class_notebooks_and_code.tar.gz" -C "$ROOT/artifacts/class_notebooks_and_code"

echo "[5/7] copying ROS/LiDAR and vendor board sources"
"${plink_base[@]}" "tar -C /home/soda -czf - catkin_ws/src" > "$ROOT/artifacts/ros_lidar_sources.tar.gz"
mkdir -p "$ROOT/artifacts/ros_lidar_sources"
tar -xzf "$ROOT/artifacts/ros_lidar_sources.tar.gz" -C "$ROOT/artifacts/ros_lidar_sources"
"${plink_base[@]}" "tar -C /home/soda -czf - --exclude='.config/hanback/images' .config/hanback" \
  > "$ROOT/artifacts/hanback_board_config.tar.gz"
mkdir -p "$ROOT/artifacts/hanback_board_config"
tar -xzf "$ROOT/artifacts/hanback_board_config.tar.gz" -C "$ROOT/artifacts/hanback_board_config"

echo "[6/7] copying critical vendor Python source for compatibility analysis"
"${plink_base[@]}" "tar -C / -czf - usr/local/lib/python3.6/dist-packages/pop usr/local/lib/python3.6/dist-packages/rplidar.py usr/local/lib/python3.6/dist-packages/pyaudio.py 2>/dev/null" \
  > "$ROOT/artifacts/vendor_python_sources.tar.gz"
mkdir -p "$ROOT/artifacts/vendor_python_sources"
tar -xzf "$ROOT/artifacts/vendor_python_sources.tar.gz" -C "$ROOT/artifacts/vendor_python_sources"

date --iso-8601=seconds > "$ROOT/reports/collected_at.txt"
printf 'host=%s\nuser=%s\nhostkey=%s\n' "$HOST" "$USER_NAME" "$HOSTKEY" > "$ROOT/reports/source.txt"

echo "[7/7] generating checksums"
(
  cd "$ROOT"
  find README.md raw artifacts tests scripts docs reports -type f ! -name SHA256SUMS \
    ! -path 'reports/checksum_verification.txt' -print0 2>/dev/null \
    | sort -z | xargs -0 sha256sum
) > "$ROOT/SHA256SUMS"

echo "collection complete: $ROOT"

