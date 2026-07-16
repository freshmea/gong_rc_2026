#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SOURCE="${1:-$REPO_ROOT/migration_data/raw/camera_compare/camera_overrides_jetpack5.isp}"
SETTINGS_DIR="/var/nvidia/nvcam/settings"
TARGET="$SETTINGS_DIR/camera_overrides.isp"
STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="/var/backups/gong-rc-camera-$STAMP"

if [[ ! -s "$SOURCE" ]]; then
  echo "ISP override file not found or empty: $SOURCE" >&2
  exit 1
fi

sudo mkdir -p "$SETTINGS_DIR" "$BACKUP_DIR"
if [[ -e "$TARGET" ]]; then
  sudo cp -a "$TARGET" "$BACKUP_DIR/"
fi
if [[ -e "$SETTINGS_DIR/nvcam_cache_0.bin" ]]; then
  sudo cp -a "$SETTINGS_DIR/nvcam_cache_0.bin" "$BACKUP_DIR/"
  sudo rm -f "$SETTINGS_DIR/nvcam_cache_0.bin"
fi

sudo install -o root -g root -m 0644 "$SOURCE" "$TARGET"
sudo systemctl restart nvargus-daemon

echo "ISP_OVERRIDE=$TARGET"
echo "BACKUP_DIR=$BACKUP_DIR"
sha256sum "$SOURCE"
sudo systemctl --no-pager --full status nvargus-daemon | sed -n '1,12p'
