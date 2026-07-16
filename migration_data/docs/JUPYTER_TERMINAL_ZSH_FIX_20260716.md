# JupyterLab terminal Zsh fix

Date: 2026-07-16  
Target: `soda@192.168.0.34`

## Symptom and cause

SSH login used Zsh, but a terminal opened from JupyterLab still used Bash. Changing the account shell alone was insufficient because the systemd Jupyter service did not define `SHELL`, and Jupyter Server had no explicit terminado shell command.

## Applied configuration

The systemd drop-in `/etc/systemd/system/jupyter-gong-rc.service.d/terminal-shell.conf` now defines:

```ini
[Service]
Environment=HOME=/home/soda
Environment=USER=soda
Environment=LOGNAME=soda
Environment=SHELL=/usr/bin/zsh
```

`/home/soda/.jupyter/jupyter_server_config.py` now includes:

```python
c.ServerApp.terminado_settings = {
    'shell_command': ['/usr/bin/zsh', '-l'],
}
```

The login flag loads the managed Oh My Zsh, CUDA, ROS Foxy, ROS workspace, and `gong-rc` virtual environment. Jupyter terminals do not enter tmux automatically because the tmux rule is restricted to interactive SSH sessions with `SSH_CONNECTION`.

## Verification

```text
SHELL=/usr/bin/zsh
TERMINADO_SETTINGS={'shell_command': ['/usr/bin/zsh', '-l']}
JUPYTER_SHELL_CONFIG=PASS
TERMINAL_SHELL=/usr/bin/zsh
ZSH_VERSION=5.8
VIRTUAL_ENV=/home/soda/venvs/gong-rc
ROS_DISTRO=foxy
TMUX=none
jupyter-gong-rc.service=active
HTTP=302
```

The previous Jupyter configuration is backed up at:

```text
/home/soda/migration_backups/jupyter_terminal_20260716_112328
```

Existing browser terminals remain attached to their original Bash processes. Close those terminal tabs and create a new JupyterLab terminal after refreshing the browser.
