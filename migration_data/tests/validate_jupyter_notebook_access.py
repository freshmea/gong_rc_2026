#!/usr/bin/env python3
"""Check Jupyter visibility and execute one non-hardware lesson as a smoke test."""

from __future__ import annotations

import argparse
import glob
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from jupyter_server.services.contents.filemanager import FileContentsManager


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", default="/home/soda/Project/python/notebook"
    )
    parser.add_argument("--folder", default="gong_rc_2026")
    parser.add_argument(
        "--smoke-notebook", default="a14_linear_regresstion.ipynb"
    )
    args = parser.parse_args()

    root = Path(args.root)
    manager = FileContentsManager(root_dir=str(root))
    model = manager.get(args.folder, content=True)
    if model.get("type") != "directory":
        raise SystemExit(f"Jupyter model is not a directory: {model}")
    item_count = len(model.get("content") or [])
    if item_count == 0:
        raise SystemExit("Jupyter returned an empty notebook folder")
    print(f"JUPYTER_CONTENTS=PASS items={item_count}")

    notebook = root / args.folder / args.smoke_notebook
    if not notebook.is_file():
        raise SystemExit(f"smoke notebook missing: {notebook}")
    output = Path("/tmp/gong_rc_a14_linear_smoke.ipynb")
    smoke_input = Path("/tmp/gong_rc_a14_linear_input.ipynb")
    output.unlink(missing_ok=True)
    smoke_input.unlink(missing_ok=True)
    shutil.copy2(notebook, smoke_input)

    env = os.environ.copy()
    private_gomp = glob.glob(
        "/home/soda/venvs/gong-rc/lib/python3.8/"
        "site-packages/scikit_learn.libs/libgomp*.so*"
    )
    if len(private_gomp) != 1:
        raise SystemExit(f"scikit-learn libgomp not found: {private_gomp}")
    env["LD_PRELOAD"] = (
        private_gomp[0] + ":/usr/lib/aarch64-linux-gnu/libGLdispatch.so.0"
    )
    env["LD_LIBRARY_PATH"] = "/usr/local/cuda/lib64"
    env.setdefault("MPLBACKEND", "Agg")
    env.setdefault("TF_FORCE_GPU_ALLOW_GROWTH", "true")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to=notebook",
            "--execute",
            "--ExecutePreprocessor.timeout=120",
            "--output-dir=/tmp",
            "--output=gong_rc_a14_linear_smoke",
            str(smoke_input),
        ],
        check=True,
        timeout=180,
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
        raise SystemExit(f"smoke notebook errors: {errors}")
    print(
        "A14_NOTEBOOK_EXECUTION=PASS "
        f"cells={len(executed.get('cells', []))} errors=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
