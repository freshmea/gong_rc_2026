#!/usr/bin/env bash
set -Eeuo pipefail

for _ in $(seq 1 30); do
    authority=$(
        ps -eo args \
            | sed -n 's/.*[[:space:]]-auth[[:space:]]\([^[:space:]]*\).*/\1/p' \
            | head -n 1
    )
    if [[ -S /tmp/.X11-unix/X0 && -n "$authority" && -r "$authority" ]]; then
        exec runuser -u gdm -- env \
            DISPLAY=:0 \
            XAUTHORITY="$authority" \
            xhost +SI:localuser:soda
    fi
    sleep 1
done

echo "Xorg :0 or its authority file did not become ready" >&2
exit 1
