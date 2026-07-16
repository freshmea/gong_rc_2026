#!/usr/bin/env bash
set -Eeuo pipefail

TARGET_USER="${TARGET_USER:-soda}"
TARGET_HOME="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
VENV="${VENV:-$TARGET_HOME/venvs/gong-rc}"
DEB="${1:-}"

if [[ $EUID -ne 0 ]]; then
  echo "Run as root" >&2
  exit 1
fi
if [[ -z "$DEB" || ! -f "$DEB" ]]; then
  echo "Usage: $0 /path/to/gong-rc-pop_VERSION_arm64.deb" >&2
  exit 1
fi
if [[ ! -x "$VENV/bin/python" ]]; then
  echo "Python environment not found: $VENV" >&2
  exit 1
fi

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y "$DEB"

sudo -H -u "$TARGET_USER" "$VENV/bin/python" -m pip install --upgrade \
  spidev bme680 adafruit-blinka adafruit-circuitpython-neopixel-spi python-can

if [[ "${INSTALL_AI_DEPS:-1}" = "1" ]]; then
  /usr/bin/gong-rc-pop-install-ai
fi

PTH="$VENV/lib/python3.8/site-packages/gong_rc_pop_source.pth"
if [[ -f "$PTH" ]]; then
  mv "$PTH" "$PTH.disabled"
fi

sudo -H -u "$TARGET_USER" env \
  LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libGLdispatch.so.0:/usr/lib/aarch64-linux-gnu/libgomp.so.1 \
  "$VENV/bin/python" - <<'PY'
import pathlib
import pop

path = pathlib.Path(pop.__file__).resolve()
assert str(path).startswith('/usr/lib/python3/dist-packages/pop/'), path
print('POP_DEB_IMPORT=PASS')
print('POP_PATH=' + str(path))
print('POP_CATEGORY=' + str(getattr(pop, '_cat', 'unknown')))
PY

dpkg-query -W -f='${Status} ${Version}\n' gong-rc-pop
