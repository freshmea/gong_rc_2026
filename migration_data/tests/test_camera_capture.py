#!/usr/bin/env python3
"""Capture one frame from a V4L2 camera and always release the device."""

import argparse
import cv2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=int, default=0)
    args = parser.parse_args()

    camera = cv2.VideoCapture(args.device, cv2.CAP_V4L2)
    try:
        if not camera.isOpened():
            print(f"CAMERA_CAPTURE=SKIP device={args.device} reason=open_failed")
            return 2
        ok, frame = camera.read()
        if not ok or frame is None:
            print(f"CAMERA_CAPTURE=FAIL device={args.device} reason=read_failed")
            return 1
        print(f"CAMERA_CAPTURE=PASS device={args.device} shape={frame.shape} dtype={frame.dtype}")
        return 0
    finally:
        camera.release()


if __name__ == "__main__":
    raise SystemExit(main())
