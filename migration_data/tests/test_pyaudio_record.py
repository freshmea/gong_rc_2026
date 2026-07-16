#!/usr/bin/env python3
"""Bounded, overflow-safe PyAudio capture test for the Gong RC Jetson."""

import argparse
import audioop
import ctypes
import math
import wave

import pyaudio


ALSA_ERROR_HANDLER = ctypes.CFUNCTYPE(
    None,
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.c_char_p,
)


def _quiet_alsa_errors():
    """Temporarily hide harmless ALSA PCM-enumeration diagnostics."""

    try:
        lib = ctypes.cdll.LoadLibrary("libasound.so.2")
        callback = ALSA_ERROR_HANDLER(lambda *_: None)
        lib.snd_lib_error_set_handler(callback)
        return lib, callback
    except OSError:
        return None, None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=5.0)
    parser.add_argument("--rate", type=int, default=48000)
    parser.add_argument("--chunk", type=int, default=4096)
    parser.add_argument("--output", default="out.wav")
    args = parser.parse_args()

    alsa, callback = _quiet_alsa_errors()
    audio = pyaudio.PyAudio()
    stream = None
    frames = []
    try:
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=args.rate,
            input=True,
            frames_per_buffer=args.chunk,
            start=False,
        )
        if alsa is not None:
            alsa.snd_lib_error_set_handler(None)

        stream.start_stream()
        print(f"녹음 시작: {args.seconds:.1f}초")
        count = math.ceil(args.rate * args.seconds / args.chunk)
        for _ in range(count):
            frames.append(
                stream.read(args.chunk, exception_on_overflow=False)
            )
    finally:
        if stream is not None:
            stream.stop_stream()
            stream.close()
        audio.terminate()
        if alsa is not None:
            alsa.snd_lib_error_set_handler(None)
        _ = callback  # Keep the C callback alive through PyAudio initialization.

    raw = b"".join(frames)
    raw = raw[: int(args.rate * args.seconds) * 2]
    with wave.open(args.output, "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(args.rate)
        output.writeframes(raw)

    full_scale = 32767.0
    rms = audioop.rms(raw, 2)
    peak = audioop.max(raw, 2)
    rms_dbfs = 20 * math.log10(max(rms, 1) / full_scale)
    peak_dbfs = 20 * math.log10(max(peak, 1) / full_scale)
    print(f"저장 완료: {args.output}")
    print(f"RMS={rms_dbfs:.2f} dBFS, peak={peak_dbfs:.2f} dBFS")


if __name__ == "__main__":
    main()
