#!/usr/bin/env python3
"""Match the a21 notebook import order: Util first, then memory-aware AI."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("MPLBACKEND", "Agg")

from pop import Util
from pop import AI

AI.configure("cpu")
DQN = AI.DQN

import tensorflow as tf

assert not tf.config.get_visible_devices("GPU")
model = DQN(state_size=4, hidden_size=8, output_size=1)
print(f"UTIL_MODULE={Util.__file__}")
print(f"DQN_DEVICE={AI.device_policy()}")
print(f"VISIBLE_GPUS={len(tf.config.get_visible_devices('GPU'))}")
print("DQN_NOTEBOOK_IMPORT_ORDER=PASS")
