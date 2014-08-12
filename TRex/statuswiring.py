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

#def write(value):
#        bus.write_byte_data(address, 0x0f, value)
#        return -1

while 1:
  wiringpi.wiringPiI2CWrite(i2cConnect, 0x0f)
  time.sleep(0.01)
  answer = i2cFD.read(24)

  currentStatus = StatusStruct._make(struct.unpack('!bbHhhhhhhhhhh', answer))
  print currentStatus
  time.sleep(0.01)

