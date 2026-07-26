#!/usr/bin/env bash
set -Eeuo pipefail

TARGET_USER="${TARGET_USER:-soda}"
TARGET_HOME="$(getent passwd "$TARGET_USER" | cut -d: -f6)"

if [[ $EUID -ne 0 ]]; then
  echo "Run as root" >&2
  exit 1
fi

if [[ ! -d "$TARGET_HOME/.oh-my-zsh/.git" ]]; then
  sudo -H -u "$TARGET_USER" git clone --depth 1 \
    https://github.com/ohmyzsh/ohmyzsh.git "$TARGET_HOME/.oh-my-zsh"
fi

cat >"$TARGET_HOME/.zshrc" <<'EOF'
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="robbyrussell"
plugins=(git)
source "$ZSH/oh-my-zsh.sh"

[[ -r /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh ]] && \
  source /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh
[[ -r /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ]] && \
  source /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

# gong_rc_2026 managed environment
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libGLdispatch.so.0:/usr/lib/aarch64-linux-gnu/libgomp.so.1
export OPENCV_LOG_LEVEL=ERROR
[[ -r /opt/ros/foxy/setup.zsh ]] && source /opt/ros/foxy/setup.zsh
[[ -r "$HOME/ros2_ws/install/setup.zsh" ]] && source "$HOME/ros2_ws/install/setup.zsh"
[[ -r "$HOME/venvs/gong-rc/bin/activate" ]] && source "$HOME/venvs/gong-rc/bin/activate"

alias tm='tmux new-session -A -s main'

# Auto-attach only for an interactive SSH login.  SCP/SFTP, Jupyter terminals,
# local consoles and nested tmux sessions remain unaffected.
if [[ -o interactive && -n "${SSH_CONNECTION:-}" && -z "${TMUX:-}" \
      && "${TERM:-dumb}" != dumb && "${NO_AUTO_TMUX:-0}" != 1 ]]; then
  exec tmux new-session -A -s main
fi
EOF

cat >"$TARGET_HOME/.tmux.conf" <<'EOF'
set -g mouse on
set -g history-limit 50000
set -g default-shell /usr/bin/zsh
set -g default-command /usr/bin/zsh
set -g status-interval 5
setw -g mode-keys vi
EOF

chown "$TARGET_USER:$TARGET_USER" "$TARGET_HOME/.zshrc" "$TARGET_HOME/.tmux.conf"
chmod 0644 "$TARGET_HOME/.zshrc" "$TARGET_HOME/.tmux.conf"
chsh -s /usr/bin/zsh "$TARGET_USER"

echo "CLI_SHELL_SETUP=PASS"
getent passwd "$TARGET_USER"
sudo -H -u "$TARGET_USER" /usr/bin/zsh -lic \
  'echo ZSH_LOGIN=PASS; echo ROS_DISTRO=${ROS_DISTRO:-missing}; echo VIRTUAL_ENV=${VIRTUAL_ENV:-missing}; tmux -V'
