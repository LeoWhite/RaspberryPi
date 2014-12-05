#!/usr/bin/env python
 
import pygame
import wiringpi2 as wiringpi
import time
import os, sys, math
from collections import namedtuple
import struct


# The I2C address of the arduino
I2CAddress = 0x07

# Initialise the pygame library, ready for use
pygame.init()

# Define the status structure
StatusStruct = namedtuple("StatusStruct", "start errorFlag batteryVoltage leftMotorCurrent leftMotorEncoder rightMotorCurrent rightMotorEncoder xAxis yAxis zAxis deltaX deltaY deltaZ")
SetMotorStruct = namedtuple("SetMotorStruct", "command leftMotor rightMotor")

def sendMessage(cmd, message):
  newMessage =  cmd + message
  
  # Calculate checksum
  CS = len(newMessage)
  for i in range(0, len(newMessage)):
    CS = (CS & 0xFF ^ ord(newMessage[i:i+1]) & 0xFF)
    
  finalMessage = newMessage + chr(CS)
    
  os.write(i2cConnect, finalMessage)
  
def readMessage(length):
    # Read in data plus checksum
    status = i2cFD.read(length + 1)
    
    if len(status) == (length + 1):
      CS = length;
      for i in range(0, length):
        CS = (CS & 0xFF ^ ord(status[i:i+1]) & 0xFF)
      
      if CS == ord(status[length:length+1]):
        # Process checksum,
        return status[:length]
      else:
        print "Checksum mismatch!"
        
    return 0
        
# output the current status of the robot
def outputStatus():
  global i2cConnect, i2cFD
  
  try:
    sendMessage("\x0F", "")

    #os.write(i2cConnect, "\x0F")
    # Reading in the acceleromotor readings takes time
    time.sleep(0.001)
    status = readMessage(24)
  
    currentStatus = StatusStruct._make(struct.unpack('!bbHhhhhhhhhhh', status))
    print currentStatus
  except:
    print "Failed to read status"
    i2cFD.flush()
  
# Stop the robot
def stop():
  global i2cConnect, i2cFD

  # Stop the motors
  try:
    sendMessage("\x11", "")
    time.sleep(0.001)
    result = readMessage(1);
    if ord(result[0:1]) != 0x11:
      print "Failed to stop!"
  except:
    print "Failed to stop motors!"
    i2cFD.flush()

    
# Set the motors
def setMotors(leftMotor, rightMotor):
  global i2cConnect, i2cFD
  
  try:
    sendMessage("\x12", struct.pack("!hh", leftMotor, rightMotor))
    time.sleep(0.001)
    result = readMessage(1);
    if ord(result[0:1]) != 0x12:
      print "Failed to set motors!"
  except:
    print "Failed to set motors!"
    i2cFD.flush()
    

# Auto drive
def autoDrive(distance, power):
  global i2cConnect, i2cFD
  
  print "Driving"
  
  try:
    sendMessage("\x13", struct.pack("!hh", distance, power))
    time.sleep(0.01)
    result = readMessage(1);
    if ord(result[0:1]) != 0x13:
      print "Failed to set autodrive!"
  except:
    print "Failed to set autodrive!"
    i2cFD.flush()

# Auto drive
def autoDriveRotate(angle):
  global i2cConnect, i2cFD
  
  print "Rotating"

  try:
    sendMessage("\x14", struct.pack("!h", angle))
    time.sleep(0.01)
    result = readMessage(1);
    if ord(result[0:1]) != 0x14:
      print "Failed to set autodrive!"
  except:
    print "Failed to set autodrive!"
    i2cFD.flush()
    # Get a handle on the joystick



threshold = 0.60
LeftTrack = 0
RightTrack = 0

# Configure wiring pi  
wiringpi.wiringPiSetupPhys()

# Open the i2C connection 
i2cConnect = wiringpi.wiringPiI2CSetup(I2CAddress)
i2cFD = os.fdopen(i2cConnect, "rw", 0)


def setcommand(axis_val):
    if axis_val > threshold:
        return 1
    elif axis_val < -threshold:
        return 2
    elif abs(axis_val) < threshold:
        return 0
 
def setmotors():
  setMotors(LeftTrack, RightTrack)  
 
try:
    # Only allow axis and button events
    pygame.event.set_allowed([pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN])

    # Make sure the motors are stopped
    stop()
    
    # Read in current status
    outputStatus()
    
    setMotors(50, 50)
    time.sleep(3)
    outputStatus()
    stop()

    
        
except KeyboardInterrupt:
    # Turn off the motors
    stop()
