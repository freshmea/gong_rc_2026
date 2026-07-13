#!/usr/bin/env bash
# Camera inventory only by default; does not open a sensor stream.
set -u

echo '=== camera device nodes ==='
find /dev -maxdepth 1 -name 'video*' -printf '%M %u:%g %p\n' 2>/dev/null | sort || true

echo '=== V4L2 inventory ==='
if command -v v4l2-ctl >/dev/null 2>&1; then
  v4l2-ctl --list-devices 2>/dev/null || true
else
  echo 'WARN: v4l2-ctl is not installed'
fi

echo '=== NVIDIA Argus ==='
if systemctl is-active --quiet nvargus-daemon; then
  echo 'PASS: nvargus-daemon active'
else
  echo 'WARN: nvargus-daemon inactive or unavailable'
fi

python3 - <<'PY'
import cv2
print('PASS: cv2 import', cv2.__version__)
print('GStreamer:', 'YES' if 'GStreamer:                   YES' in cv2.getBuildInformation() else 'inspect build information')
PY
