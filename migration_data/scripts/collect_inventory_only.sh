#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="${REMOTE_HOST:-192.168.0.34}"
USER_NAME="${REMOTE_USER:-soda}"
PASSWORD="${REMOTE_PASSWORD:?Set REMOTE_PASSWORD before running}"
HOSTKEY="${REMOTE_HOSTKEY:-SHA256:mHxNTNfeG7wgldciHKI0cq5J9fSkswLQVY25+ceIXTI}"
PLINK="${PLINK:-/mnt/c/Program Files/PuTTY/plink.exe}"

mkdir -p "$ROOT/raw/reports" "$ROOT/reports"
"$PLINK" -ssh -batch -hostkey "$HOSTKEY" -pw "$PASSWORD" "$USER_NAME@$HOST" \
  "LC_ALL=C /bin/bash -s" < "$ROOT/scripts/remote_inventory.sh" \
  | python3 "$ROOT/scripts/redact_sensitive.py" > "$ROOT/raw/reports/system_inventory.txt"

date --iso-8601=seconds > "$ROOT/reports/collected_at.txt"
printf 'host=%s\nuser=%s\nhostkey=%s\n' "$HOST" "$USER_NAME" "$HOSTKEY" > "$ROOT/reports/source.txt"
echo "inventory refreshed: $ROOT/raw/reports/system_inventory.txt"

