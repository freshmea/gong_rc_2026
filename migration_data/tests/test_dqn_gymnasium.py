#!/usr/bin/env python3
"""End-to-end check for Gymnasium CartPole, Xvfb, rendering, and POP DQN."""

import os
import shutil
import subprocess

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np
import gymnasium as gym
from pyvirtualdisplay import Display


print(f"GYMNASIUM={gym.__version__}")
display = Display(
    visible=0,
    size=(1024, 768),
    extra_args=["+extension", "GLX", "+render", "-noreset"],
)
display.start()
print(f"DISPLAY={os.environ.get('DISPLAY')}")

try:
    glxinfo = shutil.which("glxinfo")
    assert glxinfo, "glxinfo was not installed"
    result = subprocess.run(
        [glxinfo, "-B"], text=True, capture_output=True, check=False
    )
    print(f"GLXINFO_RETURN={result.returncode}")

    env = gym.make("CartPole-v1", render_mode="rgb_array")
    obs, info = env.reset(seed=42)
    frames = []
    for _ in range(20):
        frame = env.render()
        assert frame.ndim == 3 and frame.shape[2] == 3
        frames.append(frame)
        obs, reward, terminated, truncated, info = env.step(
            env.action_space.sample()
        )
        if terminated or truncated:
            obs, info = env.reset()
    env.close()
    print(f"FRAME_SHAPE={frames[-1].shape}")
    print("GYMNASIUM_CARTPOLE_RENDER=PASS")

    from pop import AI

    AI.configure("cpu")
    dqn = AI.DQN(state_size=4, hidden_size=8, output_size=1)
    states = np.array(
        [
            [0.00, 0.00, 0.00, 0.00],
            [0.01, 0.02, 0.01, 0.02],
            [-0.01, -0.02, -0.01, -0.02],
            [0.02, 0.01, -0.02, -0.01],
        ],
        dtype=np.float32,
    )
    rewards = [1.0, 1.0, 1.0, 1.0]
    actions = np.array([[0.0], [1.0], [0.0], [1.0]], dtype=np.float32)
    loss = dqn.train(states, rewards, actions, times=1)
    prediction = dqn.run([states[0]], boolean=False)
    assert np.isfinite(loss)
    assert prediction.shape == (1, 1)
    print(f"DQN_LOSS={loss}")
    print(f"DQN_PREDICTION={prediction[0, 0]}")
    print(f"DQN_DEVICE={AI.device_policy()}")
    print("POP_DQN_GYMNASIUM=PASS")
finally:
    display.stop()
