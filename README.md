# M2. Visión Computacional — TE3002B

## 1. Introduction

&ensp;&ensp;Coursework repository for **M2. Visión Computacional** (TE3002B, Tecnológico de Monterrey), based on Corke, P. (2023) *Robotics, Vision and Control: Fundamental Algorithms in Python*. Each `actividad-2-XX/` folder is a self-contained deliverable with its own README (spec, implementation notes, how to run, output evidence).

## 2. Activities

| # | Folder | Summary |
|---|---|---|
| 2.1 | [actividad-2-01](actividad-2-01/) | Geometric transformations on video frames with OpenCV: scaling, rotation about center via an explicit homogeneous matrix, horizontal flip. |
| 2.2 | [actividad-2-02](actividad-2-02/) | Connects to a CoppeliaSim scene over its ZeroMQ Remote API, starts the simulation, and captures a frame from a simulated vision sensor. |
| 2.3 | [actividad-2-03](actividad-2-03/) | Detects an orange ball in a CoppeliaSim scene (HSV threshold + contours) and returns its centroid. |
| 2.4 | [actividad-2-04](actividad-2-04/) | Detects the center line of a track from the bottom quarter of a camera frame, for line-following in the 3DGS simulator. |
| 2.5 | [actividad-2-05](actividad-2-05/) | Detects a traffic light's state (`green`/`yellow`/`red`/`none`) from a camera frame. |
| 2.6 | [actividad-2-06](actividad-2-06/) | Traffic sign detection combining a fine-tuned YOLOv8 model with SSIM template matching, reporting which sign is directly ahead. |
| 2.7 | [actividad-2-07](actividad-2-07/) | Camera calibration from a chessboard image set (K, distortion coefficients) and undistortion of a sample frame. |
| 2.8 | [actividad-2-08](actividad-2-08/) | Stitches overlapping campus photos into a panorama with a manual SIFT + RANSAC homography pipeline. |
| 2.9 | [actividad-2-09](actividad-2-09/) | Backprojects an aligned RGB-D frame (Intel RealSense D435i) into a colored 3D point cloud, computing XYZ manually. |
| 2.10 | [actividad-2-10](actividad-2-10/) | Builds two point clouds from two stereo image pairs of the same scene and aligns them with ICP into one 3D reconstruction. |

## 3. Final Exam

| Folder | Summary |
|---|---|
| [examenfinal](examenfinal/) | Detects, IDs, and tracks fish in a top-down underwater video (MOG2 background subtraction + centroid tracking); extra credit: 3D reconstruction of a peacock nest from video. |

## 4. Requirements

&ensp;&ensp;Each activity lists its exact dependencies in its own README. Across the repo:

- Python 3, `opencv-python`, `numpy` — used throughout.
- `open3d` — actividades 2.9, 2.10.
- `ultralytics`, `scikit-image` — actividad 2.6.
- `matplotlib` — actividad 2.9.
- CoppeliaSim (Edu, ZeroMQ Remote API) — actividades 2.2, 2.3.
- ROS2 — Puzzlebot camera capture (actividad 2.7) and the 3DGS simulator feed (actividades 2.4, 2.5).

## 5. License

&ensp;&ensp;See [LICENSE](LICENSE).
