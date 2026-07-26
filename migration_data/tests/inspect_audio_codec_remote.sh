#!/usr/bin/env bash
set -u

for host in 192.168.0.34 192.168.0.46; do
    echo "===== HOST=$host ====="
    sshpass -p soda ssh \
        -o UserKnownHostsFile=/dev/null \
        -o StrictHostKeyChecking=no \
        -o ConnectTimeout=8 \
        "soda@$host" 'bash -s' <<'REMOTE'
uname -r
echo '--- I2C codec devices ---'
for d in /sys/bus/i2c/devices/*; do
    if [ -f "$d/name" ]; then
        n=$(cat "$d/name")
        case "$n" in
            *rt56*|*RT56*|*codec*) echo "$d $n" ;;
        esac
    fi
done
echo '--- sound modules ---'
lsmod | grep -Ei 'rt56|snd_soc' | head -n 100 || true
echo '--- external-codec mixer controls ---'
amixer -c 1 scontrols | grep -Ei 'Capture Mux|Mic|PCM|Headphone|codec-x' || true
echo '--- DT RT5658 files ---'
find /proc/device-tree -type f -print0 2>/dev/null \
    | xargs -0 grep -IailE 'realtek,rt5658|rt5659' 2>/dev/null \
    | head -n 30 || true
echo '--- kernel log ---'
dmesg 2>/dev/null | grep -Ei 'rt565|codec|asoc|i2s5' | tail -n 100 || true
REMOTE
done
