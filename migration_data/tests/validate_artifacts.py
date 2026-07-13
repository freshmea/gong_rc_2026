#!/usr/bin/env python3
"""Validate copied notebooks and Python files without executing hardware code."""

import ast
import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
hardware_terms = (
    "GPIO", "i2c", "smbus", "rplidar", "pyaudio", "arecord", "aplay",
    "motor", "servo", "camera", "VideoCapture", "can.interface"
)


def validate_notebook(path: pathlib.Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data.get("cells"), list), "missing cells"
    syntax_errors = []
    hardware_cells = 0
    for index, cell in enumerate(data["cells"]):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        if any(term.lower() in source.lower() for term in hardware_terms):
            hardware_cells += 1
        filtered = "\n".join(
            line for line in source.splitlines()
            if not line.lstrip().startswith(("%", "!"))
        )
        if not filtered.strip():
            continue
        try:
            ast.parse(filtered, filename=str(path))
        except SyntaxError as exc:
            syntax_errors.append((index, exc.lineno, exc.msg))
    return hardware_cells, syntax_errors


def main() -> int:
    notebooks = sorted(ARTIFACTS.rglob("*.ipynb"))
    py_files = sorted(ARTIFACTS.rglob("*.py"))
    failures = 0
    hardware_notebooks = 0

    for path in notebooks:
        try:
            hardware_cells, errors = validate_notebook(path)
            hardware_notebooks += bool(hardware_cells)
            if errors:
                failures += 1
                print("WARN_NOTEBOOK_SYNTAX", path.relative_to(ROOT), errors[:5])
        except Exception as exc:
            failures += 1
            print("FAIL_NOTEBOOK", path.relative_to(ROOT), type(exc).__name__, exc)

    py_syntax_failures = 0
    for path in py_files:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (UnicodeDecodeError, SyntaxError) as exc:
            py_syntax_failures += 1
            print("WARN_PYTHON_SYNTAX", path.relative_to(ROOT), type(exc).__name__, exc)

    print("notebooks=%d hardware_notebooks=%d notebook_failures=%d" % (
        len(notebooks), hardware_notebooks, failures))
    print("python_files=%d python_syntax_warnings=%d" % (len(py_files), py_syntax_failures))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

