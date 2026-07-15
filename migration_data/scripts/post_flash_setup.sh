#!/usr/bin/env bash
set -Eeuo pipefail

TARGET_USER="${TARGET_USER:-soda}"
TARGET_HOME="$(getent passwd "$TARGET_USER" | cut -d: -f6)"

if [[ $EUID -ne 0 ]]; then
  echo "Run as root: sudo TARGET_USER=$TARGET_USER $0" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y \
  software-properties-common curl ca-certificates gnupg2 lsb-release locales \
  git git-lfs rsync jq tree htop vim nano tmux zsh unzip zip \
  build-essential cmake pkg-config ninja-build \
  i2c-tools alsa-utils v4l-utils ffmpeg \
  python3-pip python3-venv python3-dev python3-setuptools python3-wheel \
  python3-argcomplete \
  portaudio19-dev libsndfile1-dev libopenblas-dev libjpeg-dev libffi-dev \
  zsh-autosuggestions zsh-syntax-highlighting

locale-gen en_US en_US.UTF-8 ko_KR.UTF-8
update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

for group in dialout audio video i2c gpio docker; do
  if getent group "$group" >/dev/null; then
    usermod -aG "$group" "$TARGET_USER"
  fi
done

install -d -m 0755 /usr/share/keyrings
curl -fsSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
cat >/etc/apt/sources.list.d/ros2.list <<'EOF'
deb [arch=arm64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu focal main
EOF

apt-get update
apt-get install -y \
  ros-foxy-desktop ros-dev-tools python3-colcon-common-extensions python3-rosdep

if [[ ! -e /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
  rosdep init
fi
sudo -H -u "$TARGET_USER" rosdep update --rosdistro foxy

cat >/etc/udev/rules.d/99-rplidar.rules <<'EOF'
SUBSYSTEM=="tty", KERNEL=="ttyUSB*", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0660", GROUP="dialout", SYMLINK+="rplidar"
EOF
udevadm control --reload-rules
udevadm trigger

install -d -o "$TARGET_USER" -g "$TARGET_USER" "$TARGET_HOME/ros2_ws/src"
install -d -o "$TARGET_USER" -g "$TARGET_USER" "$TARGET_HOME/venvs"

for rc in "$TARGET_HOME/.bashrc" "$TARGET_HOME/.zshrc"; do
  touch "$rc"
  chown "$TARGET_USER:$TARGET_USER" "$rc"
  if ! grep -q 'gong_rc_2026 managed environment' "$rc"; then
    cat >>"$rc" <<'EOF'

# gong_rc_2026 managed environment
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
source /opt/ros/foxy/setup.bash
if [ -f "$HOME/ros2_ws/install/setup.bash" ]; then
  source "$HOME/ros2_ws/install/setup.bash"
fi
EOF
    chown "$TARGET_USER:$TARGET_USER" "$rc"
  fi
done

systemctl enable --now docker containerd ssh nvfancontrol nvargus-daemon

echo "post_flash_setup complete"
