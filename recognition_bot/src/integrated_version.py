# Raspberry cameratrap demo version:
#  * Picamer takes pictures
#  * binary stream to opencv (installed on raspberry)
#  * model execution on the raspberry
#  * results in HTML page generated on the raspberry
#
# difference here is that we can do a full rerun for each group passing,
# giving less restrictions on data storage
#
#
# Stijn Van Hoey, 2018
#
#==============================================================================

import os
import sys
import time
import logging
from datetime import datetime

import cv2
import picamera
import RPi.GPIO as GPIO
from PIL import Image
import numpy as np

logging.basicConfig(format='%(asctime)s %(message)s',
                    filename='lifewatch_demo_camera_log',
                    level=logging.DEBUG)
logging.info('Lifewatch demo setup started up successfully')

# initialize the list of class labels MobileNet SSD was trained to
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]
COLOR = (212, 85, 0)
CONFIDENCE = 0.3


def apply_recognition(image, neural_net_model):
    """Apply the opencv neural net to a given image

    Arguments:
        image {str} -- which photo?
        model {net} -- OpenCV net
    """

    # run open CV model
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843,
                                 (300, 300), 127.5)
    neural_net_model.setInput(blob)
    detections = neural_net_model.forward()

    detected_objects = []
    for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with
        # the prediction
        confidence = detections[0, 0, i, 2]
        if confidence > CONFIDENCE:
            # extract the index of the class label from the
            # `detections`, then compute the (x, y)-coordinates of
            # the bounding box for the object
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # draw the prediction on the frame
            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
            detected_objects.append(label)
            if CLASSES[idx] == "person":
                cv2.rectangle(image, (startX, startY), (endX, endY), COLOR, 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(image, label, (startX, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR, 2)

    image_info = {"classifications" : detected_objects}

    return image, image_info

def camera_sequence(framerate=3, nframes=3, resolution=(1024, 768)):
    """[summary]
    
    Arguments:
        framerate {[type]} -- [description]
        768 {[type]} -- [description]
    
    Keyword Arguments:
        nframes {[type]} -- [description] (default: {3})
    
    Returns:
        [type] -- [description]
    """
    with picamera.PiCamera() as camera:
        camera.resolution = resolution
        camera.framerate = framerate
        camera.exposure_mode = "sports"

        output = [np.empty((768 * 1024 * 3,), dtype=np.uint8) for i in range(nframes)]
        camera.capture_sequence(output, format='bgr',
                                use_video_port=False, burst=True)
        return output


def main():
    print("running...")

    sensor_pin = 13
    frames = 3
    framerate = 3 
    save_location = "../photos/"

    # Setting the GPIO (General Purpose Input Output) pins up
    # so we can detect if they are HIGH or LOW (on or off)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # load our serialized model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe("./model/MobileNetSSD_deploy.prototxt.txt",
                                   "./model/MobileNetSSD_deploy.caffemodel")

    # Defining our default states so we can detect a change
    prev_state = False
    curr_state = False

    # Starting a loop
    print("start loop")
    while True:
        time.sleep(0.1)
        prev_state = currState

        # Map the state of the camera to our input pins
        # (jumper cables connected to your PIR)
        curr_state = GPIO.input(sensor_pin)

        # Checking that our state has changed
        if curr_state != prev_state:
            new_state = "HIGH" if curr_state else "LOW"
            print("GPIO pin %s is %s" % (sensor_pin, new_state))

            if curr_state:
                # Recording that a PIR trigger was detected
                logging.info('PIR trigger detected')

                # file names based on current datetime
                i = datetime.now()
                get_date = i.strftime('%Y-%m-%d')
                get_time = i.strftime('%H:%M:%S')

                images = camera_sequence()
                for j, image in enumerate(images):
                    annotated_image, image_info = apply_recognition(image, neural_net_model=net)
                    filename = get_date + '_' +  get_time + '_' + str(j) + '.jpg'
                    cv2.imwrite(os.path.join(save_location, filename), 
                                             annotated_image)
                    logging.info(image_info)
                
                # Log that sequence was taken successfully and state the file name so we know which one
                logging.info('Photo sequence handled successfully %(show_photo_name)s', { 'show_photo_name': filename })

            else:

               # print "Waiting for a new PIR trigger to continue"
               logging.info('Waiting for a new PIR trigger to continue')


if __name__ == "__main__":
    sys.exit(main())