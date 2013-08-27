#!/usr/bin/env python
 
import pygame
import math
import time
from Adafruit_PWM_Servo_Driver import PWM
from collections import namedtuple


# Servo names
HAND = 0
WRIST = 1
FORE_ARM = 2
ELBOW = 3
SHOULDER = 4
BASE = 5



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


ServoStruct = namedtuple("ServoStruct", "channel axis min max park")

# Create the list of Servos for the arm
servos=[]
servos.append(ServoStruct(HAND, PS3_AXIS_R1, 800, 1700, 1400))
servos.append(ServoStruct(WRIST, PS3_AXIS_RIGHT_H, 400, 2000, 1250))
servos.append(ServoStruct(FORE_ARM, PS3_AXIS_L1, 1000, 2000, 1500))
servos.append(ServoStruct(ELBOW, PS3_AXIS_RIGHT_V, 500, 2500, 1500))
servos.append(ServoStruct(SHOULDER, PS3_AXIS_LEFT_V, 500, 2500, 1500))
servos.append(ServoStruct(BASE, PS3_AXIS_LEFT_H, 500, 2500, 1500))

servoMids=[]
for servo in servos:
  servoMids.append(servo.min + ((servo.max - servo.min) / 2))

servoCurrent=[]
for servo in servos:
  servoCurrent.append(servo.park)

servoPark=[]
for servo in servos:
  servoPark.append(servo.park)
  
pygame.init()



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


# ===========================================================================
# Example Code for Adafruit 16 channel PWM Driver
# Refactored by ruprecht
# Numbers for HS-55 Servo (20ms/50Hz cycle, 900-2100 us width)
# ===========================================================================

# Initialise the PWM device using the default address 0x40
pwm = PWM(0x40, debug=True)

cycle = 50 # cycle length, Hz

pulseLength = 1000000 / cycle
tick = pulseLength / 4096 # 12 bit resolution

# we need to convert us pulses to 12 bit ticks
def setServoPulse(channel, pulse):
  pwm.setPWM(channel, 0, pulse/tick)

       
def findServoForAxis(axis):
   for i in servos:
     if axis == i.axis:
       return i 

pwm.setPWMFreq(cycle) # Set frequency

# Motor defaults
LeftTrack = 0
Direction = 0
            
for servo in servos:
  setServoPulse(servo.channel, servo.park)
              
def processMotor(event):
          UpdateMotors = 0
          Position = 0
          
          if event.type == pygame.JOYAXISMOTION:
            servo = findServoForAxis(event.axis)
            
            if servo:
              Position = -(event.value)
              UpdateMotors = 1
    
            if UpdateMotors:
              #print 'speed = %f' % Speed, 'Direction %f' % Direction
              NewPosition = servoPark[servo.channel] + (((servo.max - servo.min) / 2) * Position)
              NewPosition = (int)(math.fabs(NewPosition))
              NewPosition = max(NewPosition, servo.min)
              NewPosition = min(NewPosition, servo.max)
             
              if NewPosition != servoCurrent[servo.channel]:
                servoCurrent[servo.channel] = NewPosition
                setServoPulse(servo.channel, servoCurrent[servo.channel])
                        
          elif event.type == pygame.JOYBUTTONDOWN:
              # Remember the current position as the new default
              if event.button == PS3_CROSS:
                servoPark[:] = servoCurrent[:]                          
              elif event.button == PS3_START:
                for servo in servos:
                  servoPark[servo.channel] = servo.park              
                  servoCurrent[servo.channel] = servo.park              
                  setServoPulse(servo.channel, servoCurrent[servo.channel])
 
try:
    while True:
        #time.sleep(0.1)
        events = pygame.event.get()
        for event in events:
          processMotor(event)
        
        
except KeyboardInterrupt:
    # Turn off the motors
    j.quit()
