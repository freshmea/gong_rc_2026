#!/usr/bin/env python3
"""Regression test for optimizer isolation and repeated DNN construction."""

import gc
import os

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("MPLBACKEND", "Agg")


def rss_mb():
    with open("/proc/self/status", encoding="ascii") as stream:
        for line in stream:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    raise RuntimeError("VmRSS not found")


from pop import AI

AI.configure("cpu")
DNN = AI.DNN

import numpy as np
import tensorflow as tf

X = np.array([[-1.0], [0.0], [1.0]], dtype=np.float32)
Y = np.eye(3, dtype=np.float32)

# Two live models must not share stateful TF 2.12 optimizers.
first = DNN(input_size=1, hidden_size=4, output_size=3, layer_level=1)
second = DNN(input_size=1, hidden_size=4, output_size=3, layer_level=1)
assert first.optimizer is not second.optimizer
first.model.fit(X, Y, epochs=1, verbose=0)
second.model.fit(X, Y, epochs=1, verbose=0)
print("DISTINCT_OPTIMIZERS=PASS")
del first, second
tf.keras.backend.clear_session()
gc.collect()

rss_values = []
optimizer_ids = set()
for index in range(10):
    model = DNN(input_size=1, hidden_size=4, output_size=3, layer_level=1)
    optimizer_ids.add(id(model.optimizer))
    model.model.fit(X, Y, epochs=1, verbose=0)
    rss_values.append(rss_mb())
    print(f"ITERATION={index + 1} RSS_MB={rss_values[-1]:.1f}")
    del model
    tf.keras.backend.clear_session()
    gc.collect()

assert len(optimizer_ids) == 10
growth = rss_values[-1] - rss_values[0]
print(f"RSS_GROWTH_AFTER_FIRST_MB={growth:.1f}")
# TensorFlow retains bounded tracing/allocator caches, but model variables and
# optimizer slots must not cause unbounded multi-GB growth.
assert growth < 256.0, f"repeated-model RSS growth is too high: {growth:.1f} MB"
print("POP_AI_REPEATED_MODELS=PASS")
