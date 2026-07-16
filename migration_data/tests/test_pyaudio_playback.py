#!/usr/bin/env python3
"""Play a bounded 440 Hz tone through the SGTL5000 output."""

import argparse

import numpy as np
import pyaudio

import quiet_alsa_ipython  # noqa: F401 - installs the ALSA diagnostic handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=5.0)
    parser.add_argument("--frequency", type=float, default=440.0)
    parser.add_argument("--volume", type=float, default=0.5)
    args = parser.parse_args()

    if not 0.0 <= args.volume <= 1.0:
        parser.error("--volume must be between 0.0 and 1.0")

    rate = 48000
    sample_count = int(rate * args.seconds)
    phase = 2 * np.pi * np.arange(sample_count) * args.frequency / rate
    data = (args.volume * np.sin(phase)).astype(np.float32)

    audio = pyaudio.PyAudio()
    stream = None
    try:
        stream = audio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=rate,
            output=True,
        )
        stream.write(data.tobytes())
    finally:
        if stream is not None:
            stream.stop_stream()
            stream.close()
        audio.terminate()

    print(
        f"PLAYBACK_OK frequency={args.frequency:.1f}Hz "
        f"seconds={args.seconds:.1f} volume={args.volume:.2f}"
    )


if __name__ == "__main__":
    main()
