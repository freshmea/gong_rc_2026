#!/usr/bin/env python3
"""Run one Gymnasium CartPole episode through the migrated POP DQN path."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("MPLBACKEND", "Agg")

import gymnasium as gym
import numpy as np
from pop import AI


AI.configure("cpu")
dqn = AI.DQN(state_size=4, hidden_size=8, output_size=1)
env = gym.make("CartPole-v1")
state, info = env.reset(seed=42)
states, rewards, actions = [], [], []

for _ in range(500):
    prediction = dqn.model.predict(
        np.asarray([state], dtype=np.float32), verbose=0
    )
    action = int(prediction[0, 0] >= 0.5)
    states.append(np.asarray(state, dtype=np.float32))
    actions.append([float(action)])
    state, reward, terminated, truncated, info = env.step(action)
    rewards.append(float(reward))
    if terminated or truncated:
        break

env.close()
loss = dqn.train(states, rewards, actions)
assert rewards
assert np.isfinite(loss)
print(f"EPISODE_STEPS={len(rewards)}")
print(f"DQN_LOSS={loss}")
print("A22_CARTPOLE_EPISODE=PASS")
