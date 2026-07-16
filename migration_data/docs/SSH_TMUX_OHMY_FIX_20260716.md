# SSH tmux and Oh My shell setup result

Date: 2026-07-16  
Target: `soda@192.168.0.34`

## Root cause

The migrated system had `/usr/bin/zsh` and `/usr/bin/tmux`, but the login shell was still `/bin/bash`. The following components were absent:

- `~/.oh-my-zsh`
- `~/.tmux.conf`
- an interactive SSH auto-attach rule

The old `~/.zshrc` contained only CUDA and ROS environment lines, so it could not initialize Oh My Zsh or tmux.

## Applied configuration

- Default login shell: `/usr/bin/zsh`
- Zsh: `5.8`
- tmux: `3.0a`
- Oh My Zsh commit: `677a4592b18c08ddea737f8aca70bac0e9fc9313`
- Oh My Tmux commit: `af33f07134b76134acca9d01eacbdecca9c9cda6`
- Oh My Zsh theme: `robbyrussell`
- Enabled built-in plugins: `git`, `sudo`, `command-not-found`, `colored-man-pages`, `history`, `extract`
- Oh My Zsh automatic updates are disabled to keep 21 classroom vehicles reproducible.
- ROS Foxy and `$HOME/ros2_ws` are loaded using Zsh setup files when present.
- `$HOME/venvs/gong-rc` is activated automatically.
- Interactive SSH terminals attach to `tmux new-session -A -s main`.

Automatic tmux is explicitly excluded for non-interactive SSH commands, SCP/SFTP, Jupyter services, `TERM=dumb`, local consoles, and nested tmux sessions. Set `NO_AUTO_TMUX=1` before starting Zsh when a temporary bypass is needed.

Useful aliases:

```text
cproj       go to the classroom notebook directory
jlab-status show the Jupyter service status
tm          attach/create the main tmux session
```

## Verification

```text
soda:x:1000:1000:soda,,,:/home/soda:/usr/bin/zsh
VIRTUAL_ENV=/home/soda/venvs/gong-rc
ROS_DISTRO=foxy
OMZ=/home/soda/.oh-my-zsh
AUTO_TMUX=PASS session=main shell=zsh
jupyter-gong-rc.service: active
nvargus-daemon.service: active
```

Previous startup files are backed up under:

```text
/home/soda/migration_backups/cli_20260716_110816
```

## Operator behavior

After `ssh soda@<vehicle-ip>`, the prompt appears inside the shared `main` tmux session. Disconnecting SSH does not stop jobs in tmux. Use `Ctrl-b d` to detach, and reconnect to resume. To end only the current shell, use `exit`; to remove the entire session, run `tmux kill-session -t main`.
