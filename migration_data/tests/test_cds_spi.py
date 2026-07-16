#!/usr/bin/env python3
"""Read all MCP3208 channels through the same SPI transaction used by POP."""

import pathlib
import statistics

import spidev


node = pathlib.Path("/dev/spidev0.0")
if not node.exists():
    raise FileNotFoundError(node)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 500_000

try:
    for channel in range(8):
        values = []
        for _ in range(16):
            reply = spi.xfer2([6 | (channel >> 2), (channel & 3) << 6, 0])
            values.append(((reply[1] & 15) << 8) + reply[2])
        print(
            f"channel={channel} min={min(values)} max={max(values)} "
            f"mean={statistics.fmean(values):.1f} values={values[:4]}"
        )
finally:
    spi.close()

print("CDS_SPI_RAW_TEST=PASS")
