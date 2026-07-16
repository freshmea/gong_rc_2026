#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: sudo $0 /dev/sdX output.img.zst --yes-read-whole-disk" >&2
  exit 2
}

[[ $# -eq 3 ]] || usage
SOURCE="$(readlink -f "$1")"
OUTPUT="$2"
[[ "$3" == "--yes-read-whole-disk" ]] || usage
[[ $EUID -eq 0 ]] || { echo "Run with sudo." >&2; exit 1; }
[[ -b "$SOURCE" ]] || { echo "Not a block device: $SOURCE" >&2; exit 1; }
[[ "$(lsblk -dnro TYPE "$SOURCE")" == "disk" ]] || { echo "Use the whole disk, not a partition." >&2; exit 1; }
[[ ! -e "$OUTPUT" && ! -e "$OUTPUT.size" && ! -e "$OUTPUT.sha256" ]] || { echo "Output already exists." >&2; exit 1; }

ROOT_SOURCE="$(findmnt -nro SOURCE /)"
ROOT_PARENT="/dev/$(lsblk -nro PKNAME "$ROOT_SOURCE" 2>/dev/null | head -n1)"
if [[ "$SOURCE" == "$ROOT_SOURCE" || "$SOURCE" == "$ROOT_PARENT" ]]; then
  echo "Refusing to read the host root disk: $SOURCE" >&2
  exit 1
fi

if lsblk -nrpo MOUNTPOINT "$SOURCE" | grep -q '/'; then
  echo "Unmount every partition on $SOURCE first." >&2
  exit 1
fi

command -v zstd >/dev/null || { echo "Install zstd first." >&2; exit 1; }
SIZE="$(blockdev --getsize64 "$SOURCE")"
printf '%s\n' "$SIZE" > "$OUTPUT.size"

echo "Reading $SOURCE ($SIZE bytes) to $OUTPUT"
dd if="$SOURCE" bs=16M iflag=fullblock status=progress | zstd -T0 -10 -o "$OUTPUT"
zstd --test "$OUTPUT"
(
  cd "$(dirname "$OUTPUT")"
  sha256sum "$(basename "$OUTPUT")"
) > "$OUTPUT.sha256"
echo "BACKUP=PASS"
