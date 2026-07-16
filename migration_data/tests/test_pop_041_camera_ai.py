#!/usr/bin/env python3
"""Hardware integration test for POP 0.4.1 camera and Collision_Avoid."""

import os
import resource
import time
import warnings

import numpy as np

os.environ.setdefault("OPENCV_LOG_LEVEL", "ERROR")

from pop import Camera, Pilot, __version__


TARGET_WARNING_PARTS = (
    "Failed to load image Python extension",
    "The parameter 'pretrained' is deprecated",
    "Arguments other than a weight enum",
    "Cannot query video position",
)


with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    cam = Camera(width=300, height=300, fps=30)
    try:
        deadline = time.monotonic() + 10
        while cam.value is None and time.monotonic() < deadline:
            time.sleep(0.1)
        assert isinstance(cam.value, np.ndarray), "camera did not return a frame"
        assert cam.value.shape == (300, 300, 3), cam.value.shape

        ca = Pilot.Collision_Avoid(cam)
        ca.load_datasets()
        assert str(ca.device) == "cpu", ca.device
        ca.train(times=1, autosave=False)
        inference = float(ca.run())
    finally:
        cam.stop()

target_warnings = [
    str(item.message)
    for item in caught
    if any(part in str(item.message) for part in TARGET_WARNING_PARTS)
]

print(f"PACKAGE={__version__}")
print("CAMERA_MODE=1640x1232@30")
print("FRAME_SHAPE=(300, 300, 3)")
print("COLLISION_DEVICE=cpu")
print(f"INFERENCE={inference}")
print(f"MAX_RSS_MB={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024:.1f}")
print(f"TARGET_WARNING_COUNT={len(target_warnings)}")
assert __version__ == "0.4.1", __version__
assert not target_warnings, target_warnings
print("A31_INTEGRATION=PASS")
