#!/usr/bin/env bash
set -Eeuo pipefail

TARGET_USER="${TARGET_USER:-soda}"
TARGET_HOME="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
SOURCE="${SOURCE:-$TARGET_HOME/gong_rc_2026/autocar/jupyter_source}"
TARGET="${TARGET:-$TARGET_HOME/Project/python/notebook/gong_rc_2026}"
BACKUP_ROOT="${BACKUP_ROOT:-$TARGET_HOME/Project/python/notebook/.migration_backups}"
VALIDATOR="$TARGET_HOME/gong_rc_2026/migration_data/tests/validate_notebook_bundle.py"
PYTHON="$TARGET_HOME/venvs/gong-rc/bin/python"

if [[ ! -d "$SOURCE" ]]; then
  echo "Notebook source missing: $SOURCE" >&2
  exit 1
fi
if [[ ! -x "$PYTHON" || ! -f "$VALIDATOR" ]]; then
  echo "Notebook validator or teaching Python missing" >&2
  exit 1
fi

install -d -o "$TARGET_USER" -g "$TARGET_USER" "$TARGET"
STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP="$BACKUP_ROOT/gong_rc_2026_$STAMP"
install -d -o "$TARGET_USER" -g "$TARGET_USER" "$BACKUP"
rsync -a --checksum --backup --backup-dir="$BACKUP" "$SOURCE/" "$TARGET/"
chown -R "$TARGET_USER:$TARGET_USER" "$TARGET"
chown -R "$TARGET_USER:$TARGET_USER" "$BACKUP_ROOT"

if find "$BACKUP" -type f -print -quit | grep -q .; then
  echo "NOTEBOOK_CHANGED_FILES_BACKUP=$BACKUP"
else
  rmdir "$BACKUP"
fi

sudo -H -u "$TARGET_USER" "$PYTHON" "$VALIDATOR" \
  --source "$SOURCE" --target "$TARGET"
echo "NOTEBOOK_BUNDLE_DEPLOY=PASS target=$TARGET"
