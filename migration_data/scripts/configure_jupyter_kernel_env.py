#!/usr/bin/env python3
"""Apply Jetson library and GPU settings to the installed Jupyter kernels."""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--home", default="/home/soda")
    parser.add_argument("--venv", default="/home/soda/venvs/gong-rc")
    args = parser.parse_args()

    home = Path(args.home)
    venv = Path(args.venv)
    candidates = glob.glob(
        str(
            venv
            / "lib/python3.8/site-packages/scikit_learn.libs/libgomp*.so*"
        )
    )
    if len(candidates) != 1:
        raise SystemExit(f"expected one scikit-learn libgomp, found {candidates}")

    preload = f"{candidates[0]}:/usr/lib/aarch64-linux-gnu/libGLdispatch.so.0"
    kernel_files = [
        venv / "share/jupyter/kernels/python3/kernel.json",
        home / ".local/share/jupyter/kernels/gong-rc/kernel.json",
    ]
    settings = {
        "LD_PRELOAD": preload,
        "LD_LIBRARY_PATH": "/usr/local/cuda/lib64",
        "TF_FORCE_GPU_ALLOW_GROWTH": "true",
        "TF_CPP_MIN_LOG_LEVEL": "2",
        "XLA_FLAGS": "--xla_gpu_cuda_data_dir=/usr/local/cuda-11.4",
        "MPLBACKEND": "Agg",
        "OPENCV_LOG_LEVEL": "ERROR",
    }

    changed = 0
    for kernel_file in kernel_files:
        if not kernel_file.is_file():
            raise SystemExit(f"kernel spec missing: {kernel_file}")
        with kernel_file.open("r", encoding="utf-8") as stream:
            spec = json.load(stream)
        spec.setdefault("env", {}).update(settings)
        temporary = kernel_file.with_suffix(".json.tmp")
        with temporary.open("w", encoding="utf-8") as stream:
            json.dump(spec, stream, indent=1, ensure_ascii=False)
            stream.write("\n")
        temporary.replace(kernel_file)
        changed += 1
        print(f"KERNEL_ENV_UPDATED={kernel_file}")

    print(f"JUPYTER_KERNEL_ENV=PASS kernels={changed}")
    print(f"LD_PRELOAD={preload}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
