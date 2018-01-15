#!/usr/bin/env python
# 
# Based on the excellent official Raspberry Pi tutorials,
# Naturebytes and its contributors
# 
# Stijn Van Hoey, 2018
#
# Useage: camera_handling.py -o <outputlocation>
# =========================================================================================

import RPi.GPIO as GPIO
import time
from subprocess import call
from datetime import datetime
import logging
import sys
import os

# Logging the activity to a log file.

logging.basicConfig(format='%(asctime)s %(message)s',
                    filename='lifewatch_day_camera_log',
                    level=logging.DEBUG)
logging.info('Lifewatch demo setup started up successfully')

# Assigning a variable to the pins that we have connected the PIR to
sensorPin = 13

# Setting the GPIO (General Purpose Input Output) pins up
# so we can detect if they are HIGH or LOW (on or off)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensorPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Set default save location
saveLocation = "../photos/"

def main():
    print "running..."

    # Defining our default states so we can detect a change
    prevState = False
    currState = False

    # Starting a loop
    print "start loop"
    while True:
        time.sleep(0.1)
        prevState = currState

        # Map the state of the camera to our input pins
        # (jumper cables connected to your PIR)
        currState = GPIO.input(sensorPin)

        # Checking that our state has changed
        if currState != prevState:
            # About to check if our new state is HIGH or LOW
            newState = "HIGH" if currState else "LOW"
            print "GPIO pin %s is %s" % (sensorPin, newState)
            # print "Battery level detected via pin %s is %s" % (lowbattPin, newBattState)

            if currState:  # Our state has changed, so that must be a trigger from the PIR

                i = datetime.now() # Get the time now
                get_date = i.strftime('%Y-%m-%d') # Get and format the date
                get_time = i.strftime('%H-%M-%S.%f') # Get and format the time

                # Recording that a PIR trigger was detected and
                # logging the battery level at this time
                logging.info('PIR trigger detected')

                # Assigning a variable so we can create a photo JPG file that
                # contains the date and time as its name
                photo = get_date + '_' +  get_time + '.jpg'
                photo_location =  os.path.join(saveLocation, photo)

                # Using the raspistill library to take a photo. You can show
                # that a photo has been taken in a small preview box on the desktop by
                # changing --nopreview to --preview
                cmd = 'raspistill -t 300 -w 1920 -h 1440 --nopreview --output ' + photo_location
                print 'cmd ' + cmd

                # If you find you have permission problems saving to other attached storage devices you can use this line to change the owner of the photo if required
                # perms = 'chown pi:pi /media/usb0/' + photo
                # print 'perms ' +perms

                # Log that we have just taking a photo"
                logging.info('About to take a photo and save to the drive')
                call ([cmd], shell=True)
                # call ([perms], shell=True)

                # Log that a photo was taken successfully and state the file name so we know which one"
                logging.info('Photo taken successfully %(show_photo_name)s', { 'show_photo_name': photo_location })

            else:

               # print "Waiting for a new PIR trigger to continue"
               logging.info('Waiting for a new PIR trigger to continue')

if __name__ == "__main__":
    main()
