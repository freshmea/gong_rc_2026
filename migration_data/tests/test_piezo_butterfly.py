#!/usr/bin/env python3
import time

import RPi.GPIO as GPIO
from pop import PiezoBuzzer

GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

p = PiezoBuzzer(12)

butterfly_scale = [4,4,4, 4,4,4, 4,4,4,4, 4,4,4, 4,4,4,4, 4,4,4, 4,4,4,4, 4,4,4]
butterfly_pitch = [8,5,5, 6,3,3, 1,3,5,6, 8,8,8, 8,5,5,5, 6,3,3, 1,5,8,8, 5,5,5]
butterfly_duration = [8,8,4, 8,8,4, 8,8,8,8, 8,8,4, 8,8,8,8, 8,8,4, 8,8,8,8, 8,8,4]

p.play([butterfly_scale, butterfly_pitch, butterfly_duration])
while p.isPlay():
    time.sleep(0.05)

print("PIEZO_BUZZER_BUTTERFLY_TEST=PASS")
