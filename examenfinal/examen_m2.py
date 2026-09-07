'''

Actúa como un experto en Visión por Computadora. Necesito procesar un video para contar y rastrear objetos


Aquí tienes la descripción exacta de la escena:

- Es una cámara con vista superior (top-down) grabando un cuerpo de agua poco profundo.

- El fondo es arena estática de color claro.

- Hay decenas de peces diminutos que se ven como pequeñas manchas oscuras o siluetas alargadas (de unos pocos píxeles) nadando en diferentes direcciones.

- Hay algo de ruido visual constante debido a los ligeros reflejos y ondulaciones del agua en la superficie.



Mi objetivo principal es:

1. Detectar todos los peces en la escena en cada frame.

2. Asignar un ID único a cada pez.

3. Hacer tracking (seguimiento) de cada ID a lo largo del tiempo.

Dado que los objetos son extremadamente pequeños quiero implementar un pipeline clásico de procesamiento de imágenes usando Python, OpenCV y NumPy. 

¿Podrías explicarme la mejor metodología usando técnicas de sustracción de fondo (como MOG2), aplicar filtros morfológicos para el ruido del agua, e integrarlo con un algoritmo de seguimiento por distancias euclidianas (Centroid Tracking)? Por favor, incluye un script base completamente funcional en un solo archivo. 

'''

import cv2
import numpy as np
from collections import OrderedDict

# ── Centroid Tracker ──────────────────────────────────────────────────────────
class CentroidTracker:
    def __init__(self, max_disappeared=20, max_distance=35):
        self.next_id = 0
        self.objects   = OrderedDict()
        self.disappeared = OrderedDict()
        self.max_disappeared = max_disappeared
        self.max_distance    = max_distance
        self.total_registered = 0

    def register(self, centroid):
        self.objects[self.next_id] = centroid
        self.disappeared[self.next_id] = 0
        self.next_id += 1
        self.total_registered += 1

    def deregister(self, oid):
        del self.objects[oid]
        del self.disappeared[oid]

    def update(self, rects):
        if not rects:
            for oid in list(self.disappeared):
                self.disappeared[oid] += 1
                if self.disappeared[oid] > self.max_disappeared:
                    self.deregister(oid)
            return self.objects

        input_centroids = np.array(
            [(x + w // 2, y + h // 2) for (x, y, w, h) in rects], dtype="int")

        if not self.objects:
            for c in input_centroids:
                self.register(c)
        else:
            ids      = list(self.objects.keys())
            existing = np.array(list(self.objects.values()))
            D = np.linalg.norm(existing[:, None] - input_centroids[None, :], axis=2)

            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            used_rows, used_cols = set(), set()

            for r, c in zip(rows, cols):
                if r in used_rows or c in used_cols:
                    continue
                if D[r, c] > self.max_distance:
                    continue
                oid = ids[r]
                self.objects[oid] = input_centroids[c]
                self.disappeared[oid] = 0
                used_rows.add(r)
                used_cols.add(c)

            for r in set(range(D.shape[0])) - used_rows:
                self.disappeared[ids[r]] += 1
                if self.disappeared[ids[r]] > self.max_disappeared:
                    self.deregister(ids[r])

            for c in set(range(D.shape[1])) - used_cols:
                self.register(input_centroids[c])

        return self.objects


# ── Config ────────────────────────────────────────────────────────────────────
INPUT   = 'pecesoriginal-ns.mp4'
OUTPUT  = 'peces_tracked.mp4'
SCALE   = 0.5          # process at half res, draw on full res
WARMUP  = 150          # frames for MOG2 to learn background
EXCLUDE_X_SMALL = 75   # left edge mask (in scaled coords)

# ── Open video ────────────────────────────────────────────────────────────────
cap   = cv2.VideoCapture(INPUT)
fps   = cap.get(cv2.CAP_PROP_FPS)
W     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
H     = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
TOTAL = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

SW, SH = int(W * SCALE), int(H * SCALE)   # small dims

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out    = cv2.VideoWriter(OUTPUT, fourcc, fps, (W, H))

fgbg    = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=False)
tracker = CentroidTracker(max_disappeared=20, max_distance=35)

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

np.random.seed(42)
COLORS = [tuple(int(c) for c in np.random.randint(60, 255, 3)) for _ in range(5000)]

# ── Warmup MOG2 ───────────────────────────────────────────────────────────────
print(f"Warming up MOG2 ({WARMUP} frames)...")
for i in range(WARMUP):
    ret, f = cap.read()
    if not ret:
        break
    small = cv2.resize(f, (SW, SH))
    fgbg.apply(small)

print("Processing...")
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)   # rewind to start for output video

frame_idx      = 0
max_concurrent = 0
active_history = []

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_idx += 1

    small = cv2.resize(frame, (SW, SH))
    mask  = fgbg.apply(small)

    # Morphology
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,   kernel)
    mask = cv2.dilate(mask, kernel, iterations=2)

    # Find contours
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    rects = []
    for c in cnts:
        a = cv2.contourArea(c)
        if a < 8 or a > 150:
            continue
        x, y, w, h = cv2.boundingRect(c)
        if x < EXCLUDE_X_SMALL:          # skip noisy left edge
            continue
        ar = max(w, h) / max(min(w, h), 1)
        if not (1.2 < ar < 6.0):         # fish are elongated
            continue
        rects.append((x, y, w, h))

    objects = tracker.update(rects)

    active = len(objects)
    if active > max_concurrent:
        max_concurrent = active
    active_history.append(active)

    # ── Draw on FULL-res frame ────────────────────────────────────────────────
    INV = 1.0 / SCALE
    for oid, (cx_s, cy_s) in objects.items():
        cx = int(cx_s * INV)
        cy = int(cy_s * INV)
        color = COLORS[oid % len(COLORS)]
        cv2.circle(frame, (cx, cy), 6, color, -1)
        cv2.putText(frame, str(oid), (cx + 8, cy - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.30, color, 1, cv2.LINE_AA)

    # HUD
    cv2.rectangle(frame, (8, 6), (450, 80), (15, 15, 15), -1)
    cv2.rectangle(frame, (8, 6), (450, 80), (90, 90, 90), 1)
    cv2.putText(frame, f"Peces en pantalla:  {active:4d}", (18, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 255, 120), 2, cv2.LINE_AA)
    out.write(frame)

    if frame_idx % 100 == 0:
        print(f"  frame {frame_idx:4d}/{TOTAL}  active={active:4d}  total_ids={tracker.total_registered}")

cap.release()
out.release()

print(f"\n{'='*40}")
print(f"Frames procesados      : {frame_idx}")
print(f"Máx peces simultáneos  : {max_concurrent}")
print(f"Promedio activos/frame : {np.mean(active_history):.0f}")
print(f"Video guardado         : {OUTPUT}")
