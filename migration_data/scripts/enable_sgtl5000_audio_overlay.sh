#!/usr/bin/env bash
set -Eeuo pipefail

TARGET_USER="${TARGET_USER:-soda}"
TARGET_HOME="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="$TARGET_HOME/gong_rc_2026/migration_data/raw/backups/audio_sgtl5000_$STAMP"
BASE_DTB="/boot/kernel_tegra194-p3668-0000-p3509-0000-user-custom.dtb"
OVERLAY="/boot/tegra194-p3668-all-p3509-0000-fe-pi-audio.dtbo"
OUTPUT="/boot/kernel_tegra194-p3668-0000-p3509-0000-user-custom-sgtl5000.dtb"
EXTLINUX="/boot/extlinux/extlinux.conf"

if [[ $EUID -ne 0 ]]; then
  echo "Run as root" >&2
  exit 1
fi
for file in "$BASE_DTB" "$OVERLAY" "$EXTLINUX"; do
  [[ -f "$file" ]] || { echo "Missing required file: $file" >&2; exit 1; }
done
command -v fdtoverlay >/dev/null

install -d -o "$TARGET_USER" -g "$TARGET_USER" "$BACKUP_DIR"
cp -a "$EXTLINUX" "$BACKUP_DIR/extlinux.conf.before"
cp -a "$BASE_DTB" "$OVERLAY" "$BACKUP_DIR/"
[[ ! -f "$OUTPUT" ]] || cp -a "$OUTPUT" "$BACKUP_DIR/$(basename "$OUTPUT").before"

TMP="$(mktemp /boot/.sgtl5000-dtb.XXXXXX)"
trap 'rm -f "$TMP"' EXIT
fdtoverlay -i "$BASE_DTB" -o "$TMP" "$OVERLAY"
chmod 0644 "$TMP"
mv -f "$TMP" "$OUTPUT"

sed -i '\|^LABEL JetsonIO$|,\|^$| s|^[[:space:]]*FDT .*|\tFDT /boot/kernel_tegra194-p3668-0000-p3509-0000-user-custom-sgtl5000.dtb|' "$EXTLINUX"
grep -A6 '^LABEL JetsonIO$' "$EXTLINUX" | grep -F "FDT $OUTPUT" >/dev/null

cp -a "$EXTLINUX" "$BACKUP_DIR/extlinux.conf.after"
sha256sum "$BASE_DTB" "$OVERLAY" "$OUTPUT" >"$BACKUP_DIR/sha256.after.txt"
chown -R "$TARGET_USER:$TARGET_USER" "$BACKUP_DIR"
sync

echo "SGTL5000_DTB_PREPARE=PASS"
echo "OUTPUT=$OUTPUT"
echo "BACKUP_DIR=$BACKUP_DIR"
grep -A6 '^LABEL JetsonIO$' "$EXTLINUX"
