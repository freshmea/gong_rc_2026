#!/usr/bin/env bash
set -u
echo '=== I2C adapters ==='
i2cdetect -l
for bus in 0 1 8; do
  [ -e "/dev/i2c-$bus" ] || continue
  echo "=== I2C bus $bus (read-byte scan) ==="
  i2cdetect -y -r "$bus" || echo "WARN: bus $bus requires elevated permission or rejected scan"
done

