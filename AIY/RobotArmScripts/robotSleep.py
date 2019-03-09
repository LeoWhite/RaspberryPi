#!/usr/bin/env python

import time

import pigpio

pi = pigpio.pi() # Connect to local Pi.

print("Sleeping")

pi.set_servo_pulsewidth(5, 700)
time.sleep(0.5)
pi.set_servo_pulsewidth(12, 1000)
time.sleep(0.5)
pi.set_servo_pulsewidth(24, 1500)
time.sleep(0.5)
pi.set_servo_pulsewidth(26, 660)
time.sleep(0.5)
pi.set_servo_pulsewidth(6, 1500)
time.sleep(0.5)
pi.set_servo_pulsewidth(13, 2500)
# switch servo off
#pi.set_servo_pulsewidth(26, 0);

pi.stop()

