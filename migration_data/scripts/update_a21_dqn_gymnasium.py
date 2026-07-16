#!/usr/bin/env python3
"""Migrate the a21 DQN notebook from legacy Gym to Gymnasium 0.29."""

import json
import sys
from pathlib import Path


SOURCES = [
    """import os

# Pygame의 오디오/화면 장치를 headless Jupyter에 맞춘다.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import gymnasium as gym
from pop import Util

print("Gymnasium:", gym.__version__)
""",
    """from pyvirtualdisplay import Display
""",
    """# glxinfo 같은 X11 진단용 가상 화면이다. rgb_array 렌더링은 SDL dummy로도 동작한다.
try:
    display.stop()
except (NameError, AttributeError):
    pass

display = Display(
    visible=0,
    size=(1024, 768),
    extra_args=["+extension", "GLX", "+render", "-noreset"],
)
display.start()
print("DISPLAY =", os.environ.get("DISPLAY"))
""",
    """env = gym.make("CartPole-v1", render_mode="rgb_array")
obs, info = env.reset(seed=42)

for _ in range(1000):
    frame = env.render()
    Util.imshow("CartPole", frame, mode="RGB")

    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)

    if terminated or truncated:
        obs, info = env.reset()

env.close()
""",
    """import shutil
import subprocess

glxinfo = shutil.which("glxinfo")
print("glxinfo =", glxinfo)
if glxinfo:
    subprocess.run([glxinfo, "-B"], check=False)
""",
    """# 렌더링 없이 Gymnasium의 최신 step/reset API를 확인한다.
env = gym.make("CartPole-v1")
obs, info = env.reset(seed=42)

for step in range(20):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    print(step, obs, reward, terminated, truncated)

    if terminated or truncated:
        obs, info = env.reset()

env.close()
""",
    """# POP DQN은 작은 수업 모델이므로 기본 CPU 저메모리 정책을 사용한다.
from pop import AI
import numpy as np

AI.configure("cpu")
dqn = AI.DQN(state_size=4, hidden_size=8, output_size=1)

states = np.array([
    [0.00, 0.00, 0.00, 0.00],
    [0.01, 0.02, 0.01, 0.02],
    [-0.01, -0.02, -0.01, -0.02],
    [0.02, 0.01, -0.02, -0.01],
], dtype=np.float32)
rewards = [1.0, 1.0, 1.0, 1.0]
actions = np.array([[0.0], [1.0], [0.0], [1.0]], dtype=np.float32)

loss = dqn.train(states, rewards, actions, times=1)
prediction = dqn.run([states[0]], boolean=False)
print("loss =", loss)
print("prediction =", prediction)
print("device =", AI.device_policy())
""",
    """env = gym.make("CartPole-v1")
obs, info = env.reset(seed=42)

for step in range(1000):
    prediction = float(dqn.run([obs], boolean=False)[0, 0])
    action = int(prediction >= 0.5)
    obs, reward, terminated, truncated, info = env.step(action)

    if terminated or truncated:
        print("episode length =", step + 1)
        obs, info = env.reset()
        break

env.close()
""",
]


def update(path):
    notebook_path = Path(path)
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    code_cells = [cell for cell in notebook["cells"] if cell.get("cell_type") == "code"]
    if len(code_cells) < len(SOURCES):
        raise RuntimeError(
            f"{notebook_path}: expected at least {len(SOURCES)} code cells, "
            f"found {len(code_cells)}"
        )

    for cell, source in zip(code_cells, SOURCES):
        cell["source"] = source.splitlines(keepends=True)
        cell["execution_count"] = None
        cell["outputs"] = []

    for cell in code_cells[len(SOURCES):]:
        cell["execution_count"] = None
        cell["outputs"] = []

    notebook_path.write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    print(notebook_path)


if len(sys.argv) < 2:
    raise SystemExit("usage: update_a21_dqn_gymnasium.py NOTEBOOK [NOTEBOOK ...]")

for argument in sys.argv[1:]:
    update(argument)

