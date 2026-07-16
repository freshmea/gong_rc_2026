# SGTL5000 ALSA/PyAudio migration fix

## Result

The migrated Xavier NX now detects the FE-PI Audio Z V2 SGTL5000 codec and
records non-zero audio through ALSA and PyAudio. The configuration survived a
full reboot. SPI1 and PWM8 were also rechecked after both DTB changes and remain
available.

## Root cause

- The pre-migration robot at `192.168.0.46` has an SGTL5000 at I2C bus 8,
  address `0x0a`, connected to I2S5.
- The migrated robot initially had no SGTL5000 node in its active Device Tree.
  ALSA therefore exposed only the Tegra APE interface; recording produced an
  all-zero WAV even though `arecord` and `PyAudio.open()` succeeded.
- After adding the codec, its default capture switch was off and its input was
  `MIC_IN`. The working robot used `LINE_IN`.
- PyAudio error `-9981 Input overflowed` was a separate application issue: the
  notebook loop was unbounded and `stream.read()` raised when Jupyter did not
  drain PortAudio quickly enough.

The many `Unknown PCM front/rear/surround...` and PulseAudio diagnostics are
PortAudio device-enumeration noise. They are not the cause of the recording
failure. The test program temporarily suppresses those diagnostics only while
PyAudio enumerates devices.

## Device Tree repair

The NVIDIA overlay below was merged on top of the existing SPI1/PWM8 custom
DTB, rather than regenerating the header configuration from the stock DTB:

```text
/boot/tegra194-p3668-all-p3509-0000-fe-pi-audio.dtbo
```

Active merged DTB:

```text
/boot/kernel_tegra194-p3668-0000-p3509-0000-user-custom-sgtl5000.dtb
```

Pre-change boot files are retained at:

```text
/boot/dtb-backups/audio_sgtl5000_20260715_1430/
```

Post-boot evidence:

```text
/sys/bus/i2c/devices/8-000a/driver -> .../drivers/sgtl5000
snd_soc_sgtl5000 loaded
H40-SGTL Capture Mux = LINE_IN
/dev/spidev0.0 present
/sys/class/pwm/pwmchip4 present
```

## Mixer settings applied

```text
ADMAIF1 Mux                         I2S5
I2S5 Mux                            ADMAIF1
H40-SGTL Capture Mux                LINE_IN
H40-SGTL Capture Attenuate (-6 dB)  off
H40-SGTL capture switch             on
H40-SGTL capture gain               10/15 (67%)
```

These values were saved with `alsactl store 1`; `alsa-restore.service` restored
them after reboot.

Gain measurements made in the same room were:

| Capture gain | Peak | RMS |
|---:|---:|---:|
| 0/15 | -42.04 dBFS | -56.21 dBFS |
| 5/15 | -33.39 dBFS | -48.42 dBFS |
| 10/15 | -12.38 dBFS | -36.32 dBFS |
| 15/15 | -5.92 dBFS | -28.97 dBFS |

Gain 10 was selected because gain 15 leaves little headroom for a nearby loud
voice. For final classroom calibration, speak at the actual teaching distance
and aim for ordinary speech peaks between about -12 and -6 dBFS. Use
`configure_sgtl5000_capture.sh 8` through `12` to adjust. Avoid enabling AVC as
a first response to low volume because automatic gain also raises room noise.

## Verification

- `arecord`: 3-second 48 kHz mono capture after a reboot; peak -24.74 dBFS,
  RMS -39.40 dBFS in the test environment.
- PyAudio: 5-second 48 kHz mono capture completed without `-9981`; 480,000
  payload bytes, peak -22.08 dBFS, RMS -41.21 dBFS.
- The fixed test uses a finite duration, a 4096-frame buffer, deferred stream
  start, and `exception_on_overflow=False`.

Run the reusable tests with:

```bash
bash migration_data/tests/configure_sgtl5000_capture.sh 10
python3 migration_data/tests/test_pyaudio_record.py --seconds 5 --output out.wav
python3 migration_data/tests/analyze_wav.py out.wav
```
