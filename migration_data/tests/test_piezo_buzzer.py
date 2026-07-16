#!/usr/bin/env python3
import argparse
import gc
import os
import time

import RPi.GPIO as GPIO
from pop import PiezoBuzzer


def read_int(path):
    with open(path) as f:
        return int(f.read().strip())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", type=int, default=12)
    parser.add_argument("--frequency", type=int, default=440)
    parser.add_argument("--seconds", type=float, default=1.0)
    args = parser.parse_args()

    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)

    buzzer = PiezoBuzzer(args.channel, freq=args.frequency, duty=0)
    buzzer.setDuty(50)

    info = buzzer.piezo._ch_info
    pwm_dir = os.path.join(info.pwm_chip_dir, "pwm%d" % info.pwm_id)
    values = {
        "chip": info.pwm_chip_dir,
        "channel": info.pwm_id,
        "period": read_int(os.path.join(pwm_dir, "period")),
        "duty_cycle": read_int(os.path.join(pwm_dir, "duty_cycle")),
        "enable": read_int(os.path.join(pwm_dir, "enable")),
    }
    print(values)

    expected_period = int(1_000_000_000 / args.frequency)
    assert values["enable"] == 1
    assert abs(values["period"] - expected_period) <= 1
    assert abs(values["duty_cycle"] * 2 - values["period"]) <= 1

    time.sleep(args.seconds)
    buzzer.setDuty(0)
    buzzer.piezo.stop()
    del buzzer
    gc.collect()
    GPIO.cleanup()
    print("PIEZO_BUZZER_PWM_TEST=PASS")


if __name__ == "__main__":
    main()
