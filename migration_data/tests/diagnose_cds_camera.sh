#!/usr/bin/env bash
set -u

section() { printf '\n### %s\n' "$1"; }

section "identity"
id
uname -a

section "SPI device nodes"
find /dev -maxdepth 1 -name 'spidev*' -printf '%M %u:%g %p\n' 2>/dev/null | sort
find /sys/class/spidev -maxdepth 2 -printf '%p -> %l\n' 2>/dev/null | sort
find /sys/bus/spi/devices -maxdepth 2 -printf '%p -> %l\n' 2>/dev/null | sort

section "SPI kernel and device tree"
lsmod | grep -Ei 'spi|spidev' || true
if [[ -r /proc/config.gz ]]; then
  zgrep -E '^CONFIG_SPI|^CONFIG_SPI_TEGRA|^CONFIG_SPI_SPIDEV' /proc/config.gz || true
fi
find /proc/device-tree -maxdepth 6 \( -iname '*spi*' -o -iname '*spidev*' \) \
  -print 2>/dev/null | sort | head -100
while IFS= read -r status; do
  printf '%s=' "$status"
  tr -d '\000' <"$status" 2>/dev/null || true
  printf '\n'
done < <(find /proc/device-tree -maxdepth 7 -path '*spi*/status' -type f 2>/dev/null | sort)

section "boot configuration"
grep -RniE 'overlay|spi|dtb' /boot/extlinux /boot/dtb 2>/dev/null | head -160 || true

section "Python SPI"
/home/soda/venvs/gong-rc/bin/python - <<'PY'
import pathlib
import spidev

print("spidev_module=" + str(spidev.__file__))
print("nodes=" + repr([str(p) for p in pathlib.Path('/dev').glob('spidev*')]))
spi = spidev.SpiDev()
try:
    spi.open(0, 0)
except Exception as exc:
    print(f"spidev_open_0_0=FAIL {type(exc).__name__}: {exc}")
else:
    print("spidev_open_0_0=PASS")
    spi.close()
PY

section "Jupyter and display environment"
systemctl show jupyter-gong-rc -p Environment -p User -p Group --no-pager 2>/dev/null || true
printf 'shell_DISPLAY=%s\n' "${DISPLAY-<unset>}"
printf 'shell_XAUTHORITY=%s\n' "${XAUTHORITY-<unset>}"

section "camera devices and service"
find /dev -maxdepth 1 -name 'video*' -printf '%M %u:%g %p\n' 2>/dev/null | sort
systemctl is-active nvargus-daemon 2>/dev/null || true
systemctl --no-pager --full status nvargus-daemon 2>/dev/null | head -35 || true

section "camera calibration assets"
find /home/soda/gong_rc_2026 /home/soda/Project -type f \
  \( -iname '*calib*' -o -iname '*camera*matrix*' -o -iname '*dist*coeff*' \
     -o -iname '*fisheye*' -o -iname '*intrinsic*' \) \
  -print 2>/dev/null | sort | head -200
