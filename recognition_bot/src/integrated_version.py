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

import io
import os
import sys
import logging
import threading
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


class ImageProcessor(threading.Thread):
    """Process the incoming camera shots
    """

    def __init__(self, owner, net_model, storage_path="."):
        super(ImageProcessor, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.owner = owner
        self.start()
        self.model = net_model
        self.storage_folder = storage_path
        self.identifier = 0

    def run(self):
        # This method runs in a separate thread
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                self.identifier += 1
                try:
                    self.stream.seek(0)
                    # Read the image
                    image = np.asarray(Image.open(self.stream))
                    logging.info('Image received...')

                    classified_image, image_metadata = apply_recognition(image, self.model)
                    time_now = datetime.now()
                    get_date = time_now.strftime('%Y%m%d')
                    get_time = time_now.strftime('%H%M%S')
                    file_name = '_'.join([get_date, get_time,
                                          str(self.identifier), '.jpg'])
                    cv2.imwrite(os.path.join(self.storage_folder, file_name),
                                classified_image)
                    logging.info('Image successfully %(show_photo_name)s handled',
                                 {'show_photo_name': file_name})
                    logging.info(image_metadata)

                    # Set done to True if you want the script to terminate
                    # at some point
                    self.owner.done = True
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    # Return ourselves to the available pool
                    with self.owner.lock:
                        self.owner.pool.append(self)


class ProcessOutput(object):
    """[summary]
    """

    def __init__(self, net_model, storage_path, nthreads=4):
        self.done = False
        # Construct a pool of 4 image processors along with a lock
        # to control access between threads
        self.lock = threading.Lock()
        self.pool = [ImageProcessor(self, net_model, storage_path) for i in range(nthreads)]
        self.processor = None

    def write(self, buf):
        """[summary]

        Arguments:
            buf {[type]} -- [description]
        """
        if buf.startswith(b'\xff\xd8'):
            # New frame; set the current processor going and grab
            # a spare one
            if self.processor:
                self.processor.event.set()
            with self.lock:
                if self.pool:
                    self.processor = self.pool.pop()
                else:
                    # No processor's available, we'll have to skip
                    # this frame; you may want to print a warning
                    # here to see whether you hit this case
                    self.processor = None
                    print("Skipping single frame handling")
        if self.processor:
            self.processor.stream.write(buf)

    def flush(self):
        """properly shut down the pool
        When told to flush (this indicates end of recording), shut down in an
        orderly fashion. First, add the current processor back to the pool.
        """
        if self.processor:
            with self.lock:
                self.pool.append(self.processor)
                self.processor = None
        # Now, empty the pool, joining each thread as we go
        while True:
            with self.lock:
                try:
                    proc = self.pool.pop()
                except IndexError:
                    pass # pool is empty
            proc.terminated = True
            proc.join()


def main():
    
    sensorPin = 13
    frames = 3
    framerate = 3 #fps

    save_location = "../photos/"

    # Setting the GPIO (General Purpose Input Output) pins up
    # so we can detect if they are HIGH or LOW (on or off)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(sensorPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # load our serialized model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe("./model/MobileNetSSD_deploy.prototxt.txt",
                                   "./model/MobileNetSSD_deploy.caffemodel")

    with picamera.PiCamera() as camera:
        camera.resolution = (1024, 768) # (1920, 1440) # 1296x972
        camera.exposure_mode = "sports"
        camera.framerate = framerate

        output = ProcessOutput(net, save_location, nthreads=3)
        camera.capture_sequence(output, use_video_port=False, burst=True)

if __name__ == "__main__":
    sys.exit(main())