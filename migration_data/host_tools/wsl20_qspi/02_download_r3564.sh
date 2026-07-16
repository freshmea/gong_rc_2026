#!/usr/bin/env bash
set -euo pipefail

ROOT="${JETSON_WORK_ROOT:-$HOME/jetson-r35.6.4}"
DOWNLOADS="$ROOT/downloads"
mkdir -p "$DOWNLOADS"

BSP_NAME="jetson_linux_r35.6.4_aarch64.tbz2"
ROOTFS_NAME="tegra_linux_sample-root-filesystem_r35.6.4_aarch64.tbz2"
BASE_URL="https://developer.nvidia.com/downloads/embedded/l4t/r35_release_v6.4/release"

download() {
  local name="$1"
  local output="$DOWNLOADS/$name"
  curl --fail --location --continue-at - --retry 5 --retry-delay 5 \
    --output "$output" "$BASE_URL/$name"
}

download "$BSP_NAME"
download "$ROOTFS_NAME"

(
  cd "$DOWNLOADS"
  sha256sum "$BSP_NAME" "$ROOTFS_NAME" > SHA256SUMS.local
)

tar -tjf "$DOWNLOADS/$BSP_NAME" >/dev/null
tar -tjf "$DOWNLOADS/$ROOTFS_NAME" >/dev/null
echo "DOWNLOADS=PASS"
cat "$DOWNLOADS/SHA256SUMS.local"
