#!/usr/bin/env python3
"""Import POP feature modules without constructing hardware controllers."""

import importlib
import sys


failures = 0
for name in ("pop.Pilot", "pop.Util"):
    try:
        module = importlib.import_module(name)
    except BaseException as exc:
        failures += 1
        print(f"POP_FEATURE_IMPORT_FAIL {name} {type(exc).__name__}: {exc}")
    else:
        print(f"POP_FEATURE_IMPORT_PASS {name} {module.__file__}")

sys.exit(1 if failures else 0)
