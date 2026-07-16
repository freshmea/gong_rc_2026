#!/usr/bin/env bash
set -Eeuo pipefail

TARGET_USER="${TARGET_USER:-soda}"
TARGET_HOME="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
MIGRATION_ROOT="$TARGET_HOME/gong_rc_2026/migration_data"
STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="$MIGRATION_ROOT/raw/backups/buzzer_pwm8_dtb_$STAMP"
ACTIVE_DTB="/boot/dtb/kernel_tegra194-p3668-0000-p3509-0000.dtb"

if [[ $EUID -ne 0 ]]; then
  echo "Run as root" >&2
  exit 1
fi

install -d -o "$TARGET_USER" -g "$TARGET_USER" "$BACKUP_DIR"
cp -a /boot/extlinux/extlinux.conf "$BACKUP_DIR/extlinux.conf.before"
cp -a "$ACTIVE_DTB" "$BACKUP_DIR/$(basename "$ACTIVE_DTB").before"
find /boot -maxdepth 2 -type f -name '*user-custom*.dtb' \
  -exec cp -a {} "$BACKUP_DIR/" \;

sha256sum /boot/extlinux/extlinux.conf "$ACTIVE_DTB" \
  >"$BACKUP_DIR/sha256.before.txt"
python3 /opt/nvidia/jetson-io/config-by-function.py -l enabled \
  >"$BACKUP_DIR/jetson_io_enabled.before.txt" 2>&1 || true

# Keep the previously validated SPI1 routing and add PWM8 on physical pin 32.
python3 /opt/nvidia/jetson-io/config-by-function.py -o dtb '1=spi1 pwm8' \
  2>&1 | tee "$BACKUP_DIR/jetson_io_apply.log"

cp -a /boot/extlinux/extlinux.conf "$BACKUP_DIR/extlinux.conf.after"
find /boot -maxdepth 2 -type f -name '*user-custom*.dtb' \
  -exec cp -a {} "$BACKUP_DIR/" \;
sha256sum /boot/extlinux/extlinux.conf "$ACTIVE_DTB" \
  >"$BACKUP_DIR/sha256.after.txt"

chown -R "$TARGET_USER:$TARGET_USER" "$BACKUP_DIR"
sync

echo "BUZZER_PWM8_DTB_PREPARE=PASS"
echo "BACKUP_DIR=$BACKUP_DIR"
echo "--- extlinux diff ---"
diff -u "$BACKUP_DIR/extlinux.conf.before" "$BACKUP_DIR/extlinux.conf.after" || true
echo "--- generated DTBs ---"
find /boot -maxdepth 2 -type f -name '*user-custom*.dtb' \
  -printf '%TY-%Tm-%Td %TH:%TM:%TS %s %p\n' | sort
