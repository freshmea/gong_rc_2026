#!/usr/bin/env bash
set -u
jupyter --version
jupyter kernelspec list
tmux -V

session="migration-check-$$"
if tmux new-session -d -s "$session" 'sleep 3'; then
  tmux has-session -t "$session" && echo 'PASS: tmux detached session created'
  tmux kill-session -t "$session" 2>/dev/null || true
else
  echo 'FAIL: tmux session creation failed'
  exit 1
fi

port=18888
log=/tmp/migration-jupyter-test.log
timeout 15 jupyter lab --no-browser --ip=127.0.0.1 --port="$port" >"$log" 2>&1 &
pid=$!
sleep 6
if curl -fsS "http://127.0.0.1:$port/" >/dev/null 2>&1; then
  echo 'PASS: Jupyter Lab HTTP endpoint responded'
else
  echo 'WARN: Jupyter Lab endpoint did not respond; inspect:' "$log"
  sed -n '1,120p' "$log" 2>/dev/null || true
fi
kill "$pid" 2>/dev/null || true
wait "$pid" 2>/dev/null || true

