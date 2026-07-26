#!/usr/bin/env bash
set -u

section() { printf '\n### %s\n' "$1"; }

section "platform"
hostname
uname -a
cat /etc/os-release
tr -d '\000' </proc/device-tree/model 2>/dev/null || true
printf '\n'

section "SPI modules and character devices"
lsmod | grep -E '^spidev|^spi_' || true
find /dev -maxdepth 1 -name 'spidev*' -printf '%M %u:%g %t:%T %p\n' 2>/dev/null | sort
find /sys/class/spidev -maxdepth 2 -printf '%p -> %l\n' 2>/dev/null | sort

section "SPI bus devices"
for device in /sys/bus/spi/devices/spi*; do
  [[ -e "$device" ]] || continue
  echo "DEVICE=$device"
  printf 'modalias='; cat "$device/modalias" 2>/dev/null || true
  printf 'compatible='; tr -d '\000' <"$device/of_node/compatible" 2>/dev/null || true; printf '\n'
  printf 'status='; tr -d '\000' <"$device/of_node/status" 2>/dev/null || true; printf '\n'
  printf 'driver='; readlink "$device/driver" 2>/dev/null || echo '<none>'
done

section "automatic module loading"
for file in /etc/modules /etc/modules-load.d/*.conf; do
  [[ -r "$file" ]] || continue
  echo "--- $file"
  sed -n '1,160p' "$file"
done

section "boot DT configuration"
sed -n '1,180p' /boot/extlinux/extlinux.conf 2>/dev/null || true
find /boot -maxdepth 3 -type f \( -name '*.dtb' -o -name '*.dtbo' \) \
  -printf '%s %p\n' 2>/dev/null | sort

section "Jetson-IO enabled functions"
if [[ -f /opt/nvidia/jetson-io/config-by-function.py ]]; then
  python3 /opt/nvidia/jetson-io/config-by-function.py -l enabled 2>&1 || true
fi

section "SPI pinctrl"
find /sys/kernel/debug/pinctrl -type f \( -name pinmux-pins -o -name pinconf-pins \) \
  -print 2>/dev/null | while read -r file; do
    echo "--- $file"
    grep -Ei 'spi|header|pin 19|pin 21|pin 23|pin 24|pin 26' "$file" 2>/dev/null | head -160 || true
  done

section "Python SPI open and transfer"
python3 - <<'PY'
import glob
try:
    import spidev
except Exception as exc:
    print(f"spidev_import=FAIL {type(exc).__name__}: {exc}")
    raise SystemExit(0)

print("spidev_module=" + str(spidev.__file__))
print("nodes=" + repr(glob.glob('/dev/spidev*')))
spi = spidev.SpiDev()
try:
    spi.open(0, 0)
    spi.max_speed_hz = 500_000
    for channel in range(8):
        response = spi.xfer2([6 | (channel >> 2), (channel & 3) << 6, 0])
        value = ((response[1] & 15) << 8) + response[2]
        print(f"channel={channel} response={response} value={value}")
except Exception as exc:
    print(f"spi_test=FAIL {type(exc).__name__}: {exc}")
else:
    print("spi_test=PASS")
finally:
    try:
        spi.close()
    except Exception:
        pass
PY
