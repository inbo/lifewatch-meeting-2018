#!/usr/bin/env python
# Takes sequences from an FTP and runs automatic recognition
# 
# Stijn Van Hoey, 2018
#
# ==============================================================================

import os
import sys

import cv2
import numpy as np

from creds import RASPIP, RASPUSR, RASPPWD
from ftp_connector import FTPConnector
from jinja2 import FileSystemLoader, Environment

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", 
        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        "sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
CONFIDENCE = 0.3

frames = 3

def load_last_sequence_ftp(url, usr, pwd, subfolder, remove_on_pi=False):
    """Load the latest available sequence from FTP
    Arguments:
        url {str} -- ip adress of the raspberry
        usr {str} -- username
        pwd {str} -- password
    """
    local_prefix = "../photos"
    ftp_con = FTPConnector(url, usr, pwd, subfolder)
    last_sequence_names = list(ftp_con.list_files())[-frames:]
    for filename in last_sequence_names:
        if not os.path.exists(os.path.join(local_prefix, filename)):
            ftp_con.download_file(filename, local_path_prefix=local_prefix)
    # remove the Files
    if remove_on_pi:
        for filename in last_sequence_names:
            ftp_con.delete_file(filename)
    return last_sequence_names

def run_recognition(filename, neural_net_model):
    """Apply the opencv neural net to the image
    
    Arguments:
        filename {str} -- which photo?
        model {net} -- OpenCV net
    """

    # run open CV model
    image = cv2.imread(filename)
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
            if CLASSES[idx] == "person": # only show humans...TOIMPPROVE
                cv2.rectangle(image, (startX, startY), (endX, endY), COLORS[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(image, label, (startX, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
    cv2.imwrite(filename, image)

    image_info = {"path" :filename,
                  "classifications" : detected_objects}

    return image_info

def create_webpage(data, html_template="../static/template.html",
                   html_output="./index.html"):
    """[summary]
    """
    env = Environment(loader=FileSystemLoader(os.path.dirname(html_template)))
    template = env.get_template(os.path.basename(html_template))
    html = template.render(data)

    index_page = open(html_output, "w")
    index_page.write(str(html))
    index_page.close()

def main():

    # load our serialized model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe("./model/MobileNetSSD_deploy.prototxt.txt", 
                                "./model/MobileNetSSD_deploy.caffemodel")

    print("[INFO] downloading files...")
    photo_folder = "./Documents/lifewatch-meeting-2018/recognition_bot/photos"
    filenames = load_last_sequence_ftp(RASPIP, RASPUSR, RASPPWD, photo_folder,
                                       remove_on_pi=True) # Put True to keep Pi clean
    print(filenames)
    print(os.path.join("../photos", filenames[0]))
    print("[INFO] applying model...")
    image_data = []
    for filename in filenames:
        detections = run_recognition(os.path.join("../photos", filename),
                                     neural_net_model=net)
        print(detections)
        image_data.append(detections)
    
    data = {}
    data["sequence_images"] = image_data
    print(data)
    create_webpage(data)

if __name__ == "__main__":
    sys.exit(main())
