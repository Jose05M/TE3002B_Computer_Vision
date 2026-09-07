import time
import sys
import math
import numpy as np
import cv2

class TrafficLightDetection:
    def __init__(self):
        cameraWidth = 320
        cameraHeight = 240

    def detect_state(self, image):

        image = cv2.resize(image, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)

        h, w, _ = image.shape
        image = image[0:int(h*0.4), :]

        image = cv2.convertScaleAbs(image, alpha=1.5, beta=30)

        image = cv2.GaussianBlur(image, (5,5), 0)

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])

        lower_red2 = np.array([170, 100, 100])
        upper_red2 = np.array([180, 255, 255])

        lower_yellow = np.array([15, 70, 70])
        upper_yellow = np.array([45, 255, 255])

        lower_green = np.array([35, 60, 60])
        upper_green = np.array([95, 255, 255])

        # Máscaras
        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)

        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
        mask_green = cv2.inRange(hsv, lower_green, upper_green)

        kernel = np.ones((5,5), np.uint8)
        mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)
        mask_yellow = cv2.morphologyEx(mask_yellow, cv2.MORPH_OPEN, kernel)
        mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)

        red_pixels = cv2.countNonZero(mask_red)
        yellow_pixels = cv2.countNonZero(mask_yellow)
        green_pixels = cv2.countNonZero(mask_green)

        threshold = 100

        total = red_pixels + yellow_pixels + green_pixels
        # cv2.imshow("Mask Red", mask_red)
        # cv2.imshow("Mask Yellow", mask_yellow)
        # cv2.imshow("Mask Green", mask_green)

        if total == 0:
            return "none"

        red_ratio = red_pixels / total
        yellow_ratio = yellow_pixels / total
        green_ratio = green_pixels / total

        if red_ratio > 0.5 and red_pixels > threshold:
            return "red"
        elif yellow_ratio > 0.5 and yellow_pixels > threshold:
            return "yellow"
        elif green_ratio > 0.5 and green_pixels > threshold:
            return "green"
        else:
            return "none"

if __name__ == "__main__":
    detector = TrafficLightDetection()

    cap = cv2.VideoCapture("video.mp4")

    if not cap.isOpened():
        print("Error: no se pudo abrir el video")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        state = detector.detect_state(frame)

        # Mostrar resultado en pantalla
        cv2.putText(frame, f"Estado: {state}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Video", frame)

        # Presiona 'q' para salir
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
