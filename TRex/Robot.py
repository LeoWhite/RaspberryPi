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
              NewLeftTrack = math.ceil(event.value * 0x7F)
              if NewLeftTrack != LeftTrack:
                LeftTrack = NewLeftTrack
                UpdateMotors = 1
            elif event.axis == 3:
              NewRightTrack = math.ceil(event.value * 0x7F)
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
