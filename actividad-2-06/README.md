# actividad-2-06 — Traffic Sign Detection (YOLO + SSIM)

## 1. Introduction

&ensp;&ensp;Deliverable for **Actividad 2.6** of M2. Visión Computacional (TE3002B, ITESM). Hybrid pipeline that detects traffic signs on a track video and reports which one is directly in front of the vehicle, combining a fine-tuned YOLOv8 model with an SSIM similarity check against reference templates.

## 2. Specification

| # | Step |
|---|---|
| 1 | Combine at least two of the approaches from class (image-quality metric, template matching, Haar cascade, or CNN) into one detection pipeline. |
| 2 | Detect Stop, Workers, Go Straight, Turn Left, and Turn Right signs, and report which one is in front. |
| 3 | Generate a video of the detection result. |


## 3. Implementation

&ensp;&ensp;A YOLOv8 model fine-tuned on a 5-class Roboflow dataset (`dataset/runs/detect/train/weights/best.pt`) detects sign candidates per frame (`conf=0.3`, filtered by a minimum bounding-box area). Each detected ROI is compared via SSIM against a reference template for its class (`template/`). YOLO confidence, SSIM score, and box area are fused into one score (`0.6·conf + 0.3·ssim + 0.001·area`); the highest-scoring detection is reported as the sign in front (`FRONT: <label>`), drawn on the output frame alongside all detections.

## 4. Requirements

- Python 3
- `ultralytics` (YOLOv8)
- `opencv-python`
- `scikit-image`

## 5. How To Run

```bash
python3 actividad_2_06.py
```

Reads `video.mp4`, writes annotated output to `output.mp4`. Requires the trained weights at `dataset/runs/detect/train/weights/best.pt` and the reference images in `template/`.

## 6. Output

[`output.mp4`](output.mp4) — detections and per-frame "FRONT" call drawn over the input video.

Training artifacts for the fine-tuned model are under [`dataset/runs/detect/train/`](dataset/runs/detect/train/) (precision/recall curves, confusion matrix).
