#!/usr/bin/env bash
set -Eeuo pipefail

TARGET_USER="${TARGET_USER:-soda}"
TARGET_HOME="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
VENV="${VENV:-$TARGET_HOME/venvs/gong-rc}"

if [[ $EUID -ne 0 ]]; then
  echo "Run as root" >&2
  exit 1
fi
if [[ ! -x "$VENV/bin/python" ]]; then
  echo "Python environment not found: $VENV" >&2
  exit 1
fi

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y xvfb xauth mesa-utils

sudo -H -u "$TARGET_USER" "$VENV/bin/python" -m pip install --upgrade \
  'gymnasium[classic-control]==0.29.1' \
  'PyVirtualDisplay==3.0'

sudo -H -u "$TARGET_USER" env \
  SDL_VIDEODRIVER=dummy \
  SDL_AUDIODRIVER=dummy \
  "$VENV/bin/python" - <<'PY'
import gymnasium as gym
from pyvirtualdisplay import Display

env = gym.make("CartPole-v1", render_mode="rgb_array")
observation, info = env.reset(seed=42)
frame = env.render()
assert frame.shape == (400, 600, 3)
observation, reward, terminated, truncated, info = env.step(0)
env.close()

print("gymnasium=" + gym.__version__)
print("cartpole_frame=" + str(frame.shape))
print("DQN_GYMNASIUM_DEPENDENCIES=PASS")
PY

