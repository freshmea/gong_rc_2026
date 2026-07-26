#!/usr/bin/env python3
"""Execute the real a21 notebook with long loops shortened in a temp copy."""

from __future__ import annotations

import glob
import json
import os
from pathlib import Path
import subprocess
import sys


def main() -> int:
    source = Path(
        "/home/soda/Project/python/notebook/gong_rc_2026/a21_dqn.ipynb"
    )
    temporary = Path("/tmp/gong_rc_a21_smoke_input.ipynb")
    output = Path("/tmp/gong_rc_a21_smoke_output.ipynb")
    with source.open("r", encoding="utf-8") as stream:
        notebook = json.load(stream)

    replacements = 0
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        updated = []
        for line in cell.get("source", []):
            changed = line.replace("range(1000)", "range(5)")
            replacements += changed != line
            updated.append(changed)
        cell["source"] = updated
        cell["outputs"] = []
        cell["execution_count"] = None
    if replacements < 2:
        raise SystemExit(f"expected two long loops, changed {replacements}")

    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(notebook, stream, ensure_ascii=False)
    output.unlink(missing_ok=True)

    private_gomp = glob.glob(
        "/home/soda/venvs/gong-rc/lib/python3.8/"
        "site-packages/scikit_learn.libs/libgomp*.so*"
    )
    if len(private_gomp) != 1:
        raise SystemExit(f"scikit-learn libgomp not found: {private_gomp}")
    env = os.environ.copy()
    env.update(
        {
            "LD_PRELOAD": private_gomp[0]
            + ":/usr/lib/aarch64-linux-gnu/libGLdispatch.so.0",
            "LD_LIBRARY_PATH": "/usr/local/cuda/lib64",
            "TF_FORCE_GPU_ALLOW_GROWTH": "true",
            "TF_CPP_MIN_LOG_LEVEL": "2",
            "MPLBACKEND": "Agg",
            "SDL_VIDEODRIVER": "dummy",
            "SDL_AUDIODRIVER": "dummy",
        }
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to=notebook",
            "--execute",
            "--ExecutePreprocessor.timeout=180",
            "--output-dir=/tmp",
            "--output=gong_rc_a21_smoke_output",
            str(temporary),
        ],
        check=True,
        timeout=220,
        env=env,
    )

    with output.open("r", encoding="utf-8") as stream:
        executed = json.load(stream)
    errors = [
        result
        for cell in executed.get("cells", [])
        for result in cell.get("outputs", [])
        if result.get("output_type") == "error"
    ]
    if errors:
        raise SystemExit(f"a21 smoke errors: {errors}")
    print(
        "A21_NOTEBOOK_SMOKE=PASS "
        f"cells={len(executed.get('cells', []))} errors=0 loops=5"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
