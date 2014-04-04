#!/usr/bin/env python
 
import pygame
#import usb.core
import math
import time
#import RPi.GPIO as GPIO
import subprocess
import wiringpi2
from collections import namedtuple

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


ServoStruct = namedtuple("ServoStruct", "channel axis min max park gpio")

# Create the list of Servos for the arm
servos=[]
servos.append(ServoStruct(0, PS3_AXIS_RIGHT_V, 0, 100, 50, 8))

servoMids=[]
for servo in servos:
  servoMids.append(servo.min + ((servo.max - servo.min) / 2))

servoCurrent=[]
for servo in servos:
  servoCurrent.append(servo.park)

servoLastPosition=[]
for servo in servos:
  servoLastPosition.append(0)
  
servoPark=[]
for servo in servos:
  servoPark.append(servo.park)
  
  
  
pygame.init()

# Setup the wiring Pi GPIO
io = wiringpi2.GPIO(wiringpi2.GPIO.WPI_MODE_GPIO)
 
# Setup the various GPIO values, using the BCM numbers for now
SERVOA = 8
PWMA = 18
DRIVEA0 = 22
DRIVEA1 = 27
STANDBY = 23
PWMB = 4
DRIVEB0 = 24
DRIVEB1 = 25
A0 = False
A1 = False
B0 = False
B1 = False

wiringpi2.softPwmCreate(SERVOA, 0, 100)
wiringpi2.softPwmCreate(PWMA, 0, 80)
wiringpi2.softPwmCreate(PWMB, 0, 80)

io.pinMode(DRIVEA0, io.OUTPUT)
io.pinMode(DRIVEA1, io.OUTPUT)
#io.pinMode(PWMA, io.PWM_OUTPUT)
io.pinMode(STANDBY, io.OUTPUT)
io.pinMode(DRIVEB0, io.OUTPUT)
io.pinMode(DRIVEB1, io.OUTPUT)
#io.pinMode(PWMB, io.PWM_OUTPUT)

# Set all the drives to 'off'
io.digitalWrite(DRIVEA0, A0)
io.digitalWrite(DRIVEA1, A1)
io.digitalWrite(STANDBY, io.HIGH)
io.digitalWrite(DRIVEB0, B0)
io.digitalWrite(DRIVEB1, B1)

# Enable PWM
wiringpi2.softPwmWrite(SERVOA, 0)
wiringpi2.softPwmWrite(PWMA, 0)
wiringpi2.softPwmWrite(PWMB, 0)

# Wait for a joystick
while pygame.joystick.get_count() == 0:
  print 'waiting for joystick count = %i' % pygame.joystick.get_count()
  io.digitalWrite(STANDBY, io.HIGH)
  time.sleep(1)
  io.digitalWrite(STANDBY, io.LOW)
  time.sleep(1)
  pygame.joystick.quit()
  pygame.joystick.init()

j = pygame.joystick.Joystick(0)
j.init()

print 'Initialized Joystick : %s' % j.get_name()

threshold = 0.20

camThreshold = 0.60
Step = 1

# Motor defaults
LeftTrack = 0
RightTrack = 0
Speed = 0
Direction = 0

#for servo in servos:
#  #setServoPulse(servo.channel, servo.park)

  
def findServoForAxis(axis):
   for i in servos:
     if axis == i.axis:
       return i 

def setcommand(axis_val):
    if axis_val > threshold:
        return 1
    elif axis_val < -threshold:
        return 2
    elif abs(axis_val) < threshold:
        return 0
 
def setmotors():
        io.digitalWrite(DRIVEA0, A0)
        io.digitalWrite(DRIVEA1, A1)
        io.digitalWrite(STANDBY, io.HIGH)
        io.digitalWrite(DRIVEB0, B0)
        io.digitalWrite(DRIVEB1, B1)
        wiringpi2.softPwmWrite(PWMA, (int)((math.fabs(LeftTrack) - threshold) * 80))
        wiringpi2.softPwmWrite(PWMB, (int)((math.fabs(RightTrack) - threshold) * 80))
        
