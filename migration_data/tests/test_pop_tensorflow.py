#!/usr/bin/env python3
"""Validate POP Util and TensorFlow DNN/CNN without loading PyTorch."""

import numpy as np
import tensorflow as tf

import pop.AI as AI
import pop.Util as Util


gpus = tf.config.list_physical_devices("GPU")
for gpu in gpus:
    try:
        tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError:
        pass

print(f"TENSORFLOW_VERSION={tf.__version__}")
print(f"TENSORFLOW_GPU_COUNT={len(gpus)}")
print(f"POP_UTIL_PATH={Util.__file__}")
if not gpus:
    raise RuntimeError("NVIDIA TensorFlow cannot access GPU")

value = tf.matmul(tf.ones((2, 2)), tf.ones((2, 2)))
print(f"TENSORFLOW_MATMUL=PASS value={value.numpy().tolist()}")

dnn = AI.DNN(input_size=3, hidden_size=4, output_size=1, layer_level=2, softmax=False)
dnn_result = dnn.model(np.ones((1, 3), dtype=np.float32), training=False)
print(f"POP_DNN_FORWARD=PASS shape={tuple(dnn_result.shape)}")

cnn = AI.CNN(
    input_size=[28, 28], input_level=1, kernel_size=[3, 3], kernel_count=4,
    hidden_size=8, output_size=2, conv_level=1, layer_level=1, softmax=True,
)
cnn_result = cnn.model(np.ones((1, 28, 28, 1), dtype=np.float32), training=False)
print(f"POP_CNN_FORWARD=PASS shape={tuple(cnn_result.shape)}")
print("POP_TENSORFLOW_TEST=PASS")
