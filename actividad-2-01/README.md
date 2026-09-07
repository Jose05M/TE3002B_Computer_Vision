# actividad-2-01 — Geometric Transformations with OpenCV

## 1. Introduction

&ensp;&ensp;Deliverable for **Actividad 2.1** of M2. Visión Computacional (TE3002B, ITESM). Given an input video, the script extracts four specific frames and applies a different 2D geometric transform to each one using raw OpenCV primitives (no high-level convenience wrappers for the rotation): non-uniform scaling, a rotation about the image center expressed as an explicit homogeneous matrix, and a horizontal flip.

## 2. Specification

| # | Frame | Operation | Output |
|---|---|---|---|
| 1 | 10 | Scale by **1.5×** | `frame_10.png` |
| 2 | 30 | Scale by **0.5×** | `frame_30.png` |
| 3 | 50 | Rotate **35°** about its center; persist the 3×3 transform matrix | `frame_50.png`, `rotation_matrix.pkl` |
| 4 | 70 | Horizontal flip | `frame_70.png` |

Constraint: no `cv2.imshow` — output-only, no interactive display.

## 3. Implementation

&ensp;&ensp;`video.mp4` (H.264, 1920×1080, 30 fps, 422 frames) is scanned sequentially with `cap.read()` to pull frames 10, 30, 50, and 70. Scaling uses `cv2.resize` (default `INTER_LINEAR`). The rotation is built as an explicit 3×3 homogeneous matrix — translate center to origin, rotate 35°, translate back — rather than `cv2.getRotationMatrix2D`, so that the full matrix can be persisted to `rotation_matrix.pkl`; it's then applied via `cv2.warpAffine` on its 2×3 slice. The flip uses `cv2.flip(frame, 1)`.

## 4. Requirements

- Python 3
- `opencv-python`
- `numpy`

## 5. How To Run

```bash
python3 actividad-2-01.py
```

Reads `./actividad-2-01/video.mp4` (path relative to the working directory, hardcoded in-script) and writes all five output files to the current directory.

## 6. Output

| Frame 10 — 1.5× scale | Frame 30 — 0.5× scale |
|---|---|
| ![frame_10](frame_10.png) | ![frame_30](frame_30.png) |

| Frame 50 — 35° rotation | Frame 70 — horizontal flip |
|---|---|
| ![frame_50](frame_50.png) | ![frame_70](frame_70.png) |

[`rotation_matrix.pkl`](rotation_matrix.pkl) — the 3×3 homogeneous matrix used in the frame 50 rotation, `numpy.ndarray`, `float64`.
