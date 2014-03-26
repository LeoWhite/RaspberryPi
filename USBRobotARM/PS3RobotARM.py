#!/usr/bin/env python
 
import pygame
import usb.core
import time

pygame.init()

# Wait for a joystick
while pygame.joystick.get_count() == 0:
  print 'waiting for joystick count = %i' % pygame.joystick.get_count()
  time.sleep(10)
  pygame.joystick.quit()
  pygame.joystick.init()

j = pygame.joystick.Joystick(0)
j.init()
 
print 'Initialized Joystick : %s' % j.get_name()

armFound = False

while not armFound: 
  dev = usb.core.find(idVendor=0x1267, idProduct=0x0000)
 
  if dev is None:
    print 'Arm not found. Waiting'
    time.sleep(10)
  else:
    armFound = True

 
#this arm should just have one configuration...
dev.set_configuration()

 
# How far to move the JoyStick before it has an effect (0.60 = 60%)
threshold = 0.60

# Key mappings
PS3_BUTTON_SELECT = 0

PS3_AXIS_LEFT_HORIZONTAL = 0
PS3_AXIS_LEFT_VERTICAL = 1
PS3_AXIS_RIGHT_HORIZONTAL = 2
PS3_AXIS_RIGHT_VERTICAL = 3
PS3_AXIS_X = 17
PS3_AXIS_CIRCLE = 18
PS3_AXIS_R1 = 15
PS3_AXIS_R2 = 13

# Robot Arm  defaults
command = (0,0,0)
lc = 0
shoulder = 0
base = 0
elbow = 0
wristup = 0
wristdown = 0
grip_open = 0
grip_close = 0
grip_command = 0 
wrist_command = 0 
shoulder_command = 0
base_command = 0
elbow_command = 0 
            
 
# ARM control related stuff
def setcommand(axis_val):
    if axis_val > threshold:
        return 1
    elif axis_val < -threshold:
        return 2
    elif abs(axis_val) < threshold:
        return 0
 
def buildcommand(shoulc,basec,elbowc,wristc,gripc,lightc):
    byte1 = shoulc + elbowc +  wristc + gripc
    comm_bytes = (byte1, basec, lightc)
    return comm_bytes
    
def processArm(event):
      global command, lc, shoulder, base, elbow, wristup, wristdown, grip_open, grip_close, grip_command, wrist_command, shoulder_command, base_command, elbow_command
      
      if event.type == pygame.JOYBUTTONDOWN:
          if event.button == PS3_BUTTON_SELECT:
            if lc == 0:
              lc = 1
            else:
              lc = 0
      elif event.type == pygame.JOYAXISMOTION:
        if event.axis == PS3_AXIS_LEFT_VERTICAL:
          shoulder = event.value
        elif event.axis == PS3_AXIS_LEFT_HORIZONTAL:
          base = event.value
        elif event.axis == PS3_AXIS_RIGHT_VERTICAL:          
          elbow = event.value
        elif event.axis == PS3_AXIS_R1:    
          wristup = event.value
        elif event.axis == PS3_AXIS_R2:
          wristdown = event.value
        elif event.axis == PS3_AXIS_X:          
          grip_open = event.value
        elif event.axis == PS3_AXIS_CIRCLE:          
          grip_close = event.value

        # Are we opening or closing the gripper?
        if grip_open> threshold:
            grip_command = 1
        elif grip_close> threshold:
            grip_command = 2
        else:
            grip_command = 0
        
        
        # And the same for the wrist, are we moving up or down?
        if wristup > threshold:
            wrist_command = 1*4
        elif wristdown > threshold:
            wrist_command = 2*4
        else:
            wrist_command = 0
        shoulder_command = setcommand(shoulder)*64
        base_command = setcommand(base)
        elbow_command = setcommand(elbow)*16
        
        # Work out what to send out to the robot
        newcommand = buildcommand(shoulder_command,base_command, 
                                  elbow_command, wrist_command, grip_command,lc)
                                  
        # If the command has changed, send out the new one
        if newcommand != command:
            dev.ctrl_transfer(0x40, 6, 0x100, 0, newcommand, 1000)
            command = newcommand


 
try:
    # Loop forwever
    while True:
        # Sleep so we don't eat up all the CPU time
        time.sleep(0.1)
        
        # read in events
        events = pygame.event.get()
        
        # and process them
        for event in events:
            processArm(event) 
        
        
except KeyboardInterrupt:
    j.quit()

