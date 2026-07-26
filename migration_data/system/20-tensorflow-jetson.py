"""Safe TensorFlow defaults for every Jupyter/IPython kernel on Jetson.

This file intentionally does not import TensorFlow.  The variables must be set
before a notebook imports tensorflow so CUDA uses incremental allocation.
"""

import os

os.environ.setdefault("TF_FORCE_GPU_ALLOW_GROWTH", "true")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("XLA_FLAGS", "--xla_gpu_cuda_data_dir=/usr/local/cuda-11.4")
os.environ.setdefault("MPLBACKEND", "Agg")
