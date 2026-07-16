#!/usr/bin/env bash
set -Eeuo pipefail

TARGET_USER="${TARGET_USER:-soda}"
TARGET_HOME="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
VENV="${VENV:-$TARGET_HOME/venvs/gong-rc}"
POP_PARENT="${POP_PARENT:-$TARGET_HOME/gong_rc_2026/autocar}"

if [[ $EUID -ne 0 ]]; then
  echo "Run as root" >&2
  exit 1
fi
if [[ ! -f "$POP_PARENT/pop/__init__.py" ]]; then
  echo "pop source not found: $POP_PARENT/pop/__init__.py" >&2
  exit 1
fi
if [[ ! -x "$VENV/bin/python" ]]; then
  echo "Python environment not found: $VENV" >&2
  exit 1
fi

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y python3-smbus

sudo -H -u "$TARGET_USER" "$VENV/bin/python" -m pip install --upgrade \
  spidev bme680 adafruit-blinka adafruit-circuitpython-neopixel-spi python-can

SITE_PACKAGES="$($VENV/bin/python - <<'PY'
import site
print(site.getsitepackages()[0])
PY
)"
printf '%s\n' "$POP_PARENT" >"$SITE_PACKAGES/gong_rc_pop_source.pth"
chown "$TARGET_USER:$TARGET_USER" "$SITE_PACKAGES/gong_rc_pop_source.pth"
chmod 0644 "$SITE_PACKAGES/gong_rc_pop_source.pth"

sudo -H -u "$TARGET_USER" env \
  LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libGLdispatch.so.0:/usr/lib/aarch64-linux-gnu/libgomp.so.1 \
  "$VENV/bin/python" - <<'PY'
import pathlib
import pop

path = pathlib.Path(pop.__file__).resolve()
print("POP_IMPORT=PASS")
print("POP_PATH=" + str(path))
print("POP_CATEGORY=" + str(getattr(pop, "_cat", "unknown")))
PY

echo "install_pop_source complete"
