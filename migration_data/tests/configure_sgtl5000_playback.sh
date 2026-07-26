#!/usr/bin/env bash
set -Eeuo pipefail

card=${CARD:-1}
prefix=${PREFIX:-H40-SGTL}
headphone=${HEADPHONE_VOLUME:-103}
lineout=${LINEOUT_VOLUME:-18}

if [[ $EUID -ne 0 ]]; then
    echo "Run as root so the ALSA state can be saved" >&2
    exit 1
fi

# Tegra APE playback path: ADMAIF1 -> I2S5 -> SGTL5000 DAC.
amixer -q -c "$card" sset 'I2S5 Mux' ADMAIF1
amixer -q -c "$card" sset "$prefix Digital Input Mux" I2S
amixer -q -c "$card" sset "$prefix Headphone Mux" DAC
amixer -q -c "$card" sset "$prefix PCM" 192
amixer -q -c "$card" sset "$prefix Headphone" "$headphone" unmute
amixer -q -c "$card" sset "$prefix Lineout" "$lineout" unmute

alsactl store "$card"

amixer -c "$card" sget 'I2S5 Mux'
amixer -c "$card" sget "$prefix Digital Input Mux"
amixer -c "$card" sget "$prefix Headphone"
amixer -c "$card" sget "$prefix Lineout"
echo "SGTL5000_PLAYBACK_SETUP=PASS"
