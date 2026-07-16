#!/usr/bin/env python3
"""Measure host/unified-memory use at POP AI/TensorFlow initialization stages."""

import argparse
import os
import time


def proc_memory():
    wanted = {"VmRSS", "RssAnon", "RssFile", "RssShmem", "VmSize"}
    result = {}
    with open("/proc/self/status", encoding="ascii") as stream:
        for line in stream:
            name = line.split(":", 1)[0]
            if name in wanted:
                result[name] = line.split(":", 1)[1].strip()
    with open("/proc/meminfo", encoding="ascii") as stream:
        for line in stream:
            if line.startswith("MemAvailable:"):
                result["SystemMemAvailable"] = line.split(":", 1)[1].strip()
                break
    return result


def report(label):
    values = proc_memory()
    print(label + " " + " ".join(f"{key}={value.replace(' ', '')}" for key, value in values.items()), flush=True)


parser = argparse.ArgumentParser()
parser.add_argument(
    "stage",
    choices=("baseline", "numpy", "tensorflow", "ai", "softmax", "fit"),
)
parser.add_argument("--hold", type=float, default=1.0)
args = parser.parse_args()

report("START")

if args.stage in {"numpy", "tensorflow", "ai", "softmax", "fit"}:
    import numpy as np

    report("AFTER_NUMPY")

if args.stage in {"tensorflow", "ai", "softmax", "fit"}:
    import tensorflow as tf

    report("AFTER_TENSORFLOW")
    print(f"TENSORFLOW={tf.__version__}", flush=True)

if args.stage == "ai":
    import pop.AI

    report("AFTER_POP_AI")

if args.stage in {"softmax", "fit"}:
    model = tf.keras.Sequential(
        [tf.keras.layers.Dense(3, input_shape=[1], activation="softmax")]
    )
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.05),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    report("AFTER_SOFTMAX_MODEL")

    if args.stage == "fit":
        X = np.array([73, 62, 83, 110, 139, 123, 177, 159, 182], dtype=np.float32).reshape(-1, 1)
        Y = np.eye(3, dtype=np.float32).repeat(3, axis=0)
        X = (X - X.mean()) / X.std()
        model.fit(X, Y, epochs=1, verbose=0)
        report("AFTER_FIT_ONE_EPOCH")

time.sleep(args.hold)
report("FINAL")
