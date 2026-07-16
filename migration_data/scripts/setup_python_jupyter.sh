#!/usr/bin/env bash
set -Eeuo pipefail

TARGET_USER="${TARGET_USER:-soda}"
TARGET_HOME="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
VENV="$TARGET_HOME/venvs/gong-rc"
NOTEBOOK_DIR="$TARGET_HOME/Project/python/notebook"

if [[ $EUID -ne 0 ]]; then
  echo "Run as root with JUPYTER_PASSWORD set" >&2
  exit 1
fi
if [[ -z "${JUPYTER_PASSWORD:-}" ]]; then
  echo "JUPYTER_PASSWORD is required" >&2
  exit 1
fi

install -d -o "$TARGET_USER" -g "$TARGET_USER" "$TARGET_HOME/venvs" "$NOTEBOOK_DIR"

if [[ ! -x "$VENV/bin/python" ]]; then
  sudo -H -u "$TARGET_USER" python3 -m venv --system-site-packages "$VENV"
fi

sudo -H -u "$TARGET_USER" "$VENV/bin/python" -m pip install --upgrade \
  'importlib-metadata<9' 'packaging<25'
sudo -H -u "$TARGET_USER" "$VENV/bin/python" -m pip install --upgrade \
  'pip<25.1' 'setuptools<76' wheel

sudo -H -u "$TARGET_USER" "$VENV/bin/python" -m pip install --upgrade \
  'jupyterlab<4.4' 'notebook<7.4' jupyter-server ipywidgets ipykernel \
  'numpy==1.23.5' 'scipy<1.11' 'pandas<2.1' 'matplotlib<3.8' \
  'scikit-learn<1.4' 'pillow<11' seaborn \
  pyserial smbus2 rplidar-roboticia pyaudio sounddevice \
  gTTS pyyaml requests tqdm psutil \
  fastapi uvicorn flask pytest 'onnx<1.17'

sudo -H -u "$TARGET_USER" "$VENV/bin/python" -m ipykernel install \
  --user --name gong-rc --display-name 'Python 3 (gong-rc Jetson)'

install -d -o "$TARGET_USER" -g "$TARGET_USER" "$TARGET_HOME/.jupyter"
JUPYTER_HASH="$(JUPYTER_PASSWORD="$JUPYTER_PASSWORD" "$VENV/bin/python" - <<'PY'
import os
from jupyter_server.auth.security import passwd
print(passwd(os.environ['JUPYTER_PASSWORD']))
PY
)"

cat >"$TARGET_HOME/.jupyter/jupyter_server_config.py" <<EOF
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.root_dir = '$NOTEBOOK_DIR'
c.PasswordIdentityProvider.hashed_password = '$JUPYTER_HASH'
c.ServerApp.allow_remote_access = True
c.ServerApp.allow_origin = ''
EOF
chown "$TARGET_USER:$TARGET_USER" "$TARGET_HOME/.jupyter/jupyter_server_config.py"
chmod 0600 "$TARGET_HOME/.jupyter/jupyter_server_config.py"

cat >/etc/systemd/system/jupyter-gong-rc.service <<EOF
[Unit]
Description=JupyterLab for gong_rc_2026
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$TARGET_USER
Group=$TARGET_USER
WorkingDirectory=$NOTEBOOK_DIR
Environment=PATH=$VENV/bin:/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin
Environment=LD_LIBRARY_PATH=/usr/local/cuda/lib64
Environment=LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libGLdispatch.so.0:/usr/lib/aarch64-linux-gnu/libgomp.so.1
ExecStart=$VENV/bin/jupyter lab --config=$TARGET_HOME/.jupyter/jupyter_server_config.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable jupyter-gong-rc.service
systemctl restart jupyter-gong-rc.service

echo "setup_python_jupyter complete"
