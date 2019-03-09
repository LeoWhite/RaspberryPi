#!/usr/bin/env python

import time

import pigpio

pi = pigpio.pi() # Connect to local Pi.

pi.set_servo_pulsewidth(6, 2500)
time.sleep(0.5)
pi.set_servo_pulsewidth(13, 1500)
time.sleep(1)
pi.set_servo_pulsewidth(13, 2000)
time.sleep(1)
pi.set_servo_pulsewidth(13, 1500)
time.sleep(1)
pi.set_servo_pulsewidth(13, 2000)

time.sleep(1)
pi.set_servo_pulsewidth(6, 1500)
pi.stop()

