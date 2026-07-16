#!/usr/bin/env python3
"""Verify that ten concurrent POP AI imports stay lightweight."""

import argparse
import os
import subprocess
import sys
import time


def rss_kb(pid):
    with open(f"/proc/{pid}/status", encoding="ascii") as stream:
        for line in stream:
            if line.startswith("VmRSS:"):
                return int(line.split()[1])
    raise RuntimeError(f"VmRSS not found for PID {pid}")


parser = argparse.ArgumentParser()
parser.add_argument("--child", action="store_true")
args = parser.parse_args()

if args.child:
    from pop import AI

    assert not AI.is_loaded()
    assert "tensorflow" not in sys.modules
    print("READY", flush=True)
    time.sleep(30)
    raise SystemExit(0)

children = []
try:
    for _ in range(10):
        children.append(
            subprocess.Popen(
                [sys.executable, __file__, "--child"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )

    for child in children:
        marker = child.stdout.readline().strip()
        assert marker == "READY", child.stderr.read()

    rss_values = [rss_kb(child.pid) / 1024 for child in children]
    print("RSS_MB=" + ",".join(f"{value:.1f}" for value in rss_values))
    print(f"TOTAL_RSS_MB={sum(rss_values):.1f}")
    assert max(rss_values) < 256.0
    assert sum(rss_values) < 2560.0
    print("POP_AI_TEN_IMPORTS=PASS")
finally:
    for child in children:
        child.terminate()
    for child in children:
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            child.kill()
