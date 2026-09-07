# actividad-2-05 — Traffic Light State Detection

## 1. Introduction

&ensp;&ensp;Deliverable for **Actividad 2.5** of M2. Visión Computacional (TE3002B, ITESM). Given a color frame, detects the traffic light in the scene and returns its current state as a string.

## 2. Specification

| # | Step |
|---|---|
| 1 | Detect the traffic light in the frame. |
| 2 | Determine its state. |
| 3 | Return one of: `green`, `yellow`, `red`, `none`. |

Constraint: no output files required; tested against the 3DGS simulator, the evaluator runs the function against a reference implementation.

## 3. Implementation

&ensp;&ensp;`TrafficLightDetection.detect_state()` upscales the frame 2.5× (`INTER_CUBIC`), crops the top 40% (where the traffic light sits), boosts brightness/contrast (`convertScaleAbs`, `alpha=1.5, beta=30`), blurs it, and converts to HSV. It builds separate masks for red, yellow, and green (red split across two hue ranges to cover the HSV wraparound), and decides the state by pixel-count ratio: whichever color has both `ratio > 0.5` of the combined mask and a raw count above `threshold=100` wins; otherwise `"none"`.

## 4. Requirements

- Python 3
- `opencv-python`
- `numpy`
- 3DGS simulator, for testing against a live feed.

## 5. Output

[`video.mp4`](video.mp4) — ~18.7s, evaluator output run against the 3DGS simulator.
