import time
import sys
import math
import numpy as np
import cv2

class CenterLineDetector:
    def __init__(self):
        self.cameraWidth = 320
        self.cameraHeight = 240

        self.last_valid_x = None
        self.filter_weight = 0.35

    def detect_center_line(self, image):
        if image is None:
            return None

        h, w = image.shape[:2]

        crop_start_y = int(h * 0.75)
        bottom_roi = image[crop_start_y:h, 0:w]

        gray = cv2.cvtColor(bottom_roi, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        _, bin_img = cv2.threshold(
            blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        clean_bin = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, kernel)
        clean_bin = cv2.morphologyEx(clean_bin, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(
            clean_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        best_x = None
        best_y = None
        highest_score = -float("inf")

        side_margin = int(w * 0.20)
        roi_area = bottom_roi.shape[0] * bottom_roi.shape[1]

        for cnt in contours:
            area = cv2.contourArea(cnt)

            if area < 120 or area > (roi_area * 0.55):
                continue

            x, y, bw, bh = cv2.boundingRect(cnt)

            if bw <= 0 or bh <= 0:
                continue

            if bh < 8:
                continue

            M = cv2.moments(cnt)
            if M["m00"] == 0:
                continue

            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            if cx < side_margin or cx > (w - side_margin):
                continue

            distance_to_center = abs(cx - (w // 2))
            vertical_preference = cy
            shape_bonus = bh

            if self.last_valid_x is not None:
                temporal_penalty = abs(cx - self.last_valid_x) * 1.5
            else:
                temporal_penalty = 0

            score = (
                area
                - (distance_to_center * 2.0)
                + (vertical_preference * 1.5)
                + (shape_bonus * 4.0)
                - temporal_penalty
            )

            if score > highest_score:
                highest_score = score
                best_x = cx
                best_y = cy

        if best_x is not None:
            if self.last_valid_x is None:
                self.last_valid_x = best_x
            else:
                self.last_valid_x = int(
                    (best_x * self.filter_weight) +
                    (self.last_valid_x * (1.0 - self.filter_weight))
                )

            return (self.last_valid_x, best_y + crop_start_y)

        if self.last_valid_x is not None:
            estimated_y = crop_start_y + int((h - crop_start_y) / 2)
            return (self.last_valid_x, estimated_y)

        return (w // 2, crop_start_y + int((h - crop_start_y) / 2))