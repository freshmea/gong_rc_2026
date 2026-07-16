#!/usr/bin/env python3
"""Exercise POP PyTorch, TensorFlow DNN/CNN, and YOLOv4-tiny code paths."""

from __future__ import annotations

import pathlib

import librosa
import numpy as np
import tensorflow as tf
import torch
import torchvision
from yolov4.tf import YOLOv4

import pop.AI as AI
import pop.Pilot as Pilot
import pop.Util as Util


ROOT = pathlib.Path('/usr/lib/python3/dist-packages/pop')

print(f"TORCH_VERSION={torch.__version__}")
print(f"TORCHVISION_VERSION={torchvision.__version__}")
print(f"LIBROSA_VERSION={librosa.__version__}")
print(f"TENSORFLOW_VERSION={tf.__version__}")
print(f"POP_PILOT_PATH={Pilot.__file__}")
print(f"POP_UTIL_PATH={Util.__file__}")

if not torch.cuda.is_available():
    raise RuntimeError('NVIDIA PyTorch cannot access CUDA')
device = torch.device('cuda')
torch_model = torch.nn.Sequential(
    torch.nn.Conv2d(3, 4, kernel_size=3, padding=1),
    torch.nn.ReLU(),
    torch.nn.AdaptiveAvgPool2d((1, 1)),
).to(device)
with torch.no_grad():
    torch_output = torch_model(torch.ones((1, 3, 32, 32), device=device))
print(f"PYTORCH_CUDA_CNN=PASS shape={tuple(torch_output.shape)} device={torch_output.device}")

alexnet = torchvision.models.alexnet(weights=None)
print(f"TORCHVISION_ALEXNET=PASS outputs={alexnet.classifier[-1].out_features}")

tf_gpus = tf.config.list_physical_devices('GPU')
for gpu in tf_gpus:
    try:
        tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError:
        pass
print(f"TENSORFLOW_GPU_COUNT={len(tf_gpus)}")
tf_result = tf.matmul(tf.ones((2, 2)), tf.ones((2, 2)))
print(f"TENSORFLOW_MATMUL=PASS value={tf_result.numpy().tolist()}")

dnn = AI.DNN(input_size=3, hidden_size=4, output_size=1, layer_level=2, softmax=False)
dnn_result = dnn.model(np.ones((1, 3), dtype=np.float32), training=False)
print(f"POP_DNN_FORWARD=PASS shape={tuple(dnn_result.shape)}")

cnn = AI.CNN(
    input_size=[28, 28], input_level=1, kernel_size=[3, 3], kernel_count=4,
    hidden_size=8, output_size=2, conv_level=1, layer_level=1, softmax=True,
)
cnn_result = cnn.model(np.ones((1, 28, 28, 1), dtype=np.float32), training=False)
print(f"POP_CNN_FORWARD=PASS shape={tuple(cnn_result.shape)}")

yolo = YOLOv4(tiny=True)
yolo.classes = str(ROOT / 'model/yolov4-tiny/coco.names')
yolo.input_size = (224, 224)
yolo.make_model()
yolo.load_weights(str(ROOT / 'model/yolov4-tiny/yolov4-tiny.weights'), weights_type='yolo')
yolo_result = yolo.predict(np.zeros((224, 224, 3), dtype=np.uint8), score_threshold=0.99)
print(f"YOLOV4_TINY_INFERENCE=PASS detections={len(yolo_result)}")

print("POP_AI_STACK_TEST=PASS")
