import cv2
import time
from picamera2 import Picamera2

def start_face_reg():
    print("in face reg func")
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

    while True:
        frame = picam2.capture_array()
        frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect fullbody, upperbody, and lowerbody
        fullbodies = fullbody_cascade.detectMultiScale(frameGray, 1.1, 1)
        upperbodies = upperbody_cascade.detectMultiScale(frameGray, 1.1, 1)
        lowerbodies = lowerbody_cascade.detectMultiScale(frameGray, 1.1, 1)

        # Draw rectangles for fullbodies (in red)
        for (x, y, w, h) in fullbodies:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Draw rectangles for upperbodies (in blue)
        for (x, y, w, h) in upperbodies:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Draw rectangles for lowerbodies (in green)
        for (x, y, w, h) in lowerbodies:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow("Camera Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(" "):
            print('capture')
            cv2.imwrite("frame-" + str(time.strftime("%H:%M:%S", time.localtime())) + ".jpg", frame)
        if key == ord("q"):
            break

    cv2.destroyAllWindows()

def main():
    print("here")
    start_face_reg()
    print("ending")

if __name__ == "__main__":
    main()
