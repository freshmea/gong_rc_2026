#!/usr/bin/env python3
"""Capture and report one CSI frame using the installed POP pipeline."""

import argparse
import json
import time

import cv2
from pop import Util


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--flip", type=int, default=0)
    parser.add_argument("--warmup", type=int, default=30)
    args = parser.parse_args()

    pipeline = Util.gstrmer(args.width, args.height, args.fps, args.flip)
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
    if not cap.isOpened():
        raise RuntimeError("OpenCV could not open the GStreamer camera pipeline")

    frame = None
    read_count = 0
    started = time.monotonic()
    for _ in range(args.warmup):
        ok, candidate = cap.read()
        if ok:
            frame = candidate
            read_count += 1
    elapsed = time.monotonic() - started
    cap.release()

    if frame is None:
        raise RuntimeError("Camera opened but returned no frames")
    if not cv2.imwrite(args.output, frame):
        raise RuntimeError("Could not save frame: %s" % args.output)

    b, g, r = frame.reshape(-1, 3).mean(axis=0)
    print(json.dumps({
        "pipeline": pipeline,
        "shape": list(frame.shape),
        "reads": read_count,
        "elapsed_seconds": round(elapsed, 3),
        "mean_bgr": [round(float(b), 2), round(float(g), 2), round(float(r), 2)],
        "output": args.output,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
