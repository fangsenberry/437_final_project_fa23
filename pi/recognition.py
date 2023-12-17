import cv2
import time
from picamera2 import Picamera2
import argparse
import json

perspective = "x" #change this to whatever axes this camera is operating on.

def start_face_reg():
    picam2 = Picamera2()  # Create a camera object

    dispW = 1280
    dispH = 720
    picam2.preview_configuration.main.size = (dispW, dispH)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.preview_configuration.align()
    picam2.preview_configuration.controls.FrameRate = 30

    picam2.configure("preview")
    picam2.start()

    # Load the classifiers
    fullbody_cascade = cv2.CascadeClassifier("models/haarcascade_fullbody.xml")
    upperbody_cascade = cv2.CascadeClassifier("models/haarcascade_upperbody.xml")
    lowerbody_cascade = cv2.CascadeClassifier("models/haarcascade_lowerbody.xml")

    # JSON object to store the results
    json_data = {
        "frames": []
    }

    while True:
        frame = picam2.capture_array()
        frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect fullbody, upperbody, and lowerbody
        fullbodies = fullbody_cascade.detectMultiScale(frameGray, 1.1, 1)
        upperbodies = upperbody_cascade.detectMultiScale(frameGray, 1.1, 1)
        lowerbodies = lowerbody_cascade.detectMultiScale(frameGray, 1.1, 1)

        # Calculate the x-coordinates of the centers
        centers = []
        for (x, y, w, h) in fullbodies + upperbodies + lowerbodies:
            center_x = x + w // 2
            centers.append(center_x)

            # Draw rectangles
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Update JSON object with the current frame's data
        frame_data = {
            "time": time.strftime("%H:%M:%S", time.localtime()),
            "locations": centers
        }
        json_data["frames"].append(frame_data)

        cv2.imshow("Camera Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(" "):
            print('capture')
            cv2.imwrite("frame-" + str(time.strftime("%H:%M:%S", time.localtime())) + ".jpg", frame)
        elif key == ord("q"):
            break

    cv2.destroyAllWindows()
    with open(f"output_{perspective}.json", "w") as outfile:
        json.dump(json_data, outfile, indent=4)

def main():
    start_face_reg()

if __name__ == "__main__":
    main()
