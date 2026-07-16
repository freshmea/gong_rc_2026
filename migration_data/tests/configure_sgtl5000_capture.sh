#!/usr/bin/env bash
set -Eeuo pipefail

card=${CARD:-1}
gain=${1:-10}
prefix=${PREFIX:-H40-SGTL}

if (( gain < 0 || gain > 15 )); then
    echo "capture gain must be between 0 and 15" >&2
    exit 2
fi

amixer -q -c "$card" sset 'ADMAIF1 Mux' I2S5
amixer -q -c "$card" sset 'I2S5 Mux' ADMAIF1
amixer -q -c "$card" sset "$prefix Capture Mux" LINE_IN
amixer -q -c "$card" sset "$prefix Capture Attenuate Switch (-6dB)" off
amixer -q -c "$card" sset "$prefix" "$gain" cap

sudo alsactl store "$card"

amixer -c "$card" sget "$prefix Capture Mux"
amixer -c "$card" sget "$prefix"
echo "Saved SGTL5000 capture gain $gain/15 for ALSA card $card."
