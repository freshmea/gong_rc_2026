#!/usr/bin/env bash
set -euo pipefail

ROOT="${JETSON_WORK_ROOT:-$HOME/jetson-r35.6.4}"
OWNER="${JETSON_OWNER:-${SUDO_USER:-$(id -un)}}"
DOWNLOADS="$ROOT/downloads"
MASTER="$ROOT/master/Linux_for_Tegra"
LANES="$ROOT/lanes"
BSP="$DOWNLOADS/jetson_linux_r35.6.4_aarch64.tbz2"
ROOTFS="$DOWNLOADS/tegra_linux_sample-root-filesystem_r35.6.4_aarch64.tbz2"

verify_rootfs_privileges() {
  local rootfs="$1"
  local path uid gid mode

  for path in usr/bin/sudo usr/bin/passwd bin/su; do
    read -r uid gid mode < <(stat -c '%u %g %a' "$rootfs/$path")
    if [[ "$uid" != 0 || "$gid" != 0 || "$mode" != 4755 ]]; then
      echo "Invalid privileged-file metadata: $rootfs/$path uid=$uid gid=$gid mode=$mode" >&2
      echo "Re-extract the sample rootfs as root; never recursively chown Linux_for_Tegra." >&2
      exit 1
    fi
  done
}

[[ -r "$BSP" && -r "$ROOTFS" ]] || {
  echo "Run 02_download_r3564.sh first." >&2
  exit 1
}

if [[ ! -x "$MASTER/flash.sh" ]]; then
  rm -rf "$ROOT/master"
  mkdir -p "$ROOT/master"
  tar -xpf "$BSP" -C "$ROOT/master"
fi

sudo mkdir -p "$MASTER/rootfs"
if [[ ! -f "$MASTER/rootfs/etc/os-release" ]]; then
  sudo tar -xpf "$ROOTFS" -C "$MASTER/rootfs"
fi

cd "$MASTER"
sudo ./apply_binaries.sh
sudo ./tools/l4t_flash_prerequisites.sh

verify_rootfs_privileges "$MASTER/rootfs"

test -x flash.sh
test -f jetson-xavier-nx-devkit-qspi.conf
grep -q '# R35 (release), REVISION: 6.4' rootfs/etc/nv_tegra_release

mkdir -p "$LANES"
for lane in 1 2 3 4; do
  echo "Preparing isolated lane $lane"
  sudo mkdir -p "$LANES/lane$lane"
  sudo rsync -a --delete --exclude qspi-logs/ "$MASTER/" "$LANES/lane$lane/"
  verify_rootfs_privileges "$LANES/lane$lane/rootfs"
done

# Do not recursively chown $ROOT. The Ubuntu sample rootfs contains files that
# must remain owned by root and setuid (for example sudo, passwd and su).
# Recursive chown also clears their setuid bits and produces an unusable image.

echo "BSP_PREPARE=PASS"
