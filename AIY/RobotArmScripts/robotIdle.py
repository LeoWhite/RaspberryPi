#!/usr/bin/env python

import time

import pigpio

pi = pigpio.pi() # Connect to local Pi.

print("standing")

pi.set_servo_pulsewidth(26, 700)
time.sleep(0.25)
pi.set_servo_pulsewidth(6, 1500)
time.sleep(0.25)
pi.set_servo_pulsewidth(13, 2000)
time.sleep(0.25)
pi.set_servo_pulsewidth(5, 1500)
time.sleep(0.25)
pi.set_servo_pulsewidth(12, 1500)
time.sleep(0.25)
pi.set_servo_pulsewidth(24, 1500)
time.sleep(0.25)

# switch servo off
#pi.set_servo_pulsewidth(26, 0);

pi.stop()

