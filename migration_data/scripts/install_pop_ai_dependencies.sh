#!/usr/bin/env bash
set -Eeuo pipefail

TARGET_USER="${TARGET_USER:-soda}"
TARGET_HOME="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
VENV="${VENV:-$TARGET_HOME/venvs/gong-rc}"
TORCH_URL="${TORCH_URL:-https://developer.download.nvidia.com/compute/redist/jp/v512/pytorch/torch-2.1.0a0+41361538.nv23.06-cp38-cp38-linux_aarch64.whl}"
TF_INDEX="${TF_INDEX:-https://developer.download.nvidia.com/compute/redist/jp/v512}"

if [[ $EUID -ne 0 ]]; then
  echo "Run as root" >&2
  exit 1
fi
if [[ ! -x "$VENV/bin/python" ]]; then
  echo "Python environment not found: $VENV" >&2
  exit 1
fi

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  libopenblas-dev libopenmpi-dev libjpeg-dev zlib1g-dev libpng-dev \
  libsndfile1-dev libhdf5-dev liblapack-dev libblas-dev gfortran python3-h5py

run_pip() {
  sudo -H -u "$TARGET_USER" "$VENV/bin/python" -m pip "$@"
}

# TensorFlow 2.12 requires NumPy < 1.24. This version also remains compatible
# with the migrated SciPy, pandas, scikit-learn, ONNX, librosa and PyTorch stack.
run_pip install --upgrade 'numpy==1.23.5'

# NVIDIA CUDA-enabled Jetson wheels. Do not let torchvision replace this torch
# build with a generic PyPI torch wheel.
run_pip install --upgrade "$TORCH_URL"
run_pip install --upgrade --no-deps 'torchvision==0.16.0'

# POP Util/AI, Pilot.Data_Collector and Object_Follow dependencies.
run_pip install --upgrade \
  'librosa==0.10.2.post1' 'yolov4==2.1.0' 'websock==1.0.4'
run_pip install --upgrade --extra-index-url "$TF_INDEX" \
  'tensorflow==2.12.0+nv23.06'

sudo -H -u "$TARGET_USER" env \
  LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libGLdispatch.so.0:/usr/lib/aarch64-linux-gnu/libgomp.so.1 \
  "$VENV/bin/python" - <<'PY'
import librosa
import tensorflow as tf
import torch
import torchvision
from yolov4.tf import YOLOv4

print('POP_AI_DEPENDENCIES=PASS')
print('torch=' + torch.__version__)
print('torchvision=' + torchvision.__version__)
print('torch_cuda=' + str(torch.cuda.is_available()))
print('tensorflow=' + tf.__version__)
print('tensorflow_gpus=' + str(len(tf.config.list_physical_devices('GPU'))))
print('librosa=' + librosa.__version__)
print('yolov4=' + str(YOLOv4))
PY

echo "install_pop_ai_dependencies complete"
