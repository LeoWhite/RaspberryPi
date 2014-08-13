#!/usr/bin/python
import wiringpi2 as wiringpi

import time
import os, sys

address = 0x07
from collections import namedtuple
import struct

# Define the status structure
StatusStruct = namedtuple("StatusStruct", "start errorFlag batteryVoltage leftMotorCurrent leftMotorEncoder rightMotorCurrent rightMotorEncoder xAxis yAxis zAxis deltaX deltaY deltaZ")
SetMotorStruct = namedtuple("SetMotorStruct", "command leftMotor rightMotor")

# output the current status
def outputStatus():
  global i2cConnect, i2cFD
  
  os.write(i2cConnect, "\x0F")
  time.sleep(0.01)
  status = i2cFD.read(24)
  
  currentStatus = StatusStruct._make(struct.unpack('!bbHhhhhhhhhhh', status))
  print currentStatus
  
# Stop the robot
def stop():
  global i2cConnect, i2cFD

  # Stop the motors
  os.write(i2cConnect, "\x11")
  time.sleep(0.1)
  result = wiringpi.wiringPiI2CRead(i2cConnect)

  if result != 0x11:
    print "Failed to stop!"
    
# Set the motors
def setMotors(leftMotor, rightMotor):
  global i2cConnect, i2cFD
  
  os.write(i2cConnect, struct.pack("!bhh", 0x12, leftMotor, rightMotor))
  time.sleep(0.1)
  result = wiringpi.wiringPiI2CRead(i2cConnect)

  if result != 0x12:
    print "Failed to set motors!"

        
# Configure wiring pi  
wiringpi.wiringPiSetupPhys()

# Open the i2C connection 
i2cConnect = wiringpi.wiringPiI2CSetup(address)
i2cFD = os.fdopen(i2cConnect, "rw", 0)


# Read in current status
outputStatus()

setMotors(0x7F, 0x7F)

time.sleep(0.5)

# Read in current status
outputStatus()

setMotors(0xFF, 0xFF)

time.sleep(0.5)

setMotors(-120, --120)

time.sleep(0.5)

stop()

# Read in current status
outputStatus()
