#!/usr/bin/env python3
"""Non-destructive import and accelerator inventory for the migrated Jetson."""

from __future__ import annotations

import importlib
import platform
import sys


MODULES = (
    "numpy",
    "scipy",
    "pandas",
    "matplotlib",
    "sklearn",
    "PIL",
    "cv2",
    "tensorrt",
    "vpi",
    "onnx",
    "jupyterlab",
    "serial",
    "smbus2",
    "rplidar",
    "pyaudio",
    "sounddevice",
    "Jetson.GPIO",
    "RPi.GPIO",
)


def version_of(module: object) -> str:
    return str(getattr(module, "__version__", getattr(module, "VERSION", "unknown")))


def main() -> int:
    print(f"PYTHON={sys.version.split()[0]}")
    print(f"PLATFORM={platform.platform()}")
    failures: list[str] = []
    loaded: dict[str, object] = {}

    for name in MODULES:
        try:
            module = importlib.import_module(name)
            loaded[name] = module
            print(f"IMPORT_PASS {name} {version_of(module)}")
        except BaseException as exc:
            failures.append(name)
            print(f"IMPORT_FAIL {name} {type(exc).__name__}: {exc}")

    cv2 = loaded.get("cv2")
    if cv2 is not None:
        try:
            count = cv2.cuda.getCudaEnabledDeviceCount()
        except BaseException as exc:
            print(f"OPENCV_CUDA_QUERY_WARN {type(exc).__name__}: {exc}")
        else:
            print(f"OPENCV_CUDA_DEVICE_COUNT={count}")
        build = cv2.getBuildInformation()
        print("OPENCV_GSTREAMER=" + ("YES" if "GStreamer:                   YES" in build else "NO_OR_UNKNOWN"))

    try:
        torch = importlib.import_module("torch")
    except BaseException as exc:
        print(f"OPTIONAL_IMPORT_MISSING torch {type(exc).__name__}: {exc}")
    else:
        print(f"OPTIONAL_IMPORT_PASS torch {version_of(torch)}")
        print(f"TORCH_CUDA_AVAILABLE={torch.cuda.is_available()}")
        print(f"TORCH_CUDA_VERSION={torch.version.cuda}")

    if failures:
        print("REQUIRED_IMPORT_FAILURES=" + ",".join(failures))
        return 1
    print("PYTHON_STACK_TEST=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
