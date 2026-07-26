#!/usr/bin/env python3
"""Validate that the deployed Gong RC notebook bundle matches its source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def files_under(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file()
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        default="/home/soda/gong_rc_2026/autocar/jupyter_source",
    )
    parser.add_argument(
        "--target",
        default="/home/soda/Project/python/notebook/gong_rc_2026",
    )
    args = parser.parse_args()

    source = Path(args.source)
    target = Path(args.target)
    if not source.is_dir() or not target.is_dir():
        raise SystemExit(f"missing directory: source={source} target={target}")

    source_files = files_under(source)
    target_files = files_under(target)
    missing = sorted(source_files.keys() - target_files.keys())
    extra = sorted(target_files.keys() - source_files.keys())
    if missing:
        raise SystemExit(f"bundle files missing: {missing}")

    mismatched = []
    manifest = hashlib.sha256()
    for relative in sorted(source_files):
        source_hash = digest(source_files[relative])
        target_hash = digest(target_files[relative])
        if source_hash != target_hash:
            mismatched.append(relative)
        manifest.update(relative.encode("utf-8"))
        manifest.update(b"\0")
        manifest.update(source_hash.encode("ascii"))
        manifest.update(b"\n")
    if mismatched:
        raise SystemExit(f"bundle hash mismatch: {mismatched}")

    notebooks = sorted(target.glob("*.ipynb"))
    for notebook in notebooks:
        with notebook.open("r", encoding="utf-8") as stream:
            document = json.load(stream)
        if document.get("nbformat") not in (4,):
            raise SystemExit(f"unsupported notebook format: {notebook.name}")
        if not isinstance(document.get("cells"), list):
            raise SystemExit(f"notebook has no cell list: {notebook.name}")

    required = {f"a{number:02d}" for number in range(1, 31)}
    present = {path.name.split("_", 1)[0] for path in notebooks}
    missing_lessons = sorted(required - present)
    if missing_lessons:
        raise SystemExit(f"missing numbered lessons: {missing_lessons}")

    print("NOTEBOOK_BUNDLE_VALIDATION=PASS")
    print(f"source_files_verified={len(source_files)}")
    print(f"notebooks={len(notebooks)}")
    print(f"generated_extra_files={len(extra)}")
    if extra:
        print("generated_extra_paths=" + ",".join(extra))
    print(f"manifest_sha256={manifest.hexdigest()}")
    print(f"target={target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
