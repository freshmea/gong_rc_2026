#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: sudo $0 image.img.zst /dev/sdX --yes-really-erase" >&2
  exit 2
}

[[ $# -eq 3 ]] || usage
IMAGE="$(readlink -f "$1")"
TARGET="$(readlink -f "$2")"
[[ "$3" == "--yes-really-erase" ]] || usage
[[ $EUID -eq 0 ]] || { echo "Run with sudo." >&2; exit 1; }
[[ -f "$IMAGE" ]] || { echo "Image not found: $IMAGE" >&2; exit 1; }
[[ -b "$TARGET" ]] || { echo "Not a block device: $TARGET" >&2; exit 1; }
[[ "$(lsblk -dnro TYPE "$TARGET")" == "disk" ]] || { echo "Use the whole target disk." >&2; exit 1; }

ROOT_SOURCE="$(findmnt -nro SOURCE /)"
ROOT_PARENT="/dev/$(lsblk -nro PKNAME "$ROOT_SOURCE" 2>/dev/null | head -n1)"
if [[ "$TARGET" == "$ROOT_SOURCE" || "$TARGET" == "$ROOT_PARENT" ]]; then
  echo "Refusing to erase the host root disk: $TARGET" >&2
  exit 1
fi

if lsblk -nrpo MOUNTPOINT "$TARGET" | grep -q '/'; then
  echo "Unmount every partition on $TARGET first." >&2
  exit 1
fi

command -v zstd >/dev/null || { echo "Install zstd first." >&2; exit 1; }
zstd --test "$IMAGE"

SIZE_FILE="$IMAGE.size"
if [[ -r "$SIZE_FILE" ]]; then
  REQUIRED="$(tr -d '[:space:]' < "$SIZE_FILE")"
  AVAILABLE="$(blockdev --getsize64 "$TARGET")"
  [[ "$REQUIRED" =~ ^[0-9]+$ ]] || { echo "Invalid size file: $SIZE_FILE" >&2; exit 1; }
  if (( AVAILABLE < REQUIRED )); then
    echo "Target is too small: $AVAILABLE bytes, need $REQUIRED bytes." >&2
    exit 1
  fi
fi

echo "ERASING $TARGET from $IMAGE"
zstd -dc "$IMAGE" | dd of="$TARGET" bs=16M conv=fsync status=progress
sync
partprobe "$TARGET" 2>/dev/null || true
echo "RESTORE=PASS"
