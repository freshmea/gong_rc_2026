#!/usr/bin/env python3
"""Validate the migrated POP package without commanding actuators."""

import pathlib

import pop


path = pathlib.Path(pop.__file__).resolve()
print("POP_IMPORT=PASS")
print("POP_PATH=" + str(path))
print("POP_CATEGORY=" + str(getattr(pop, "_cat", "unknown")))
for name in ("Camera", "Audio", "PixelDisplay", "checkI2C"):
    print(f"POP_SYMBOL {name}={hasattr(pop, name)}")
