#!/usr/bin/env python
 
import pygame
import wiringpi2 as wiringpi
import time
import os, sys, math
from collections import namedtuple
import struct

# Key mappings
PS3_SELECT = 0
PS3_L3 = 1
PS3_R3 = 2
PS3_START = 3
PS3_DPAD_UP = 4
PS3_DPAD_RIGHT = 5
PS3_DPAD_DOWN = 6
PS3_DPAD_LEFT = 7
PS3_L2 = 8
PS3_R2 = 9
PS3_L1 = 10
PS3_R1 = 11
PS3_TRIANGLE = 12
PS3_CIRCLE = 13
PS3_CROSS =  14
PS3_SQUARE = 15
PS3_PLAYSTATION = 16

PS3_AXIS_LEFT_H = 0
PS3_AXIS_LEFT_V = 1
PS3_AXIS_RIGHT_H = 2
PS3_AXIS_RIGHT_V = 3
PS3_AXIS_DPAD_UP = 8
PS3_AXIS_DPAD_RIGHT = 9
PS3_AXIS_DPAD_DOWN = 10
PS3_AXIS_DPAD_LEFT = 11 
PS3_AXIS_L2 = 12
PS3_AXIS_R2 = 3
PS3_AXIS_L1 = 14
PS3_AXIS_R1 = 15
PS3_AXIS_TRIANGLE = 16
PS3_AXIS_CIRCLE = 17
PS3_AXIS_CROSS =  18
PS3_AXIS_SQUARE = 19
PS3_AXIS_PLAYSTATION = 16


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
  
# Wait for a joystick
while pygame.joystick.get_count() == 0:
  print 'waiting for joystick count = %i' % pygame.joystick.get_count()
  pygame.joystick.quit()
  time.sleep(1)
  pygame.joystick.init()

# Stop the robot
def stop():
  global i2cConnect, i2cFD

  # Stop the motors
  try:
    sendMessage("\x11", "")
    time.sleep(0.0001)
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
    time.sleep(0.0001)
    result = readMessage(1);
    if ord(result[0:1]) != 0x12:
      print "Failed to set motors!"
  except:
    print "Failed to set motors!"
    i2cFD.flush()
    

# Auto drive
def autoDriveForwards(distance):
  global i2cConnect, i2cFD
  
  print "Driving forwards"
  
  try:
    sendMessage("\x13", struct.pack("!h", distance))
    time.sleep(0.0001)
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
    time.sleep(0.0001)
    result = readMessage(1);
    if ord(result[0:1]) != 0x14:
      print "Failed to set autodrive!"
  except:
    print "Failed to set autodrive!"
    i2cFD.flush()
    # Get a handle on the joystick


j = pygame.joystick.Joystick(0)
j.init()

print 'Initialized Joystick : %s' % j.get_name()


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
    
    while True:
        time.sleep(0.25)
        events = pygame.event.get()
        for event in events:
          if event.type == pygame.JOYBUTTONDOWN:
            if event.button == PS3_CROSS:
              autoDriveForwards(500)
            elif event.button == PS3_SQUARE:
              autoDriveRotate(90)

        # Read in current status
        # outputStatus()
        
except KeyboardInterrupt:
    # Turn off the motors
    stop()
    j.quit()
