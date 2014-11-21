#!/usr/bin/env python
 
import pygame
import wiringpi2 as wiringpi
import time
import os, sys, math
from collections import namedtuple
import struct

# The I2C address of the arduino
I2CAddress = 0x07

# The trigger and echo pins for the HC-SR04 sensor
SR04Trigger = 22
SR04Echo    = 23

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
  global i2cConnect, i2cFD, LeftTrack, RightTrack

  # Stop the motors
  # Note: We always send the stop, in case the 'current track' information
  # is incorrect
  try:
    sendMessage("\x11", "")
    time.sleep(0.0001)
    result = readMessage(1);
    if ord(result[0:1]) != 0x11:
      print "Failed to stop!"
    else:
      LeftTrack = 0
      RightTrack = 0
  except:
    print "Failed to stop motors!"
    i2cFD.flush()

    
# Set the motors
def setMotors(leftMotor, rightMotor):
  global i2cConnect, i2cFD, LeftTrack, RightTrack
  
  try:
    if LeftTrack != leftMotor or RightTrack != rightMotor:
      sendMessage("\x12", struct.pack("!hh", leftMotor, rightMotor))
      time.sleep(0.0001)
      result = readMessage(1);
      if ord(result[0:1]) != 0x12:
        print "Failed to set motors!"
      else:
        LeftTrack = leftMotor
        RightTrack = rightMotor
        
  except:
    print "Failed to set motors!"
    i2cFD.flush()
    
def turnRight():
  setMotors(150, -150)
  time.sleep(0.1)
  stop()
  time.sleep(0.1)
  

LeftTrack = 0
RightTrack = 0

# Configure wiring pi  
wiringpi.wiringPiSetupPhys()
io = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_GPIO)

# Open the i2C connection 
i2cConnect = wiringpi.wiringPiI2CSetup(I2CAddress)
i2cFD = os.fdopen(i2cConnect, "rw", 0)

# Configure the GPIO
io.pinMode(SR04Trigger, io.OUTPUT)
io.pinMode(SR04Echo, io.INPUT)

io.digitalWrite(SR04Trigger, False)

def getDistance():
  start = 0
  stop = 0
  
  # Trigger the sensor
  io.digitalWrite(SR04Trigger, True)
  time.sleep(0.00001)
  io.digitalWrite(SR04Trigger, False)
  start = time.time()  
  
  # Wait for the response
  while io.digitalRead(SR04Echo)==0:
    start = time.time()  
      
  # And wait for the response to finish
  while io.digitalRead(SR04Echo)==1:
    stop = time.time()  
    
  elapsed = stop-start
  distance = elapsed * 34300
  distance = distance / 2
  
  return distance
  
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
    
    # Allow the system to settle down
    time.sleep(0.5)
    
    # Make sure the motors are stopped
    stop()
    
    # Read in current status    
    outputStatus()
    
    while True:
        currentDistance = 0
        time.sleep(0.1)
        
        # output the distance
        currentDistance = getDistance()
        
        # If the distance is big enough, drive forwards
        if currentDistance >= 75:
          # Move forwards
          if LeftTrack == 0 or RightTrack == 0:
            # Get over the inertia
            setMotors(-150, -150)
            time.sleep(0.05)
            
          setMotors(-50, -50)
        else:
          stop()
          
          turnRight()
          
          
        
        
            
        
        
except KeyboardInterrupt:
    # Turn off the motors
    stop()
