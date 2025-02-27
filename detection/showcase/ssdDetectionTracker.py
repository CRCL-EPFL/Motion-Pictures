import cv2 as cv
import numpy as np
from imutils.video import VideoStream
import argparse
import time

# SSD people detector with VideoWriter

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", default="../data/mobilenet/MobileNetSSD_deploy.prototxt.txt")
ap.add_argument("-m", "--model", default="../data/mobilenet/MobileNetSSD_deploy.caffemodel")
ap.add_argument("-c", "--confidence", type=float, default=0.4)
args = vars(ap.parse_args())

# init class list
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

IGNORE = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]

print("Loading model...")
net = cv.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# init video stream

vs = VideoStream(src=0).start()
# vs = cv.VideoCapture('../data/video/capturePerspective.mov')
time.sleep(2.0)

# Get matrix for transform

# input_points = np.float32([[300, 236],[1662, 236],[90, 856],[1846, 856]])
input_points = np.array([[300, 236],[1662, 236],[90, 856],[1846, 856]], dtype="float32")

width = 1920
height = int(width*.5625)

# convertedPoints= np.float32([[0, 0], [width, 0], [0, height], [width, height]])
convertedPoints= np.array([[0, 0], [width, 0], [0, height], [width, height]], dtype="float32")

matrix = cv.getPerspectiveTransform(input_points, convertedPoints)
# matrix = cv.findHomography(input_points, convertedPoints)

print("MATRIX")
print(matrix)

print((width, height))
print("Test of the transform matrix")
# print(cv.transform(np.array([[[300, 236],[1662, 236],[90, 856],[1846, 856]]]), matrix)[0])
testArray = np.array([[[300, 236],[1662, 236],[90, 856],[1846, 856]]])
print(testArray.shape)
# testArrayShape = np.reshape(testArray, (1,2,4))
print(cv.transform(np.array([[[300, 236],[1662, 236],[90, 856],[1846, 856]]]), matrix).squeeze())
# print(cv.transform(testArrayShape, matrix).squeeze())
testPoint = np.array([[1661, 235, 1]])
testPoint = np.reshape(testPoint, (3,1))
print(testPoint.shape)
# print(cv.transform(testPoint, matrix))
# print(testPoint*matrix)
print(np.matmul(matrix, testPoint))

while True:
    # frame = vs.read()
    success, frame = vs.read()
    # frame = imutils.resize(frame, width = 600)

    # Init blank frame
    blank = np.zeros((height, width, 3), np.uint8)  

    # gray frame
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    (h,w) = frame.shape[:2]
    blob = cv.dnn.blobFromImage(cv.resize(frame, (300,300)), 0.007843, (300,300), 127.5)

    # pass blob through the network, obtain detections
    net.setInput(blob)
    detections = net.forward()

    for i in np.arange(0, detections.shape[2]):
        # get confidence value of detections
        confidence = detections[0,0,i,2]

        cv.polylines(frame, np.array([[[300, 236],[1662, 236],[1846, 856],[90, 856]]], np.int32), True, (255,0,0), 2)

        # filter out weak detections
        if confidence > args["confidence"]:
            # extract index of class label from detections
            # compute x and y coords of bounding box
            idx = int(detections[0,0,i,1])

            if CLASSES[idx] in IGNORE:
                continue

            box = detections[0,0,i,3:7] * np.array([w,h,w,h])
            (startX, startY, endX, endY) = box.astype("int")
            body_roi = gray[startY:endY, startX:endX]

            label = "{}: {:.2f}%".format(CLASSES[idx], confidence*100)
            cv.rectangle(frame,(startX, startY), (endX, endY), COLORS[idx], 2)
            cv.circle(frame, (int(startX + (endX-startX)/2), endY), 4, (0,255,0), -1)
            # text positioning
            y = startY - 15 if startY-15 > 15 else startY+15
            cv.putText(frame, label, (startX, y), cv.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

            # Draw transformed points onto blank
            dst = cv.transform(np.array([[[int(startX + (endX-startX)/2), endY]]]), matrix)[0]
            print(dst)
            cv.circle(blank, (dst[0][0], dst[0][1]), 3, (0,255,0), -1)


    cv.imshow("frame", frame)
    # Show blank with points
    cv.imshow("transformed", blank)
    cv.imshow("warped", cv.warpPerspective(frame, matrix, (width, height)))

    key = cv.waitKey(1) & 0xFF

    if key == ord("q"):
        break

print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))


cv.destroyAllWindows()
vs.release()
# vs.stop()