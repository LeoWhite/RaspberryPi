#!/usr/bin/env python3

import io
import os
import time
import signal
import subprocess

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

# Instantiates a client
def createClient():
  # Instantiates a client
  return vision.ImageAnnotatorClient()

def getImage():

  # Get the PID of the raspistil process that was launched from crontab using somethign
  # similar to
  # @reboot raspistill -o /tmp/aiyimage.jpg -s -t 0 -w 640 -h 480 &
  raspistillPID = subprocess.check_output(["pidof", "raspistill"])

  # Request that a picture is taken by sending a USR1 signal to the Raspistill process
  os.kill(int(raspistillPID), signal.SIGUSR1)

  # Wait for the photo to be taken
  time.sleep(0.5)

  # The location of the file is hardcoded.
  file_name = "/tmp/aiyimage.jpg"

  # Loads the image into memory, ready for processing
  with io.open(file_name, 'rb') as image_file:
     content = image_file.read()
     return types.Image(content=content)

  # We failed to load in the image, or process it for some reason
  return None
  
def detectLabels(imageToProcess):
  # Perform label detection on the image file
  response = client.label_detection(image=imageToProcess)
  labels = response.label_annotations

  confidentResults = []

  # Walk through all the labels, keeping any that are 80% confident or greator
  for label in labels:
      if label.score >= 0.80:
        confidentResults.append(label.description)

  # Check how many results we got (if any) and output an appropiate response to say
  if (len(confidentResults) > 1):
      print("That is a {}".format(" ".join(confidentResults)))
  elif (len(confidentResults) > 0):
      print("That is {}".format(" ".join(confidentResults)))
  else:
      print("Sorry, I don't know what that is")
      
      
def detectLogo (imageToProcess):
  # Performs label detection on the image file
  response = client.label_detection(image=imageToProcess)  
  logos = response.logo_annotations

  if len(logos) > 0:
    print("That is the {} logo.".format(logos[0].description))
  else:
     print("Sorry, I don't know what logo that is.")
     
client = createClient()

newImage = getImage()

detectLabels(newImage)
