#!/usr/bin/env python

import time

import pigpio

pi = pigpio.pi() # Connect to local Pi.

pi.set_servo_pulsewidth(26, 1800)
time.sleep(0.25)
# switch servo off
#pi.set_servo_pulsewidth(26, 0);

print("Opening")

pi.stop()

