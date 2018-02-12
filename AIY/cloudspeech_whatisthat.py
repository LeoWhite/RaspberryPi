#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A demo of the Google CloudSpeech recognizer."""

import aiy.audio
import aiy.cloudspeech
import aiy.voicehat
import subprocess
import whatisthat

def main():
    recognizer = aiy.cloudspeech.get_recognizer()
    recognizer.expect_phrase('what is that')
    recognizer.expect_phrase('what logo is that')
    recognizer.expect_phrase('what does that say')

    button = aiy.voicehat.get_button()
    led = aiy.voicehat.get_led()
    aiy.audio.get_recorder().start()

    while True:
        print('Press the button and speak')
        button.wait_for_press()
        print('Listening...')
        text = recognizer.recognize()
        if text is None:
            print('Sorry, I did not hear you.')
        else:
            # Clear the output variable, so we don't repeat any previous results
            output = None
 
            # Determine what action to take
            if 'what is that' in text:
                output = whatisthat.takeAndProcessImage('label')
            elif 'what logo is that' in text:
                output = whatisthat.takeAndProcessImage('logo')
            elif 'what does that say' in text:
                output = whatisthat.takeAndProcessImage('text')
            elif 'goodbye' in text:
                break

            # If we got a result then both print and speak it. 
            if output is not None:
               print(output)
               aiy.audio.say(output)

if __name__ == '__main__':
    main()
