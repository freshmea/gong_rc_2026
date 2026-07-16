# POP 0.4.1 camera and torchvision compatibility fix

Date: 2026-07-16  
Target: Jetson Xavier NX, `soda@192.168.0.34`  
Python environment: `/home/soda/venvs/gong-rc`

## Result

- Installed package: `gong-rc-pop 0.4.1+20260716`
- POP Python version: `0.4.1`
- Rebuilt and installed torchvision `0.16.0` against the installed NVIDIA torch `2.1.0a0+41361538.nv23.06`.
- Camera capture now requests sensor mode 1640x1232 at 30 FPS instead of 3280x2464 at 21 FPS for the classroom 300x300 stream.
- The integrated A31 Collision_Avoid test completed camera capture, dataset load, one CPU training pass, and inference.
- Target warning count was zero.

## Root causes and changes

### torchvision image extension

The previous `torchvision/image.so` binary was not ABI-compatible with the installed NVIDIA torch and failed on `parseSchemaOrName`. torchvision v0.16.0 was rebuilt from the official v0.16.0 source tag on the Jetson against the currently installed torch and CUDA stack.

Validation:

```text
TORCHVISION_VERSION=0.16.0
TORCHVISION_IMAGE_EXTENSION=PASS
TORCHVISION_NMS=PASS
```

### Camera load and GStreamer warning

- Removed the hard-coded `sudo systemctl restart nvargus-daemon` from `Camera.load()`. Loading a camera no longer prompts for the soda password or disrupts other camera users.
- Changed the capture request to 1640x1232 at 30 FPS and added a one-frame appsink queue (`drop=true max-buffers=1 sync=false`).
- Set `OPENCV_LOG_LEVEL=ERROR` before importing OpenCV so the non-seekable live-stream position-query warning is not printed.
- Added deterministic camera-thread shutdown: signal stop, join the capture thread, then release `VideoCapture`.
- Made `stop()` idempotent and added capture-thread state checks.

`GST_ARGUS: Available Sensor modes` and setup/cleanup messages remain normal driver information. They are not errors.

### Collision_Avoid memory behavior

- Uses the torchvision weights enum API instead of deprecated `pretrained=True`.
- Defaults training to CPU on this 8 GB unified-memory Jetson.
- Uses 224x224 model input, batch size 2, and zero data-loader workers.
- Freezes AlexNet feature layers and trains only the final classifier.
- Evaluation and inference use `no_grad()`.

## Final integrated validation

```text
PACKAGE=0.4.1
CAMERA_MODE=1640x1232@30
FRAME_SHAPE=(300, 300, 3)
COLLISION_DEVICE=cpu
INFERENCE=0.6036402583122253
MAX_RSS_MB=1011.4
TARGET_WARNING_COUNT=0
A31_INTEGRATION=PASS
GST_ARGUS: Cleaning up
CONSUMER: Done Success
GST_ARGUS: Done Success
```

The target warning assertions cover:

- `Failed to load image Python extension`
- torchvision `pretrained` deprecation
- OpenCV `Cannot query video position`
- the camera-load sudo password prompt

## Reinstall artifacts

```text
packages/gong-rc-pop_0.4.1+20260716_arm64.deb
SHA256 7d8c67f1750e6bea5b07ad9c847d6dcb799a2ed53051d94e5eec636c2428e406

packages/torchvision-0.16.0-cp38-cp38-linux_aarch64.whl
SHA256 12ee38cc63cb5f0a47c21f9a2f3aaeab738ba9d3dc638b1a05ffaa2a1b8c87d4
```

Reinstall commands on the Jetson:

```bash
sudo dpkg -i gong-rc-pop_0.4.1+20260716_arm64.deb
/home/soda/venvs/gong-rc/bin/python -m pip install --force-reinstall --no-deps \
  torchvision-0.16.0-cp38-cp38-linux_aarch64.whl
sudo systemctl restart jupyter-gong-rc.service
```

The original torchvision directory is backed up at:

```text
/home/soda/venvs/gong-rc/.migration_backups/torchvision_20260716/torchvision_pre_rebuild.tar.gz
```

`pip check` still reports the unrelated pre-existing Ubuntu package issue `launchpadlib 1.10.13 requires testresources`. It does not affect POP, torch, torchvision, or the camera test.
