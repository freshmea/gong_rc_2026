#!/usr/bin/env python3
"""Validate lazy POP AI import and its CPU/GPU device policy."""

import argparse
import os
import sys


def rss_mb():
    with open("/proc/self/status", encoding="ascii") as stream:
        for line in stream:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    raise RuntimeError("VmRSS not found")


parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=("import", "cpu", "gpu"))
args = parser.parse_args()

print(f"START_RSS_MB={rss_mb():.1f}")
from pop import AI

print(f"AFTER_AI_IMPORT_RSS_MB={rss_mb():.1f}")
print(f"AI_MODULE={AI.__file__}")
assert "tensorflow" not in sys.modules, "TensorFlow loaded during lightweight AI import"
assert not AI.is_loaded()
print("TENSORFLOW_LAZY_IMPORT=PASS")

if args.mode == "import":
    raise SystemExit(0)

AI.configure(args.mode)
DNN = AI.DNN

import numpy as np
import tensorflow as tf

print(f"AFTER_AI_LOAD_RSS_MB={rss_mb():.1f}")
print(f"DEVICE_POLICY={AI.device_policy()}")
print(f"VISIBLE_GPUS={len(tf.config.get_visible_devices('GPU'))}")

if args.mode == "cpu":
    assert not tf.config.get_visible_devices("GPU")
else:
    assert tf.config.get_visible_devices("GPU")

model = DNN(input_size=1, hidden_size=4, output_size=3, layer_level=1)
X = np.array([[-1.0], [0.0], [1.0]], dtype=np.float32)
Y = np.eye(3, dtype=np.float32)
model.model.fit(X, Y, epochs=1, verbose=0)
prediction = model.model.predict(X, verbose=0)

assert prediction.shape == (3, 3)
assert np.all(np.isfinite(prediction))
assert np.allclose(prediction.sum(axis=1), 1.0, atol=1e-5)
print(f"AFTER_DNN_FIT_RSS_MB={rss_mb():.1f}")
print(f"POP_AI_{args.mode.upper()}=PASS")
