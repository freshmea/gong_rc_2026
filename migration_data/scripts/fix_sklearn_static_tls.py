#!/usr/bin/env python3
"""Relink aarch64 scikit-learn wheel extensions to the system libgomp.

Some aarch64 wheels rename and bundle libgomp. Loading that second OpenMP
runtime after TensorFlow can exhaust glibc's static TLS block on Jetson.
"""

import argparse
import datetime as dt
import json
import pathlib
import shutil
import subprocess
import sysconfig
import tarfile


def needed(path):
    result = subprocess.run(
        ["patchelf", "--print-needed", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--site-packages",
        type=pathlib.Path,
        default=pathlib.Path(sysconfig.get_paths()["purelib"]),
    )
    parser.add_argument("--backup-dir", type=pathlib.Path)
    args = parser.parse_args()

    if shutil.which("patchelf") is None:
        raise SystemExit("patchelf is required")

    site = args.site_packages.resolve()
    sklearn = site / "sklearn"
    bundled = site / "scikit_learn.libs"
    if not sklearn.is_dir():
        raise SystemExit(f"scikit-learn not found under {site}")

    candidates = sorted(sklearn.rglob("*.so"))
    affected = []
    replacements = {}
    for extension in candidates:
        old_names = [
            name
            for name in needed(extension)
            if name.startswith("libgomp-") and name != "libgomp.so.1"
        ]
        if old_names:
            affected.append(extension)
            replacements[str(extension)] = old_names

    if not affected:
        print("SKLEARN_TLS_PATCH=ALREADY_OK")
        return

    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = args.backup_dir or (site.parent.parent.parent / ".migration_backups")
    backup_dir.mkdir(parents=True, exist_ok=True)
    archive = backup_dir / f"sklearn_static_tls_{stamp}.tar.gz"
    manifest = backup_dir / f"sklearn_static_tls_{stamp}.json"

    bundled_libs = sorted(bundled.glob("libgomp-*.so*"))
    with tarfile.open(archive, "w:gz") as output:
        for path in affected + bundled_libs:
            output.add(path, arcname=path.relative_to(site))

    manifest.write_text(
        json.dumps(
            {
                "site_packages": str(site),
                "archive": str(archive),
                "extensions": replacements,
                "replacement": "libgomp.so.1",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    for extension in affected:
        for old_name in replacements[str(extension)]:
            subprocess.run(
                [
                    "patchelf",
                    "--replace-needed",
                    old_name,
                    "libgomp.so.1",
                    str(extension),
                ],
                check=True,
            )

    remaining = []
    for extension in affected:
        remaining.extend(
            name for name in needed(extension) if name.startswith("libgomp-")
        )
    if remaining:
        raise SystemExit(f"unpatched libgomp dependencies remain: {remaining}")

    print(f"SKLEARN_TLS_PATCH=PASS extensions={len(affected)}")
    print(f"BACKUP={archive}")
    print(f"MANIFEST={manifest}")


if __name__ == "__main__":
    main()
