#!/usr/bin/env bash
set -Eeo pipefail

source /opt/ros/foxy/setup.bash
set -u

workdir="$(mktemp -d)"
listener_pid=""
cleanup() {
  if [[ -n "$listener_pid" ]]; then
    kill "$listener_pid" 2>/dev/null || true
    wait "$listener_pid" 2>/dev/null || true
  fi
  rm -rf "$workdir"
}
trap cleanup EXIT

echo "ROS_DISTRO=${ROS_DISTRO:-unset}"
echo "ROS_VERSION=${ROS_VERSION:-unset}"
ros2 --help >/dev/null
colcon version-check 2>/dev/null || colcon --help >/dev/null
ros2 doctor --report >"$workdir/doctor.txt" 2>&1 || true

timeout 12 ros2 run demo_nodes_py listener >"$workdir/listener.txt" 2>&1 &
listener_pid=$!
sleep 3

set +e
timeout 7 ros2 run demo_nodes_cpp talker >"$workdir/talker.txt" 2>&1
talker_rc=$?
set -e
if [[ $talker_rc -ne 0 && $talker_rc -ne 124 ]]; then
  cat "$workdir/talker.txt"
  exit "$talker_rc"
fi

sleep 2
if ! grep -q 'I heard' "$workdir/listener.txt"; then
  echo "ROS2 DDS message test failed"
  cat "$workdir/talker.txt"
  cat "$workdir/listener.txt"
  exit 1
fi

echo "ROS2_DDS_MESSAGE_TEST=PASS"
grep -m 3 'Publishing' "$workdir/talker.txt" || true
grep -m 3 'I heard' "$workdir/listener.txt" || true
echo "ROS2_DOCTOR_REPORT=GENERATED"
