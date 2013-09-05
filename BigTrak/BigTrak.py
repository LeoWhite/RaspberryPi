#!/usr/bin/env python
 
import pygame
import usb.core
import time
import RPi.GPIO as GPIO
import subprocess

pygame.init()

# Setup the various GPIO values, using the BCM numbers for now
DRIVEPWMA = 18
DRIVEA0 = 22
DRIVEA1 = 27
STANDBY = 23
DRIVEPWMB = 4
DRIVEB0 = 24
DRIVEB1 = 25
A0 = False
A1 = False
B0 = False
B1 = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(DRIVEPWMA, GPIO.OUT)
GPIO.setup(DRIVEA0, GPIO.OUT)
GPIO.setup(DRIVEA1, GPIO.OUT)
GPIO.setup(STANDBY, GPIO.OUT)
GPIO.setup(DRIVEPWMB, GPIO.OUT)
GPIO.setup(DRIVEB0, GPIO.OUT)
GPIO.setup(DRIVEB1, GPIO.OUT)

# Set all the drives to 'off'
GPIO.output(DRIVEA0, A0)
GPIO.output(DRIVEA1, A1)
GPIO.output(STANDBY, False)
GPIO.output(DRIVEB0, B0)
GPIO.output(DRIVEB1, B1)

# Enable the PWM outputs
GPIO.output(DRIVEPWMA, True)
GPIO.output(DRIVEPWMB, True)

# Wait for a joystick
while pygame.joystick.get_count() == 0:
  print 'waiting for joystick count = %i' % pygame.joystick.get_count()
  GPIO.output(STANDBY, True)
  time.sleep(1)
  GPIO.output(STANDBY, False)
  time.sleep(1)
  pygame.joystick.quit()
  pygame.joystick.init()


j = pygame.joystick.Joystick(0)
j.init()

print 'Initialized Joystick : %s' % j.get_name()


threshold = 0.60
LeftTrack = 0
RightTrack = 0

def setcommand(axis_val):
    if axis_val > threshold:
        return 1
    elif axis_val < -threshold:
        return 2
    elif abs(axis_val) < threshold:
        return 0
 
def setmotors():
        GPIO.output(DRIVEA0, A0)
        GPIO.output(DRIVEA1, A1)
        GPIO.output(STANDBY, True)
        GPIO.output(DRIVEB0, B0)
        GPIO.output(DRIVEB1, B1)
 
try:
    # Only allow axis and button events
    pygame.event.set_allowed([pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN])

    # Turn on the motors
    GPIO.output(STANDBY, True)
    while True:
        time.sleep(0.1)
        events = pygame.event.get()
        for event in events:
          UpdateMotors = 0
          
          if event.type == pygame.JOYAXISMOTION:
            if event.axis == 1:
              LeftTrack = event.value
              UpdateMotors = 1
            elif event.axis == 3:
              RightTrack = event.value
              UpdateMotors = 1
    
            if UpdateMotors:
              #print 'LeftTrack %f' % LeftTrack
              #print 'RightTrack %f' % RightTrack
              
              # Move forwards
              if (RightTrack > threshold):
                  A0 = False
                  A1 = True
              # Move backwards
              elif (RightTrack < -threshold):
                  A0 = True
                  A1 = False
              else:
                  A0 = False
                  A1 = False
                  
              # As the B motor is flipped we need to drive
              # it in the opposite direction to the A motor
              if (LeftTrack > threshold):
                  B0 = False
                  B1 = True
              # Move backwards
              elif (LeftTrack < -threshold):
                  B0 = True
                  B1 = False
              else:
                  B0 = False
                  B1 = False
            
              setmotors()
            
          if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 14:
              print 'button up axis %d' % event.button
              subprocess.call(["irsend","SEND_ONCE","bigtrak","fire"])
        
        
except KeyboardInterrupt:
    # Turn off the motors
    GPIO.output(STANDBY, False)
    j.quit()
