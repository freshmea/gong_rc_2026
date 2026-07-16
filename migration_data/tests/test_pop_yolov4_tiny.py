#!/usr/bin/env python3
"""Load packaged YOLOv4-tiny weights and run one blank-frame inference."""

import pathlib

import numpy as np
import tensorflow as tf
from yolov4.tf import YOLOv4


for gpu in tf.config.list_physical_devices("GPU"):
    try:
        tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError:
        pass

root = pathlib.Path("/usr/lib/python3/dist-packages/pop/model/yolov4-tiny")
yolo = YOLOv4(tiny=True)
yolo.classes = str(root / "coco.names")
yolo.input_size = (224, 224)
yolo.make_model()
yolo.load_weights(str(root / "yolov4-tiny.weights"), weights_type="yolo")
result = yolo.predict(
    np.zeros((224, 224, 3), dtype=np.uint8), score_threshold=0.99
)
print(f"YOLOV4_TINY_INFERENCE=PASS detections={len(result)}")
