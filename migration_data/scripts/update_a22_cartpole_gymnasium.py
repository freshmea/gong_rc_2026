#!/usr/bin/env python3
"""Migrate a22 CartPole DQN training to Gymnasium 0.29."""

import json
import sys
from pathlib import Path


SOURCES = [
    """import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import gymnasium as gym
import numpy as np
from pop import AI, Util

# CartPole DQN은 작은 네트워크이므로 CPU 저메모리 정책을 사용한다.
AI.configure("cpu")
dqn = AI.DQN(state_size=4, hidden_size=8, output_size=1)

env = gym.make('CartPole-v1', render_mode='rgb_array')
print("Gymnasium:", gym.__version__)
print("device:", AI.device_policy())
""",
    """for episode in range(1000):
    state, info = env.reset(seed=42 + episode)
    total_reward = 0.0
    states, rewards, actions = [], [], []

    while True:
        frame = env.render()
        Util.imshow('CartPole', frame, width=600, height=400, mode='RGB')
        # np.bool 기반 구형 DQN.run 대신 확률을 받아 명시적으로 행동을 선택한다.
        prediction = dqn.model.predict(
            np.asarray([state], dtype=np.float32),
            verbose=0,
        )
        action = int(prediction[0, 0] >= 0.5)

        states.append(np.asarray(state, dtype=np.float32))
        actions.append([float(action)])

        next_state, reward, terminated, truncated, info = env.step(action)
        rewards.append(float(reward))
        total_reward += reward
        state = next_state

        if terminated or truncated:
            loss = dqn.train(states, rewards, actions)
            print(
                "episode", episode + 1,
                "steps", len(rewards),
                "reward", total_reward,
                "loss", loss,
            )
            break

env.close()
""",
]


def update(path):
    notebook_path = Path(path)
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    code_cells = [cell for cell in notebook["cells"] if cell.get("cell_type") == "code"]
    if len(code_cells) < len(SOURCES):
        raise RuntimeError(f"{notebook_path}: not enough code cells")
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
    raise SystemExit("usage: update_a22_cartpole_gymnasium.py NOTEBOOK [NOTEBOOK ...]")
for argument in sys.argv[1:]:
    update(argument)

