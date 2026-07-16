#!/usr/bin/env python3
"""Regression test for the classroom softmax example on Jetson."""

import os

# These must be set before importing TensorFlow.
os.environ.setdefault("TF_FORCE_GPU_ALLOW_GROWTH", "true")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np
import tensorflow as tf


a1 = [73, 62, 83, 110, 139, 123, 177, 159, 182]
a2 = [1, 1, 1, 0, 0, 0, 0, 0, 0]
a3 = [0, 0, 0, 1, 1, 1, 0, 0, 0]
a4 = [0, 0, 0, 0, 0, 0, 1, 1, 1]

X = np.array(a1, dtype=np.float32).reshape(-1, 1)
Y = np.array([a2, a3, a4], dtype=np.float32).T
X_scaled = (X - X.mean()) / X.std()

model = tf.keras.Sequential(
    [tf.keras.layers.Dense(3, input_shape=[1], activation="softmax")]
)
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.05),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
    # TF 2.12 may otherwise XLA-compile the optimizer update.  This tiny
    # classroom model gains nothing from XLA and can hit Jetson memory limits.
    jit_compile=False,
)

history = model.fit(X_scaled, Y, epochs=10, verbose=0)
prediction = model.predict(X_scaled, verbose=0)

assert prediction.shape == (9, 3)
assert np.all(np.isfinite(prediction))
assert np.allclose(prediction.sum(axis=1), 1.0, atol=1e-5)

print(f"TENSORFLOW={tf.__version__}")
print(f"GPU_COUNT={len(tf.config.list_physical_devices('GPU'))}")
print(f"FINAL_LOSS={history.history['loss'][-1]:.6f}")
print(f"FINAL_ACCURACY={history.history['accuracy'][-1]:.6f}")
print("SOFTMAX_ROW_SUMS=" + np.array2string(prediction.sum(axis=1), precision=6))
print("SOFTMAX_JETSON=PASS")
