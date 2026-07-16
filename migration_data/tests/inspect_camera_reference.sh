#!/usr/bin/env bash
set -u

section() { printf '\n### %s\n' "$1"; }

section "platform"
hostname
uname -a
cat /etc/os-release

section "OpenCV and GStreamer"
if [[ -x /home/soda/venvs/gong-rc/bin/python ]]; then
  PYTHON=/home/soda/venvs/gong-rc/bin/python
else
  PYTHON=python3
fi
"$PYTHON" - <<'PY'
import cv2
print('cv2=' + cv2.__version__)
for line in cv2.getBuildInformation().splitlines():
    if 'GStreamer' in line or 'Video I/O' in line:
        print(line)
PY
gst-launch-1.0 --version 2>/dev/null || true
gst-inspect-1.0 nvarguscamerasrc 2>/dev/null | sed -n '1,260p' || true

section "Argus and camera service"
systemctl cat nvargus-daemon 2>/dev/null || true
systemctl --no-pager --full status nvargus-daemon 2>/dev/null | head -80 || true
journalctl -u nvargus-daemon -b --no-pager 2>/dev/null | grep -Ei 'override|sensor|module|imager|error|warning' | tail -120 || true

section "ISP and camera configuration files"
for root in /var/nvidia/nvcam /etc/nvcam /etc/nvidia /usr/share/camera /opt/nvidia; do
  [[ -e "$root" ]] || continue
  find "$root" -maxdepth 7 -type f \
    \( -iname '*.isp' -o -iname '*camera*' -o -iname '*argus*' \
       -o -iname '*imx219*' -o -iname '*imx477*' -o -iname '*nvcam*' \) \
    -printf '%s %p\n' 2>/dev/null | sort
done

section "ISP file checksums"
find /var/nvidia/nvcam /etc/nvcam /etc/nvidia -type f \
  \( -iname '*.isp' -o -iname '*override*' \) -print0 2>/dev/null \
  | xargs -0 -r sha256sum

section "Device Tree camera modules"
find /proc/device-tree -maxdepth 10 -type f \
  \( -name badge -o -name position -o -name status -o -name compatible \
     -o -name sensor_model -o -name devname \) -print 2>/dev/null \
  | grep -Ei 'camera|imx|tegra-camera|module[0-9]' \
  | while read -r file; do
      printf '%s=' "$file"
      tr -d '\000' <"$file" 2>/dev/null || true
      printf '\n'
    done

section "Video devices"
v4l2-ctl --list-devices 2>/dev/null || true
v4l2-ctl -d /dev/video0 --all 2>/dev/null || true
