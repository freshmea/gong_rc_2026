#!/usr/bin/env python3
"""Report basic PCM WAV levels for migration audio tests."""

import argparse
import audioop
import wave


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("wav")
    args = parser.parse_args()

    with wave.open(args.wav, "rb") as wav:
        frames = wav.readframes(wav.getnframes())
        width = wav.getsampwidth()
        peak = audioop.max(frames, width) if frames else 0
        rms = audioop.rms(frames, width) if frames else 0
        full_scale = float((1 << (8 * width - 1)) - 1)
        print(f"file={args.wav}")
        print(f"channels={wav.getnchannels()} rate={wav.getframerate()} frames={wav.getnframes()}")
        print(f"rms={rms} ({20 * __import__('math').log10(max(rms, 1) / full_scale):.2f} dBFS)")
        print(f"peak={peak} ({20 * __import__('math').log10(max(peak, 1) / full_scale):.2f} dBFS)")


if __name__ == "__main__":
    main()
