#!/usr/bin/env python3
"""Redact common credentials while preserving migration-relevant context."""

import re
import sys


PATTERNS = [
    (re.compile(r"(?i)(https?://)([^/@\s:]+):([^/@\s]+)@"), r"\1[REDACTED]:[REDACTED]@"),
    (re.compile(r"(?i)(--?(?:password|passwd|token|api[-_]?key|secret)(?:=|\s+))([^\s'\"]+)"), r"\1[REDACTED]"),
    (re.compile(r"(?i)\b((?:password|passwd|token|api[-_]?key|secret|client[-_]?secret)\s*[:=]\s*)(['\"]?)([^\s,'\"}]+)\2"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(export\s+)?([A-Z0-9_]*(?:TOKEN|PASSWORD|PASSWD|API_KEY|SECRET)[A-Z0-9_]*=)([^\s]+)"), r"\1\2[REDACTED]"),
    (re.compile(r"(?i)(authorization:\s*(?:bearer|basic)\s+)[^\s]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(c\.NotebookApp\.(?:token|password)\s*=\s*)[^\n]+"), r"\1'[REDACTED]'"),
]


def redact(text: str) -> str:
    for pattern, replacement in PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def main() -> int:
    data = sys.stdin.buffer.read().decode('utf-8', errors='replace')
    sys.stdout.write(redact(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

