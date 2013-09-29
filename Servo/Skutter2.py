#!/usr/bin/env python
 
import pygame
import math
import time
from Adafruit_PWM_Servo_Driver import PWM
from collections import namedtuple
import wiringpi

# Setup the wiring Pi GPIO
io = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_GPIO)

# Setup the various GPIO values, using the BCM numbers for now
DRIVEA0 = 22
DRIVEA1 = 27
PWMA = 4
STANDBY = 23
DRIVEB0 = 25
DRIVEB1 = 24
PWMB=18
A0 = io.LOW
A1 = io.LOW
B0 = io.LOW
B1 = io.LOW

# The different drive methods
DRIVE = 0
ARM = 1

# Default to driving the motors
SKUTTERMODE = DRIVE

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

# Configure the motors
wiringpi.softPwmCreate(PWMA, 0, 80)
wiringpi.softPwmCreate(PWMB, 0, 80)

io.pinMode(DRIVEA0, io.OUTPUT)
io.pinMode(DRIVEA1, io.OUTPUT)
io.pinMode(STANDBY, io.OUTPUT)
io.pinMode(DRIVEB0, io.OUTPUT)
io.pinMode(DRIVEB1, io.OUTPUT)

# Set all the drives to 'off'
io.digitalWrite(DRIVEA0, A0)
io.digitalWrite(DRIVEA1, A1)
io.digitalWrite(STANDBY, io.HIGH)
io.digitalWrite(DRIVEB0, B0)
io.digitalWrite(DRIVEB1, B1)

# Enable PWM
wiringpi.softPwmWrite(PWMA, 0)
wiringpi.softPwmWrite(PWMB, 0)

# Confgure the Servo configurations
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

servoLastPosition=[]
for servo in servos:
  servoLastPosition.append(0)
  
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
RightTrack = 0
Speed = 0
Direction = 0
MotorThreshold = 0.20
            
threshold = 0.60
Step = 2.5

for servo in servos:
  setServoPulse(servo.channel, servo.park)

def changemode():
    global SKUTTERMODE, command, lc
    
    if SKUTTERMODE == DRIVE:
        print 'Switching to ARM'
        # Stop the motors
        A0 = io.LOW
        A1 = io.LOW
        B0 = io.LOW
        B1 = io.LOW
          
        setmotors()

        # Now turn the drive controller off
        # This should make the light on the BigTrak go out
        io.digitalWrite(STANDBY, io.LOW)
  
        # Turn the light on
        # Currently no light to turn on!
        
        SKUTTERMODE = ARM
    else:
        print 'Switching to Motor'
          
        # Stop the ARM
        for servo in servos:
          servoLastPosition[servo.channel] = 0
          
        # Turn the light off on the arm
        # Need to add a light onto the ARM
                      
        # Enable the emotors
        io.digitalWrite(STANDBY, io.HIGH)
          
        SKUTTERMODE = DRIVE           

def setmotors():
        io.digitalWrite(DRIVEA0, A0)
        io.digitalWrite(DRIVEA1, A1)
        io.digitalWrite(STANDBY, io.HIGH)
        io.digitalWrite(DRIVEB0, B0)
        io.digitalWrite(DRIVEB1, B1)
        wiringpi.softPwmWrite(PWMA, (int)((math.fabs(LeftTrack) - threshold) * 80))
        wiringpi.softPwmWrite(PWMB, (int)((math.fabs(RightTrack) - threshold) * 80))
 
def processMotor(event):
          global LeftTrack, RightTrack, Speed, Direction, A0, A1, B0, B1
          
          UpdateMotors = 0
          
          if event.type == pygame.JOYAXISMOTION:
            if event.axis == 1:
              Speed = -(event.value)
              UpdateMotors = 1
            elif event.axis == 0:
              Direction = event.value
              UpdateMotors = 1
    
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
              if event.button == PS3_SELECT:
                changemode()
                
              print 'button up axis %d' % event.button

              
def processArm(event):
          UpdateMotors = 0
          Position = 0
          
          if event.type == pygame.JOYAXISMOTION:
            servo = findServoForAxis(event.axis)
            
            if servo:
              servoLastPosition[servo.channel] = -(event.value)
              UpdateMotors = 1
                            
          elif event.type == pygame.JOYBUTTONDOWN:
              # Remember the current position as the new default
              if event.button == PS3_CROSS:
                servoPark[:] = servoCurrent[:]                          
              elif event.button == PS3_START:
                for servo in servos:
                  servoPark[servo.channel] = servo.park              
                  servoCurrent[servo.channel] = servo.park              
                  setServoPulse(servo.channel, servoCurrent[servo.channel])
 
          if event.type == pygame.JOYBUTTONDOWN:
              if event.button == PS3_SELECT:
                changemode()
 
try:
    while True:
        #time.sleep(0.1)
        events = pygame.event.get()
        for event in events:
          if SKUTTERMODE == DRIVE:
            processMotor(event)
          else:
            processArm(event) 

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
              # print 'NewPosition = %f' % NewPosition
              servoCurrent[servo.channel] = NewPosition
              setServoPulse(servo.channel, (int)(math.fabs(servoCurrent[servo.channel])))              
        
        
except KeyboardInterrupt:
    # Turn off the motors
    io.digitalWrite(STANDBY, io.LOW)
    j.quit()
    
