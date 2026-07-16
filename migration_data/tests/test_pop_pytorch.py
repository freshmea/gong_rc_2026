#!/usr/bin/env python3
"""Validate POP Pilot and a CUDA CNN without loading TensorFlow."""

import torch
import torchvision

import pop.Pilot as Pilot


print(f"TORCH_VERSION={torch.__version__}")
print(f"TORCHVISION_VERSION={torchvision.__version__}")
print(f"POP_PILOT_PATH={Pilot.__file__}")
if not torch.cuda.is_available():
    raise RuntimeError("NVIDIA PyTorch cannot access CUDA")

device = torch.device("cuda")
model = torch.nn.Sequential(
    torch.nn.Conv2d(3, 4, kernel_size=3, padding=1),
    torch.nn.ReLU(),
    torch.nn.AdaptiveAvgPool2d((1, 1)),
).to(device)
with torch.no_grad():
    output = model(torch.ones((1, 3, 32, 32), device=device))
print(f"PYTORCH_CUDA_CNN=PASS shape={tuple(output.shape)} device={output.device}")

alexnet = torchvision.models.alexnet(weights=None)
print(f"TORCHVISION_ALEXNET=PASS outputs={alexnet.classifier[-1].out_features}")
print("POP_PYTORCH_TEST=PASS")
