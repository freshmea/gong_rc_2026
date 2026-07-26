# Xavier NX 32GB migration execution log - 2026-07-16

## Scope and current state

Target: Xavier NX Developer Kit with 32 GB microSD, hostname
`gong-rc-32gb`, user `soda`.  USB SSH is `192.168.55.1`; the current Wi-Fi
address is `192.168.0.67` on open network `iptime5G`.

The migration, final reboot, post-boot hardware acceptance tests and reusable
deployment-script updates were completed on 2026-07-17.  The temporary Codex
execution-credit pause occurred before the reboot and caused no target-side
failure or partial write.

## Flash result

- L4T R35.6.4 full 32 GB flash: PASS
- Root filesystem: `/dev/mmcblk0p1`
- Flash log status: `0`
- Flash log markers: `Flashing completed`, `Coldbooting the device`
- Root image ownership fix verified:
  - `/usr/bin/sudo`: `root:root 4755`
  - `/usr/bin/passwd`: `root:root 4755`
  - `/bin/su`: `root:root 4755`
  - `sudo -S true`: PASS

The first generated rootfs was invalid because the host preparation script
recursively changed the extracted rootfs to the host user.  The script no
longer runs recursive `chown`; it explicitly validates the three setuid files
before an image is accepted.

## Repository and storage

Only classroom-essential data was copied to conserve the 32 GB card:

- `autocar/`
- `migration_data/{scripts,system,tests,docs,raw}`
- `gong-rc-pop_0.4.1+20260716_arm64.deb`
- the compatible torchvision 0.16.0 aarch64 wheel

Both package checksums passed.  Historical package archives were not copied.
After JetPack runtime installation the root filesystem had about 8.2 GB free.

## Repository/network repair

The Ubuntu package indexes initially failed because the local network timed out
on `http://ports.ubuntu.com:80`.  `/etc/apt/sources.list` was backed up and the
Ubuntu ARM URLs were changed to HTTPS.  Package indexes then downloaded
normally.  NVIDIA R35.6 repositories were already reachable.

## Installed and verified software

- Ubuntu 20.04.6 / L4T R35.6.4
- ROS2 Foxy Desktop and `rosdep`: `ros2 --help` PASS
- JupyterLab 4.3.8, LAN bind `0.0.0.0:8888`, password `soda`
- Jupyter Terminal command: `/usr/bin/zsh -l`
- Oh My Zsh, tmux 3.0a, Zsh login shell, safe SSH-only tmux attach
- POP deb `0.4.1+20260716`, import path under
  `/usr/lib/python3/dist-packages/pop/`
- Docker 26.1.3, containerd, NVIDIA container runtime
- JetPack 5.1.6 runtime: CUDA 11.4, cuDNN 8.6, TensorRT 8.5.2, VPI,
  NVIDIA OpenCV
- NVIDIA PyTorch `2.1.0a0+41361538.nv23.06`
- torchvision 0.16.0 from the checked local wheel
- NVIDIA TensorFlow `2.12.0+nv23.6`
- scikit-learn 1.3.2, librosa 0.10.2.post1, YOLOv4 2.1.0

Additional compatibility packages required by the runtime-only JetPack
installation were `cuda-nvtx-11-4`, `cuda-nvcc-11-4`, and
`python3-libnvinfer`.  TensorFlow XLA uses
`XLA_FLAGS=--xla_gpu_cuda_data_dir=/usr/local/cuda-11.4`.

## AI validation

`migration_data/tests/validate_ai_stack.sh` runs frameworks in separate fresh
processes.  Final results after the hardware reboot:

- PyTorch CUDA: PASS, device `Xavier`
- torchvision extension import: PASS
- TensorFlow GPU enumeration: PASS, one GPU
- TensorFlow memory growth: PASS (`True`)
- TensorFlow softmax train step: PASS
- `LinearRegression.fit`: PASS, coefficient approximately 3.0
- POP `Pilot` and `Util` imports: PASS
- idle memory after all fresh-process tests: about 1.0 GiB used of 6.7 GiB

This confirms that importing and releasing the AI frameworks no longer leaves
about 5 GiB allocated per kernel.

## Activated hardware configuration

- Jetson-IO generated a combined `spi1 pwm8` user DTB.
- The NVIDIA FE-PI SGTL5000 overlay was merged on top of that DTB, preserving
  SPI and PWM routing.
- `extlinux.conf` default is `JetsonIO` and its FDT is
  `/boot/kernel_tegra194-p3668-0000-p3509-0000-user-custom-sgtl5000.dtb`.
- Backups are stored under
  `migration_data/raw/backups/buzzer_pwm8_dtb_20260716_101437` and
  `migration_data/raw/backups/audio_sgtl5000_20260716_101554`.
- The checked JetPack 5 camera ISP override was installed with SHA-256
  `b6bcafec4e9cc2226d7c23e51e14c9d9ee40192000a1be8588b6ec6f7e9c20e1`.
- `nvargus-daemon` restarted successfully.
- The restricted X service grants display access only to local user `soda`;
  `DISPLAY=:0 xdpyinfo` passed.

## Post-boot incidents and corrections

After reboot the Jetson RNDIS device appeared in Windows as VID:PID
`0955:7020`, but WSL did not automatically bring up its network interface.
`usbipd bind/attach --auto-attach` succeeded, then the WSL interface was given
`192.168.55.100/24`; USB SSH to `192.168.55.1` immediately recovered.  This
was a host-side USBIP interface issue, not a Jetson boot failure.  Wi-Fi also
recovered as `192.168.0.67/24` on `iptime5G`.

