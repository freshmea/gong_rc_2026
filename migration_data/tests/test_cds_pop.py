#!/usr/bin/env python3
"""Validate the POP Cds class after SPI1 pinmux configuration."""

import statistics

from pop import Cds


cds = Cds(7)
raw = [cds.read() for _ in range(32)]
if not any(raw):
    raise RuntimeError("Cds channel 7 returned only zero values")

print(
    f"CDS_RAW=PASS min={min(raw)} max={max(raw)} "
    f"mean={statistics.fmean(raw):.1f}"
)
print(f"CDS_PSEUDO_LUX={cds.readAverage()}")
print("CDS_POP_TEST=PASS")