try:
    # Only allow axis and button events
    pygame.event.set_allowed([pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN])

    # Enable the emotors
    io.digitalWrite(STANDBY, io.HIGH)
        
    while True:
        time.sleep(0.01)
        events = pygame.event.get()
        for event in events:
          UpdateMotors = 0
          UpdateCam = 0
          Position = 0
          
          if event.type == pygame.JOYAXISMOTION:
            servo = findServoForAxis(event.axis)
            
            if servo:
              servoLastPosition[servo.channel] = -(event.value)
                        
            if event.axis == 1:
              Speed = -(event.value)
              UpdateMotors = 1
            elif event.axis == 0:
              Direction = event.value
              UpdateMotors = 1
    
            if UpdateCam:
              NewPosition = servoPark[servo.channel] + (((servo.max - servo.min) / 2) * Position)
              NewPosition = (int)(math.fabs(NewPosition))
              NewPosition = max(NewPosition, servo.min)
              NewPosition = min(NewPosition, servo.max)
             
              if NewPosition != servoCurrent[servo.channel]:
                print 'NewPositoin = %f' %NewPosition
                servoCurrent[servo.channel] = NewPosition
                wiringpi2.softPwmWrite(servo.gpio, (int)(servoCurrent[servo.channel]))
    
            if UpdateMotors:
              # We need to work out what speed to drive each of the motors
              LeftTrack = Speed + Direction
              RightTrack = Speed - Direction
              LeftMotorScale = max(1.0, math.fabs(LeftTrack))
              RightMotorScale = max(1.0, math.fabs(RightTrack))
              MaxMotorScale = max(LeftMotorScale, RightMotorScale)
              MaxMotorScale = max(MaxMotorScale, 1)
 
              LeftTrack = LeftTrack/MaxMotorScale
              RightTrack = -(RightTrack/MaxMotorScale)

              # Make forwards/backwards easier
              if math.fabs(LeftTrack + RightTrack) < (threshold * 2):
                RightTrack = -LeftTrack

              #print 'LeftTrack = %f' % LeftTrack, 'RightTrack = %f' % RightTrack
              #print 'LeftMotorScale = %f' % LeftMotorScale, 'RightMotorScale = %f' % RightMotorScale, 'MaxMotorScale = %f' % MaxMotorScale

              # Move forwards
              if (RightTrack > threshold):
                  A0 = io.LOW
                  A1 = io.HIGH
              # Move backwards
              elif (RightTrack < -threshold):
                  A0 = io.HIGH
                  A1 = io.LOW
              else:
                  A0 = io.LOW
                  A1 = io.LOW

              # As the B motor is flipped we need to drive
              # it in the opposite direction to the A motor
              if (LeftTrack > threshold):
                  B0 = io.HIGH
                  B1 = io.LOW
              # Move backwards
              elif (LeftTrack < -threshold):
                  B0 = io.LOW
                  B1 = io.HIGH
              else:
                  B0 = io.LOW
                  B1 = io.LOW
            
              setmotors()
            
          if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 14:
              #print 'button up axis %d' % event.button
              subprocess.call(["irsend","SEND_ONCE","bigtrak","fire"])
        
        for servo in servos:
          if servoLastPosition[servo.channel] != 0:
            NewPosition = servoCurrent[servo.channel]
              
            if (servoLastPosition[servo.channel] > threshold):
              NewPosition = NewPosition + Step
            elif (servoLastPosition[servo.channel] < -threshold):
              NewPosition = NewPosition - Step
                          
            NewPosition = max(NewPosition, servo.min)
            NewPosition = min(NewPosition, servo.max)
              
            if NewPosition != servoCurrent[servo.channel]:
              print 'NewPosition = %f' % NewPosition
              servoCurrent[servo.channel] = NewPosition
              wiringpi2.softPwmWrite(servo.gpio, (int)(math.fabs(servoCurrent[servo.channel])))
                             
except KeyboardInterrupt:
    # Turn off the motors
    io.digitalWrite(STANDBY, io.HIGH)
    j.quit()
