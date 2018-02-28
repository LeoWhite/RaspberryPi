#!/usr/bin/env python3

"""
The MIT License (MIT)

Copyright (c) 2018 Leo White

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

The functions in this file provides examples for taking photos, processing them
via the Google ImageAnnotatorClient API and returning an appropiate text string
to be spoken.

It is setup to run on a Raspberry Pi as part of the Google Voice AIY project,
but could be modified to run on other platforms (The only OS specific component
is taking the phots)

Further details can be found at http://blog.mybigideas.uk/

Original source, and related files, can be found at https://github.com/LeoWhite/RaspberryPi/tree/master/AIY

"""

import io
import os
import time
import signal
import subprocess
import sys

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

def createClient():
  """Instantiates an instance of an ImageAnnotatorClient """

  # Instantiates a client
  return vision.ImageAnnotatorClient()

def getImage():
  """Takes a fresh picture and returns it as an Image object"""

  # Get the PID of the raspistil process that was launched from crontab using a
  # command similar to
  # @reboot raspistill -o /tmp/aiyimage.jpg -s -t 0 -w 640 -h 480 &
  raspistillPID = subprocess.check_output(["pidof", "raspistill"])

  # Request that a picture is taken by sending a USR1 signal to the Raspistill process
  os.kill(int(raspistillPID), signal.SIGUSR1)

  # Wait for the photo to be taken
  time.sleep(0.5)

  # The location of the file is hardcoded.
  file_name = "/tmp/aiyimage.jpg"

  # Loads the image into memory, ready for processing, and return it
  with io.open(file_name, 'rb') as image_file:
     content = image_file.read()
     return types.Image(content=content)

  # We failed to load in the image, or process it for some reason
  return None
  
def detectLabels(client, imageToProcess):
  """Calls the 'label_detection' function on the Image and returns the high confidence results."""

  # Perform label detection on the image file
  response = client.label_detection(image=imageToProcess)
  labels = response.label_annotations

  confidentResults = []

  # Walk through all the labels, keeping any that are 80% confident or greator
  for label in labels:
      if label.score >= 0.80:
        confidentResults.append(label.description)

  # Check how many results we got (if any) and create an appropiate sentance
  if (len(confidentResults) > 1):
      return "That is a {}".format(" ".join(confidentResults))
  elif (len(confidentResults) > 0):
      return "That is {}".format(" ".join(confidentResults))
  else:
      return "Sorry, I don't know what that is"
      
      
def detectLogo (client, imageToProcess):
  """Calls the 'logo_detection' function on the Image and returns the first result."""

  # Performs logo detection on the image file
  response = client.logo_detection(image=imageToProcess)
  logos = response.logo_annotations

  if len(logos) > 0:
    return "That is the {} logo.".format(logos[0].description)
  else:
     return "Sorry, I don't know what logo that is."

def detectText (client, imageToProcess):
  """Calls the 'text_detection' function on the Image and returns the first result."""

  # Performs text detection on the image file
  response = client.text_detection(image=imageToProcess)
  texts = response.text_annotations

  if len(texts) > 0:
    return "That says {}".format(texts[0].description)
  else:
    return "Sorry, I couldn't read that."

def takeAndProcessImage (processType):
  """Performs all the tasks required to take a new photo and send to Google for analysis."""

  # Creat a client to perform the processing
  client = createClient()

  # Request a new image to be processed
  newImage = getImage()

  # What form of processing do we want?
  if ("logo" == processType):
    # Check for logos
    result = detectLogo(client, newImage)
  elif ("text" == processType):
    # Check for text
    result = detectText(client, newImage)
  else:
    # Default to labels
    result = detectLabels(client, newImage)
  
  return result

# If this is the 'main' file (i.e. not being imported) then default to
# processing an image for any labels
if __name__ == '__main__':
    print(takeAndProcessImage("label"))
