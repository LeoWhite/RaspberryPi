#!/usr/bin/env python
 
import pygame
import wiringpi2 as wiringpi
import time
import os, sys
from collections import namedtuple
import struct

# The I2C address of the arduino
I2CAddress = 0x07

# Initialise the pygame library, ready for use
pygame.init()

# Define the status structure
StatusStruct = namedtuple("StatusStruct", "start errorFlag batteryVoltage leftMotorCurrent leftMotorEncoder rightMotorCurrent rightMotorEncoder xAxis yAxis zAxis deltaX deltaY deltaZ")
SetMotorStruct = namedtuple("SetMotorStruct", "command leftMotor rightMotor")

# output the current status of the robot
def outputStatus():
  global i2cConnect, i2cFD
  
  try:
    os.write(i2cConnect, "\x0F")
    # Reading in the acceleromotor readings takes time
    time.sleep(0.001)
    status = i2cFD.read(24)
  
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
    os.write(i2cConnect, "\x11")
    time.sleep(0.0001)
    result = wiringpi.wiringPiI2CRead(i2cConnect)
    if result != 0x11:
      print "Failed to stop!"
  except:
    print "Failed to stop motors!"
    i2cFD.flush()

    
# Set the motors
def setMotors(leftMotor, rightMotor):
  global i2cConnect, i2cFD
  
  try:
    os.write(i2cConnect, struct.pack("!bhh", 0x12, leftMotor, rightMotor))
    time.sleep(0.0001)
    result = wiringpi.wiringPiI2CRead(i2cConnect)
    if result != 0x12:
      print "Failed to set motors!"
  except:
    print "Failed to set motors!"
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
        time.sleep(0.1)
        events = pygame.event.get()
        for event in events:
          UpdateMotors = 0
          NewLeftTrack = 0;
          NewRightTrack = 0;
          
          if event.type == pygame.JOYAXISMOTION:
            if event.axis == 1:
              NewLeftTrack = event.value * 0xFF
              if NewLeftTrack != LeftTrack:
                LeftTrack = NewLeftTrack
                UpdateMotors = 1
            elif event.axis == 3:
              NewRightTrack = event.value * 0xFF
              if NewRightTrack != RightTrack:
                RightTrack = NewRightTrack
                UpdateMotors = 1
    
            if UpdateMotors:
              #print 'LeftTrack %f' % LeftTrack
              #print 'RightTrack %f' % RightTrack
                          
              setmotors()
            
        
        
except KeyboardInterrupt:
    # Turn off the motors
    stop()
    j.quit()
