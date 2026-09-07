# actividad-2-04 — Track Center-Line Detection

## 1. Introduction

&ensp;&ensp;Deliverable for **Actividad 2.4** of M2. Visión Computacional (TE3002B, ITESM). Given a color frame from the track camera, detects the center line of the track and returns its coordinates in the original image's reference frame.

## 2. Specification

| # | Step |
|---|---|
| 1 | Receive a color image. |
| 2 | Use only the bottom ¼ of the image. |
| 3 | Detect the track's center line. |
| 4 | Return its coordinates relative to the original image size. |

Constraint: no output files required; tested against the 3DGS simulator, the evaluator runs the function against a reference implementation.

## 3. Implementation

&ensp;&ensp;`CenterLineDetector.detect_center_line()` receives an already-captured frame (no image acquisition of its own — the 3DGS simulator feed is provided externally, over gRPC), crops the bottom 25% of it, converts it to grayscale, and applies Otsu thresholding (inverted) followed by morphological close+open to clean up the binary mask. Among the resulting contours, it scores each candidate by area, distance to the horizontal center, vertical position, and bounding-box height, penalizing large jumps from the previous frame's result; the highest-scoring centroid is smoothed with an exponential filter (`filter_weight=0.35`) against the last valid `x`, and returned in the original image's coordinate system. If no valid contour is found, it falls back to the last known `x` or the image center.

## 4. Requirements

- Python 3
- `opencv-python`
- `numpy`
- 3DGS simulator, for testing against a live track camera feed.

## 5. Output

Evaluator run recorded as evidence:

[`actividad_2_04 video.mp4`](actividad_2_04%20video.mp4) — 360×240, 52s.
