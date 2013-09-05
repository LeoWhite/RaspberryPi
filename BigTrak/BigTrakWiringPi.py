#!/usr/bin/env python
 
import pygame
import usb.core
import math
import time
#import RPi.GPIO as GPIO
import subprocess
import wiringpi

pygame.init()

# Setup the wiring Pi GPIO
io = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_GPIO)
 
# Setup the various GPIO values, using the BCM numbers for now
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

wiringpi.softPwmCreate(PWMA, 0, 80)
wiringpi.softPwmCreate(PWMB, 0, 80)

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
wiringpi.softPwmWrite(PWMA, 0)
wiringpi.softPwmWrite(PWMB, 0)

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

# Motor defaults
LeftTrack = 0
RightTrack = 0
Speed = 0
Direction = 0


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
        wiringpi.softPwmWrite(PWMA, (int)((math.fabs(LeftTrack) - threshold) * 80))
        wiringpi.softPwmWrite(PWMB, (int)((math.fabs(RightTrack) - threshold) * 80))
        
try:
    # Only allow axis and button events
    pygame.event.set_allowed([pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN])

    # Enable the emotors
    io.digitalWrite(STANDBY, io.HIGH)
        
    while True:
        time.sleep(0.1)
        events = pygame.event.get()
        for event in events:
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
            if event.button == 14:
              #print 'button up axis %d' % event.button
              subprocess.call(["irsend","SEND_ONCE","bigtrak","fire"])
        
        
except KeyboardInterrupt:
    # Turn off the motors
    io.digitalWrite(STANDBY, io.HIGH)
    j.quit()
