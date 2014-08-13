#!/usr/bin/python
import wiringpi2 as wiringpi

import time
import os, sys

address = 0x07
#answer = bytearray(24)
from collections import namedtuple
import struct

wiringpi.wiringPiSetupPhys()

i2cConnect = wiringpi.wiringPiI2CSetup(address)
i2cFD = os.fdopen(i2cConnect, "rw", 0)

StatusStruct = namedtuple("StatusStruct", "start errorFlag batteryVoltage leftMotorCurrent leftMotorEncoder rightMotorCurrent rightMotorEncoder xAxis yAxis zAxis deltaX deltaY deltaZ")

# Read in current status
os.write(i2cConnect, "\x0F")
time.sleep(0.01)
answer = i2cFD.read(24)

currentStatus = StatusStruct._make(struct.unpack('!bbHhhhhhhhhhh', answer))
print currentStatus
time.sleep(0.01)

# Stop the motors
os.write(i2cConnect, "\x11")
time.sleep(0.1)
stopped = wiringpi.wiringPiI2CRead(i2cConnect)

if stopped != 0x11:
  print "Failed to stop!"
  print stopped[0]


os.write(i2cConnect, "\x12\x00\x7F\x00\x7F")
time.sleep(0.1)
stopped = wiringpi.wiringPiI2CRead(i2cConnect)

if stopped != 0x12:
  print "Failed to set motors!"
  print stopped[0]

time.sleep(0.5)

os.write(i2cConnect, "\x0F")
time.sleep(0.01)
answer = i2cFD.read(24)

currentStatus = StatusStruct._make(struct.unpack('!bbHhhhhhhhhhh', answer))
print currentStatus

os.write(i2cConnect, "\x12\x00\xFF\x00\xFF")
time.sleep(0.1)
stopped = wiringpi.wiringPiI2CRead(i2cConnect)

time.sleep(0.5)

os.write(i2cConnect, "\x11")
time.sleep(0.1)
stopped = wiringpi.wiringPiI2CRead(i2cConnect)

if stopped != 0x11:
  print "Failed to stop!"
  print stopped[0]

os.write(i2cConnect, "\x0F")
time.sleep(0.01)
answer = i2cFD.read(24)

currentStatus = StatusStruct._make(struct.unpack('!bbHhhhhhhhhhh', answer))
print currentStatus
