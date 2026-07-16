#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: sudo $0 batch4.tsv --yes-flash-batch" >&2
  exit 2
}

[[ $# -eq 2 && "$2" == "--yes-flash-batch" ]] || usage
[[ $EUID -eq 0 ]] || { echo "Run with sudo." >&2; exit 1; }
INVENTORY="$(readlink -f "$1")"
[[ -r "$INVENTORY" ]] || { echo "Inventory not found: $INVENTORY" >&2; exit 1; }

ROOT="${JETSON_WORK_ROOT:-/home/aa/jetson-r35.6.4}"
FLASHER="$ROOT/06_flash_qspi_lane.sh"
[[ -x "$FLASHER" ]] || { echo "Missing flasher: $FLASHER" >&2; exit 1; }

declare -a units instances lanes pids
while IFS=$'\t' read -r unit instance lane extra; do
  [[ -z "${unit// }" || "$unit" == \#* ]] && continue
  [[ -z "${extra:-}" ]] || { echo "Too many fields for $unit" >&2; exit 1; }
  [[ "$lane" =~ ^[1-4]$ ]] || { echo "Lane must be 1-4 for $unit" >&2; exit 1; }
  units+=("$unit")
  instances+=("$instance")
  lanes+=("$lane")
done < "$INVENTORY"

count=${#units[@]}
(( count >= 1 && count <= 4 )) || { echo "Inventory must contain 1-4 units." >&2; exit 1; }

for ((i=0; i<count; i++)); do
  for ((j=i+1; j<count; j++)); do
    [[ "${units[i]}" != "${units[j]}" ]] || { echo "Duplicate unit ID." >&2; exit 1; }
    [[ "${instances[i]}" != "${instances[j]}" ]] || { echo "Duplicate USB instance." >&2; exit 1; }
    [[ "${lanes[i]}" != "${lanes[j]}" ]] || { echo "Duplicate lane." >&2; exit 1; }
  done
done

echo "About to overwrite QSPI on $count units:"
for ((i=0; i<count; i++)); do
  printf '  unit=%s usb=%s lane=%s\n' "${units[i]}" "${instances[i]}" "${lanes[i]}"
done

for ((i=0; i<count; i++)); do
  "$FLASHER" "$ROOT/lanes/lane${lanes[i]}" \
    "${instances[i]}" "${units[i]}" --yes-flash-qspi &
  pids+=("$!")
done

failures=0
for ((i=0; i<count; i++)); do
  if wait "${pids[i]}"; then
    echo "BATCH_UNIT=PASS unit=${units[i]}"
  else
    echo "BATCH_UNIT=FAIL unit=${units[i]}" >&2
    failures=$((failures + 1))
  fi
done

if (( failures > 0 )); then
  echo "BATCH=FAIL failures=$failures" >&2
  exit 1
fi
echo "BATCH=PASS count=$count"
