# Buzzer PWM8 fix and verification - 2026-07-15

## Outcome

The POP `PiezoBuzzer(12)` path now creates a valid hardware PWM signal on the
Xavier NX 40-pin header without monkey-patching `GPIO.setup()` or manually
writing `/sys/class/pwm/pwmchip4/unexport`.

The supplied Butterfly melody completed successfully with no Python exception.
Electrical PWM and software playback were verified; acoustic output cannot be
measured automatically without attaching a microphone or oscilloscope.

## Root cause

- POP called `GPIO.setup(12, GPIO.OUT)` immediately before `GPIO.PWM(12, ...)`.
  This placed the pad in GPIO mode before creating hardware PWM.
- Physical header pin 32, BCM channel 12, maps to PWM8 controller
  `32f0000.pwm`, exposed as `/sys/class/pwm/pwmchip4`, channel 0.
- Before the fix, Jetson-IO reported physical pin 32 as `unused`; exporting
  `pwmchip4/pwm0` changed sysfs values but could not route PWM to the connector.
- A process interrupted before cleanup could leave `pwm0` exported.
- `PiezoBuzzer.rest()` generated a low-frequency tone instead of silence, and
  `getTempo()` was missing `self`.

## DTB change

NVIDIA Jetson-IO generated a new user-custom DTB with header functions:

- `pwm8` on physical pin 32
- existing `spi1` on pins 19, 21, 23, 24, and 26
- existing M.2 `i2s3` remained enabled

The generated DTS contains `hdr40-pin32`, output pin configuration for
`soc_gpio44_pr0`, and `pwm@32f0000 { status = "okay"; }`.

Post-reboot checks:

- `config-by-pin.py -p 32`: `pwm8`
- `config-by-function.py -l enabled`: `pwm8`, `spi1`, and `i2s3`
- `/dev/spidev0.0`: retained

Backup directory on the Jetson and migration workspace:

`migration_data/raw/backups/buzzer_pwm8_dtb_20260715_134255`

## POP library changes

`PiezoBuzzer` now:

- skips the conflicting `GPIO.setup(channel, GPIO.OUT)` call;
- resolves the PWM chip dynamically from Jetson.GPIO channel metadata;
- unexports only a stale PWM channel not owned by the current process;
- implements a true silent `rest()`;
- validates positive tempo and duration;
- fixes `getTempo(self)`;
- tolerates Python interpreter shutdown ordering in `__del__()`.

Installed package:

- `gong-rc-pop 0.2.3+20260715`
- SHA-256: `35e9a16d0ea03ae1d3115e03bad9309d96fbd120dc1a4093c5c55553edb643bb`

## Verification

### Hardware PWM

`migration_data/tests/test_piezo_buzzer.py` created 440 Hz PWM at 50 percent
duty cycle for channel 12.

```text
chip=/sys/devices/platform/32f0000.pwm/pwm/pwmchip4
channel=0
period=2272727 ns
duty_cycle=1136363 ns
enable=1
PIEZO_BUZZER_PWM_TEST=PASS
```

After cleanup, `pwmchip4` contained no exported `pwm0`, confirming that stale
state was not left behind.

### Supplied melody

`migration_data/tests/test_piezo_butterfly.py` uses the supplied scale, pitch,
and duration lists without a `GPIO.setup` monkey patch or manual sysfs access.

```text
PIEZO_BUZZER_BUTTERFLY_TEST=PASS
```

### Regression checks

- `Cds(7)`: PASS, raw min 1585, max 1749, mean 1665.8, pseudo lux 722
- `jupyter-gong-rc`: active
- `nvargus-daemon`: active
- `nvfancontrol`: active

## Student code

The workaround is no longer required:

```python
import RPi.GPIO as GPIO
from pop import PiezoBuzzer

GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

p = PiezoBuzzer(12)
p.play(sheet_butterfly)
```

## Reproduction and rollback

- DTB setup: `migration_data/scripts/enable_buzzer_pwm8_jetson_io.sh`
- PWM test: `migration_data/tests/test_piezo_buzzer.py`
- Melody test: `migration_data/tests/test_piezo_butterfly.py`
- Decompiled DTB evidence:
  `migration_data/raw/reports/buzzer_pwm8_user_custom.dts`

Rollback restores the previous extlinux configuration:

```bash
BACKUP=/home/soda/gong_rc_2026/migration_data/raw/backups/buzzer_pwm8_dtb_20260715_134255
sudo cp -a "$BACKUP/extlinux.conf.before" /boot/extlinux/extlinux.conf
sudo sync
sudo reboot
```
