#!/usr/bin/env python
# Takes sequences from an FTP and runs automatic recognition
# 
# Stijn Van Hoey, 2018
#
# ==============================================================================

import os
import sys
import time

import cv2
import numpy as np

from jinja2 import FileSystemLoader, Environment

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", 
        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        "sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
CONFIDENCE = 0.3

def run_recognition(filename, image, neural_net_model, output_dir):
    """Apply the opencv neural net to the image

    Arguments:
        filename {str} -- which photo?
        image {cv2 image}
        neural_net_model {net} -- OpenCV net
        output_dir -- where to write the output result?
    """

    # run open CV model
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843,
                                    (300, 300), 127.5)
    neural_net_model.setInput(blob)
    detections = neural_net_model.forward()

    detected_objects = []
    detected_humans = False
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
                detected_humans = True
    cv2.imwrite(os.path.join(output_dir, os.path.basename(filename)), image)

    image_info = {"path" : os.path.join(output_dir, os.path.basename(filename)),
                  "classifications" : detected_objects,
                  "humans": detected_humans}

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

    print("[INFO] loading files...")
    photo_folder = "../photos"
    output_dir = "../annotated_photos"

    image_data = []    
    while True:
        files = sorted(os.listdir(photo_folder))
        if len(files) > 0:
            time.sleep(0.1)
            oldest_file = files[0]
            # apply model
            print("Handling file", oldest_file)
            try: # hacky method to handle zero-size buffered images
                image = cv2.imread(os.path.join(photo_folder, oldest_file))
                image.shape
            except:
                continue
            detections = run_recognition(os.path.join(photo_folder, oldest_file), image,
                                         neural_net_model=net, output_dir=output_dir)
            print(detections)
            image_data.append(detections)
            # delete file
            os.remove(os.path.join(photo_folder, oldest_file))

           # create the output
            data = {}
            data["sequence_images"] = image_data
            print(data)
            create_webpage(data)
        else:
            time.sleep(0.5)
            print("waiting for files")

if __name__ == "__main__":
    sys.exit(main())