The active Device Tree contained both `tegra-spidev` devices, but the kernel
module was not loaded automatically.  Loading `spidev` created
`/dev/spidev0.0` and `.1`; udev then assigned `root:gpio 0660`, allowing user
`soda` access through the existing `gpio` group.  The reusable setup now calls
`setup_spi_spidev.sh` and installs `/etc/modules-load.d/gong-rc-spidev.conf`.

SGTL5000 did not appear as a separate ALSA card, which is expected on this
Tegra topology.  It successfully bound inside APE card 1 as `8-000a`, exposed
the `H40-SGTL` controls, and was routed `ADMAIF1 <-> I2S5`.  Capture mux is
`LINE_IN`, attenuation is off, gain is saved at 10/15.  `LD_PRELOAD` for
`libgomp` and `OPENCV_LOG_LEVEL=ERROR` are now applied to Jupyter and the Zsh
teaching environment so the plugin-scanner static-TLS warning and benign live
stream position warning do not distract students.

The old health check used system Python and obsolete notebook/udev paths.  It
was updated to use `/home/soda/venvs/gong-rc/bin/python`,
`99-rplidar.rules`, and `autocar/jupyter_source`.  The official Foxy package
`ros-foxy-rplidar-ros` is now installed and included in `post_flash_setup.sh`.

## Final acceptance results

- Two cold boots completed.  On the second boot `spidev` loaded without manual
  intervention and both nodes appeared as `root:gpio 0660`; the Device Tree
  reported `spi1`, `pwm8`, `i2s5`, and `i2s3` enabled.
- SPI ADC raw scan: PASS on channels 0-7.
- POP `Cds(7)`: PASS, nonzero live readings (range 1883-2134 during test).
- PWM buzzer: PASS at 440 Hz; sysfs period/duty/enable matched assertions.
- I2C bus 8: SGTL5000 `UU`, EEPROM/device `0x57`, IMU `0x68`, mux `0x70`.
- ALSA record: PASS, 3-second 48 kHz WAV, no overflow; quiet-room result
  RMS -44.03 dBFS and peak -28.94 dBFS.
- ALSA playback: PASS, bounded 440 Hz test tone.
- CSI/Argus camera: PASS, 30/30 frames at 640x480; saved frame mean BGR
  133.18/133.89/138.62.  A second capture with the final environment emitted
  neither the libgomp TLS warning nor the OpenCV position warning.
- LiDAR: PASS, model 40, firmware 1.28, hardware 6, health `Good`; ROS2 Foxy
  driver installed.
- ROS2 CLI: PASS, `ROS_DISTRO=foxy`.
- Jupyter: service active, local and Windows LAN `/lab` both HTTP 302 (expected
  login redirect), Zsh terminal and password `soda` configured.  Allow about
  20 seconds after boot for extension loading before port 8888 is ready.
- Docker: 26.1.3 active, `nvidia` runtime enumerated.  Use `sudo docker` because
  no passwordless Docker-group privilege was granted.
- AI stack after reboot: PASS for PyTorch CUDA, torchvision extension,
  TensorFlow GPU/memory growth/softmax, sklearn LinearRegression and POP AI.
  Memory returned to about 1.1 GiB used with 5.3 GiB available.
- Fan/thermal: `nvfancontrol` active; measured zones were about 45.0-45.5 C.
  PWM was zero at that cool point, which is normal automatic-fan behavior.
- Storage before cache cleanup: 29 GiB root, 19 GiB used, 8.2 GiB available.
  Removing only reproducible pip/APT download caches freed about 2.7 GiB;
  final state is 17 GiB used and 11 GiB available (60%).
- Final `remote_health_check.sh` after the second cold boot: 25 PASS, 0 WARN,
  0 FAIL.

Saved evidence is under `migration_data/reports/runtime_32gb/`:
`audio_capture.wav`, `camera_frame.jpg`, and `camera_frame_quiet.jpg`.

The checked offline packages were preserved after cache cleanup:

- POP deb SHA-256: `7d8c67f1750e6bea5b07ad9c847d6dcb799a2ed53051d94e5eec636c2428e406`
- torchvision wheel SHA-256: `12ee38cc63cb5f0a47c21f9a2f3aaeab738ba9d3dc638b1a05ffaa2a1b8c87d4`

Drive motors were deliberately not actuated while the vehicle was unattended.
The attached buses/drivers were checked non-destructively; a final human
wheel-off-ground motion check remains an operational safety step, not a
software migration blocker.

For the remaining fleet use `XAVIER_NX_20_UNIT_IMAGE_DEPLOYMENT_20260716.md`
and `QSPI_L4T_35.6.4_20_UNIT_PLAN_20260716.md`.  The scripts referenced there
now include the corrections discovered during this 32 GB acceptance run.

## Jupyter lesson bundle and a04 follow-up - 2026-07-17

The 44-file 64 GB classroom source bundle was deployed to the actual Jupyter
root at `/home/soda/Project/python/notebook/gong_rc_2026`.  All 31 notebooks
parsed, the source manifest matched, Jupyter ContentsManager exposed the
folder, and a14 executed with 20 cells and zero errors after both kernel specs
were given the private scikit-learn `libgomp` preload.

The a04 no-sound fault was an ALSA mute state, not a PyAudio failure.  Both
SGTL5000 Headphone and Lineout outputs are now unmuted, saved by `alsactl`,
successfully restored after a forced mute, and a04 completed after restoration.
Full details are in `NOTEBOOK_BUNDLE_AUDIO_A04_FIX_20260717.md`.
