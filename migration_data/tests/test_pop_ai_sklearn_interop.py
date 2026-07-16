#!/usr/bin/env python3
"""Validate POP AI, TensorFlow GPU, and scikit-learn in one process."""

import os

os.environ.setdefault("TF_FORCE_GPU_ALLOW_GROWTH", "true")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np
import tensorflow as tf
from pop import AI
from sklearn.linear_model import LinearRegression


def main():
    gpus = tf.config.list_physical_devices("GPU")
    if not gpus:
        raise RuntimeError("TensorFlow GPU not detected")

    with tf.device("/GPU:0"):
        matrix = tf.constant([[1.0, 2.0], [3.0, 4.0]])
        product = tf.matmul(matrix, matrix).numpy().tolist()

    pop_model = AI.Linear_Regression()
    pop_model.hypothesis.fit(
        np.array([[0.0], [1.0], [2.0]], dtype=np.float32),
        np.array([[0.0], [2.0], [4.0]], dtype=np.float32),
        epochs=2,
        verbose=0,
    )

    sklearn_model = LinearRegression().fit(
        [[0.0], [1.0], [2.0]],
        [0.0, 2.0, 4.0],
    )

    print(f"POP_AI_PATH={AI.__file__}")
    print(f"TENSORFLOW={tf.__version__}")
    print(f"TF_GPU_MATMUL={product}")
    print(f"SKLEARN_COEF={sklearn_model.coef_.tolist()}")
    print(f"SKLEARN_PREDICT={sklearn_model.predict([[3.0]]).tolist()}")
    print("POP_AI_SKLEARN_INTEROP=PASS")


if __name__ == "__main__":
    main()
