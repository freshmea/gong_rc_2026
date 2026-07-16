#!/usr/bin/env bash
set -euo pipefail

ROOT="${JETSON_WORK_ROOT:-$HOME/jetson-r35.6.4}"
echo "DISTRO=$(lsb_release -ds)"
echo "ARCH=$(uname -m)"
echo "FREE=$(df -h "$ROOT" | awk 'NR==2 {print $4}')"
[[ "$(uname -m)" == "x86_64" ]]
grep -q 'Ubuntu 20.04' /etc/os-release

for lane in 1 2 3 4; do
  directory="$ROOT/lanes/lane$lane"
  test -x "$directory/flash.sh"
  test -f "$directory/jetson-xavier-nx-devkit-qspi.conf"
  grep -q '# R35 (release), REVISION: 6.4' "$directory/rootfs/etc/nv_tegra_release"
  echo "LANE_${lane}=PASS"
done

echo "WORKSPACE=PASS"
