#!/usr/bin/env python3
"""Check environment injected by the Jetson IPython startup file."""

import os


expected = {
    "TF_FORCE_GPU_ALLOW_GROWTH": "true",
    "TF_CPP_MIN_LOG_LEVEL": "2",
    "MPLBACKEND": "Agg",
}

for name, value in expected.items():
    actual = os.environ.get(name)
    print(f"{name}={actual}")
    assert actual == value, f"{name}: expected {value!r}, got {actual!r}"

print("TENSORFLOW_KERNEL_DEFAULTS=PASS")
