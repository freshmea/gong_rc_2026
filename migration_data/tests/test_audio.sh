#!/usr/bin/env bash
set -u
echo '=== ALSA cards ==='
cat /proc/asound/cards 2>/dev/null || true
aplay -l 2>/dev/null || true
arecord -l 2>/dev/null || true

if [ "${1:-}" = "--active" ]; then
  test_wav=/tmp/migration_audio_capture.wav
  echo '=== one-second capture test ==='
  if timeout 5 arecord -q -d 1 -f S16_LE -r 16000 -c 1 "$test_wav"; then
    file "$test_wav"
    echo "PASS: capture completed ($test_wav)"
  else
    echo 'WARN: capture failed or no default capture device'
  fi
  echo '=== playback test ==='
  sample=/usr/share/sounds/alsa/Front_Center.wav
  [ -f "$sample" ] && timeout 8 aplay -q "$sample" && echo 'PASS: playback command completed' || echo 'WARN: playback failed'
fi

