# actividad-2-03 — Orange Ball Detection in CoppeliaSim

## 1. Introduction

&ensp;&ensp;Deliverable for **Actividad 2.3** of M2. Visión Computacional (TE3002B, ITESM). Grabs a frame from a CoppeliaSim vision sensor and detects an orange ball in the scene, returning the pixel coordinates of its centroid.

## 2. Specification

| # | Step |
|---|---|
| 1 | Acquire the image from the simulated camera. |
| 2 | Detect the orange ball in the scene and return the pixel coordinates of its center. |

Constraints: don't start/stop the simulation from Python — the evaluator does it. Remove any CoppeliaSim path additions before submission — the evaluator injects its own. No output files are required; the evaluator runs the function against a reference implementation and compares results.

## 3. Implementation

&ensp;&ensp;`OrangeDetector.detect_orange_object()` converts the frame to HSV, thresholds it against an orange range (`[0,80,50]`–`[20,255,255]`), cleans the mask with morphological open+close, and picks the largest contour above 50px² by area; the centroid is computed from its image moments (`m10/m00`, `m01/m00`).

&ensp;&ensp;There are two variants of this same pipeline in the folder, serving different purposes:

- **`actividad_2_03.py`** — evaluator-facing version: no CoppeliaSim path injection, doesn't start/stop the simulation, matching the spec's constraints exactly.
- **`actividad_2_03-template.py`** — standalone version for local testing: adds the CoppeliaSim path via `sys.path.append` and starts the simulation (`sim.startSimulation()` + 1s wait) in the constructor, since there's no evaluator harness driving it when run directly.

## 4. Requirements

- CoppeliaSim (Edu), with the ZeroMQ Remote API enabled.
- `actividad-2-03.ttt` — the simulation scene, with the orange ball in view of `/Vision_sensor`.
- `coppeliasim-zmqremoteapi-client`
- `opencv-python`
- `numpy`

## 5. How To Run

1. Open CoppeliaSim and load the scene `actividad-2-03.ttt`.
2. Run the script:

```bash
python3 actividad_2_03-template.py
```

## 6. Output

&ensp;&ensp;No output files are required — the function returns `(cx, cy)` directly. Sample run:

```
Mejor centroide detectado en: (317, 236)
Mejor centroide detectado en: (317, 236)
Mejor centroide detectado en: (317, 236)
Mejor centroide detectado en: (317, 236)
```
