#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  abootimg bc binfmt-support bzip2 ca-certificates cpio curl \
  device-tree-compiler dosfstools git lbzip2 libxml2-utils \
  nfs-kernel-server openssh-client python3 python3-yaml \
  qemu-user-static rsync sshpass tar usbutils util-linux wget xxd zstd

echo "HOST_DEPENDENCIES=PASS"
