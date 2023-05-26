import cv2
from ultralytics import YOLO
import numpy as np
from tracking.tracker import Tracker

# Settings for unwarp fisheye 
DIM=(1280, 720)
K=np.array([[715.0845213313972, 0.0, 649.466032885757], [0.0, 714.7508174031162, 349.07092982998165], [0.0, 0.0, 1.0]])
D=np.array([[-0.018535944017385605], [-0.036164616733474465], [0.0996012486725898], [-0.08137886264463776]])

# Store map results
map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)

def undistort(img, map1, map2):  
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)    
    return undistorted_img

# Load the YOLOv8 model
model = YOLO('yolov8n.pt')

# Open the video file1
cap1 = cv2.VideoCapture(0)

# Set camera stream dimensions
# cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
# cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
# cap1.set(cv2.CAP_PROP_FPS, 60)

# Width and height of projection area in pixels
w = 1920
h = 1880

# Corner points to be perspective transformed
inputPoints = np.float32([[410, 282],[716, 243],[481, 596],[889, 488]])
convertedPoints= np.float32([[0, 0], [w, 0], [0, h], [w, h]])
matrix = cv2.getPerspectiveTransform(inputPoints, convertedPoints)

track = Tracker((w, h))

# Loop through the video frames
while cap1.isOpened():
    # Read a frame from the video
    success1, frame1 = cap1.read()

    # Init blank frame
    blank = np.zeros((h, w, 3), np.uint8)

    # track = Tracker((w, h))
    points1 = []

    if success1:
        frame1 = cv2.rotate(frame1, cv2.ROTATE_180)

        frame1 = undistort(frame1, map1, map2)

        # Run YOLOv8 inference on the frame
        results1 = model.track(frame1, classes=0, tracker="botsort.yaml", imgsz=320, persist=True)

        if results1[0].boxes.id != None:
            print("In results")
            boxes = results1[0].boxes.xyxy.cpu().numpy().astype(int)
            ids = results1[0].boxes.id.cpu().numpy().astype(int)
            # print(ids)
            
            for box, id in zip(boxes, ids):
                # Get coordinates of middle
                point = (int(box[0] + (box[2] - box[0])/2), box[3])
                # points1.append(point)

                transPoint = cv2.perspectiveTransform(np.float32(np.array([[[point[0], point[1]]]])), matrix)[0][0]
                # Add transformed points to the array for tracker
                points1.append((int(transPoint[0]), int(transPoint[1])))

                # print(transPoint)

                # Annotate frame
                cv2.circle(frame1, point, 4, (255,0,0), -1)
                # cv2.circle(blank, (int(transPoint[0]), int(transPoint[1])), 4, (0,0,255), -1)
                cv2.rectangle(frame1, (box[0], box[1]), (box[2], box[3]), (0,255,0), 2)

            objects = track.update(ids, points1)

            for (id, point) in objects.items():
                # cv2.circle(frame1, centroid, 4, (0,0,255), -1)
                formatPoint = (int(point[0] * w), int(point[1] * h))
                print("POINT to draw: " + str(formatPoint))
                cv2.circle(blank, formatPoint, 8, (0,0,255), -1)
            # for object in objects:
            #     cv2.circle(frame1, object.values(), 4, (0,0,255), -1)

        # Display the annotated frame
        cv2.imshow("annotate1", frame1)
        cv2.imshow("blank1", blank)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        
    else:
        break

# Release the video capture object and close the display window
cap1.release()
cv2.destroyAllWindows()
