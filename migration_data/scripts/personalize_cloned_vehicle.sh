#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || ! "$1" =~ ^[a-z0-9][a-z0-9-]{0,62}$ ]]; then
  echo "Usage: sudo $0 gong-rc-01" >&2
  exit 2
fi
[[ $EUID -eq 0 ]] || { echo "Run with sudo." >&2; exit 1; }

NEW_HOSTNAME="$1"
hostnamectl set-hostname "$NEW_HOSTNAME"

rm -f /etc/ssh/ssh_host_*
ssh-keygen -A

rm -f /var/lib/dbus/machine-id
truncate -s 0 /etc/machine-id
systemd-machine-id-setup
ln -sfn /etc/machine-id /var/lib/dbus/machine-id

echo "HOSTNAME=$NEW_HOSTNAME"
echo "MACHINE_ID=$(cat /etc/machine-id)"
echo "SSH_ED25519=$(ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub)"
echo
echo "Review cloned network profiles for fixed IP addresses:"
nmcli -f NAME,TYPE,DEVICE connection show || true
echo
echo "PERSONALIZE=PASS - reboot before connecting this clone to the fleet LAN."
