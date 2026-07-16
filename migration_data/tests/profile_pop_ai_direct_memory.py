#!/usr/bin/env python3
"""Measure a clean-process direct import of pop.AI."""

import time


def report(label):
    values = {}
    wanted = {"VmRSS", "RssAnon", "RssFile", "RssShmem", "VmSize"}
    with open("/proc/self/status", encoding="ascii") as stream:
        for line in stream:
            name = line.split(":", 1)[0]
            if name in wanted:
                values[name] = line.split(":", 1)[1].strip().replace(" ", "")
    with open("/proc/meminfo", encoding="ascii") as stream:
        for line in stream:
            if line.startswith("MemAvailable:"):
                values["SystemMemAvailable"] = line.split(":", 1)[1].strip().replace(" ", "")
                break
    print(label + " " + " ".join(f"{key}={value}" for key, value in values.items()), flush=True)


report("START")
import pop.AI  # noqa: E402
import tensorflow as tf  # noqa: E402
report("AFTER_POP_AI_DIRECT")
print(f"TENSORFLOW={tf.__version__}", flush=True)
time.sleep(1)
report("FINAL")
