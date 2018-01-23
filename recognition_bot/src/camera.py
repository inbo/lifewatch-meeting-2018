#!/usr/bin/env python
# 
# Based on the excellent official Raspberry Pi tutorials,
# Naturebytes and its contributors
# 
# Stijn Van Hoey, 2018
#
# Useage: camera_handling.py -o <outputlocation>
# ==============================================================================

import os
import sys
import time
import logging
from subprocess import call
from datetime import datetime

import picamera
import RPi.GPIO as GPIO
from gpiozero import MotionSensor

# Logging the activity to a log file.
logging.basicConfig(format='%(asctime)s %(message)s',
                    filename='lifewatch_day_camera_log',
                    level=logging.DEBUG)
logging.info('Lifewatch demo setup started up successfully')

# Assigning a variable to the pins that we have connected the PIR to
sensorPin = 27 # using Broadcom (BCM) pin numbering
frames = 2
framerate = 5 #fps

# Setting the GPIO (General Purpose Input Output) pins up
# so we can detect if they are HIGH or LOW (on or off)
pir = MotionSensor(sensorPin)

# Set default photo location
save_location = "../photos/"

def main():

    # Starting a loop
    print("start loop")
    while True:
        time.sleep(0.1)

        # Checking that our state has changed
        #if pir.when_motion:
        print("GPIO pin %s is low" % (sensorPin))
        pir.wait_for_motion()

        while pir.motion_detected:
            print("GPIO pin %s is %s, high" % (sensorPin, 1))
            i = datetime.now() # Get the time now
            get_date = i.strftime('%Y-%m-%d') # Get and format the date
            get_time = i.strftime('%H:%M:%S') # Get and format the time

            # Recording that a PIR trigger was detected and
            # logging the battery level at this time
            logging.info('PIR trigger detected')

            # Assigning a variable so we can create a photo JPG file that
            # contains the date and time as its name
            photo = get_date + '_' +  get_time + '_%01d.jpg'
            photo_location =  os.path.join(save_location, photo)
            
            logging.info('About to take photo sequence and save to the drive')
            with picamera.PiCamera() as camera:
                camera.resolution = (1024, 768)
                camera.framerate = framerate
                camera.exposure_mode = "sports"
                camera.capture_sequence([photo_location % i for i in range(frames)],
                                        use_video_port=False, burst=True)

            # Log that sequence was taken successfully and state the file name so we know which one
            logging.info('Photo sequence taken successfully %(show_photo_name)s', { 'show_photo_name': photo_location })
            time.sleep(0.1)

if __name__ == "__main__":
    main()

