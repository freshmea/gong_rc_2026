#!/usr/bin/env bash
set -Eeuo pipefail

TARGET_HOME="${TARGET_HOME:-/home/soda}"
PYTHON="${PYTHON:-$TARGET_HOME/venvs/gong-rc/bin/python}"
cd "$TARGET_HOME"
export LD_LIBRARY_PATH="/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export LD_PRELOAD="/usr/lib/aarch64-linux-gnu/libGLdispatch.so.0:/usr/lib/aarch64-linux-gnu/libgomp.so.1"
export TF_FORCE_GPU_ALLOW_GROWTH=true
export TF_CPP_MIN_LOG_LEVEL=2
export XLA_FLAGS=--xla_gpu_cuda_data_dir=/usr/local/cuda-11.4
export MPLBACKEND=Agg
export OPENCV_LOG_LEVEL=ERROR

echo "AI_VALIDATION_START=$(date -Is)"
free -h

"$PYTHON" - <<'PY'
import torch
import torchvision
from torchvision.io import read_image

assert torch.cuda.is_available(), "PyTorch CUDA unavailable"
print("TORCH_VALIDATION=PASS")
print("torch=" + torch.__version__)
print("torchvision=" + torchvision.__version__)
print("device=" + torch.cuda.get_device_name(0))
print("torchvision_read_image=" + str(callable(read_image)))
PY

"$PYTHON" - <<'PY'
import os
import numpy as np
import tensorflow as tf

gpus = tf.config.list_physical_devices("GPU")
assert gpus, "TensorFlow GPU unavailable"
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

x = np.array([[-1.0], [0.0], [1.0]], dtype=np.float32)
y = np.eye(3, dtype=np.float32)
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(1,)),
    tf.keras.layers.Dense(3, activation="softmax"),
])
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
    loss="categorical_crossentropy",
)
loss = float(model.train_on_batch(x, y))
print("TENSORFLOW_VALIDATION=PASS")
print("tensorflow=" + tf.__version__)
print("tensorflow_gpus=" + str(len(gpus)))
print("memory_growth=" + str(tf.config.experimental.get_memory_growth(gpus[0])))
print("softmax_loss=" + str(loss))
PY

"$PYTHON" - <<'PY'
import numpy as np
from sklearn.linear_model import LinearRegression

x = np.arange(8, dtype=np.float64).reshape(-1, 1)
y = 3.0 * x[:, 0] + 2.0
model = LinearRegression().fit(x, y)
assert abs(model.coef_[0] - 3.0) < 1e-9
print("SKLEARN_VALIDATION=PASS")
print("linear_regression_coef=" + str(model.coef_[0]))
PY

"$PYTHON" - <<'PY'
import pathlib
import pop
from pop import Pilot, Util

path = pathlib.Path(pop.__file__).resolve()
assert str(path).startswith("/usr/lib/python3/dist-packages/pop/"), path
print("POP_AI_IMPORT=PASS")
print("pop_path=" + str(path))
print("pilot=" + str(Pilot.__name__))
print("util=" + str(Util.__name__))
PY

free -h
echo "AI_STACK_VALIDATION=PASS"
echo "AI_VALIDATION_END=$(date -Is)"
