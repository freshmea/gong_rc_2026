# SPI, camera, and fisheye diagnosis - 2026-07-15

## Compared systems

- Migrated: `192.168.0.34`, Ubuntu 20.04, kernel 5.10.216-tegra
- Known-good: `192.168.0.46`, Ubuntu 18.04, kernel 4.9.140-tegra
- Raw evidence:
  - `migration_data/raw/reports/spi_192.168.0.34.txt`
  - `migration_data/raw/reports/spi_192.168.0.46.txt`
  - `migration_data/raw/reports/spi_reference_vs_migrated.diff`

## 1. Cds and SPI

`Cds(7)` calls `spidev.SpiDev().open(0, 0)`. Initially the migrated system had
SPI bus devices in sysfs but no `/dev/spidev0.0`, so POP raised
`FileNotFoundError`.

### First fault: spidev module was not loaded

- Kernel configuration has `CONFIG_SPI_SPIDEV=m`.
- Loading `spidev` created `/dev/spidev0.0`, `.1`, `spidev2.0`, and `.1`.
- Nodes are `root:gpio 0660`; user `soda` belongs to `gpio`.
- `Cds(7)` construction then passed.
- `/etc/modules-load.d/gong-rc-spidev.conf` now loads `spidev` at boot.
- Reproducer: `migration_data/scripts/setup_spi_spidev.sh`.

### Remaining fault: SPI1 header pinmux is missing

After creating the device node, all MCP3208 channels still read exactly zero.
The same transaction on the known-good robot returned representative values:

- channel 0: 11
- channel 2: 865
- channel 4: 3693
- channel 7 (Cds): 2492

The pinctrl comparison is decisive:

- Known-good SPI1 SCK/MISO/MOSI/CS0: `function spi1`, HOG configured.
- Migrated SPI1 SCK/MISO/MOSI/CS0: `MUX UNCLAIMED`.
- Known-good system boots a custom `FE-PI Audio Z V2` DTB.
- Migrated system boots the default `kernel_tegra194-p3668-0000-p3509-0000.dtb`.
- Migrated Jetson-IO reports no enabled function on the 40-pin header.
- Its supported `spi1` function maps to physical pins 19, 21, 23, 24, and 26.

Therefore module loading fixed the missing file, but the ADC remains unusable
because the flashed DTB does not route SPI1 to the 40-pin header. The old
`compatible=spidev` versus new `compatible=tegra-spidev` strings are not the
fault; both bind successfully after their matching module is loaded.

### Proposed DTB step - not yet executed

Back up boot configuration and the current DTB, then generate an SPI1-enabled
DTB with NVIDIA Jetson-IO:

```bash
sudo cp -a /boot/extlinux/extlinux.conf \
  /boot/extlinux/extlinux.conf.pre-gong-rc-spi
sudo cp -a /boot/dtb/kernel_tegra194-p3668-0000-p3509-0000.dtb \
  /boot/dtb/kernel_tegra194-p3668-0000-p3509-0000.dtb.pre-gong-rc-spi
sudo python3 /opt/nvidia/jetson-io/config-by-function.py -o dtb '1=spi1'
sudo reboot
```

After reboot verify: Jetson-IO lists `spi1`; pinctrl shows `function spi1`;
`/dev/spidev0.0` exists; and `test_cds_spi.py` returns a nonzero channel 7.

## 2. Camera messages

### GStreamer position warning

`Cannot query video position: status=0, value=-1, duration=-1` is expected for
a live `nvarguscamerasrc` stream, which has no seek position or finite length.
Argus listed sensor modes, completed setup, connected the producer, and began
captures. `/dev/video0` exists and `nvargus-daemon` is active. This warning is
not a capture failure.

### `No protocol specified`

The Jupyter service has neither `DISPLAY` nor `XAUTHORITY`. `from pop import
Util` imports TensorFlow and CUDA/graphics-related libraries, which can probe
X and emit this line. Jupyter widgets and Argus capture do not require an X11
window, so it is nonfatal. Notebook code should avoid `cv2.imshow()` and use
widget/JPEG display unless an X server is deliberately configured.

### torchvision warning

The optional `torchvision.io.image` native extension has an ABI mismatch with
the NVIDIA PyTorch build. PIL, ImageFolder, transforms, models, AlexNet, and
the CUDA CNN lesson path passed. Rebuild torchvision against NVIDIA PyTorch
only if a lesson directly uses `torchvision.io.read_image`.

## 3. Fisheye distortion

POP's current camera pipeline only captures, flips/resizes with `nvvidconv`,
converts to BGR, and sends frames to appsink. It contains no fisheye undistort
or remap operation. No camera matrix, distortion coefficients, fisheye, or
intrinsic calibration file exists on the robot. `steering_calibration.json`
is unrelated steering calibration.

Accurate correction requires checkerboard images captured with this exact
lens/sensor pair. OpenCV's fisheye model must calculate camera matrix `K` and
distortion vector `D`; resolution-specific maps should then be precomputed and
applied with `cv2.remap()`. Guessing coefficients was intentionally avoided
because it changes lane geometry and CNN inputs.
