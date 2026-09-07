import cv2
import pickle
import numpy as np

video_path = "./actividad-2-01/video.mp4"
#video_path = "/home/ed/Downloads/Vision/actividad-2-01/video.mp4"
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error al abrir el video")
    exit()

frame_count = 0
#Frames
target_frames = [10, 30, 50, 70]
frames = [None] * len(target_frames)

#Leer video
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    for i, target in enumerate(target_frames):
        if frame_count == target:
            frames[i] = frame.copy()

    if all(f is not None for f in frames):
        break
cap.release()

# 2 Escala la frame 10 a 1.5 veces más grande
frame_10 = frames[0]
(h, w) = frame_10.shape[:2]
scaled_10 = cv2.resize(frame_10, (int(w*1.5), int(h*1.5)))
cv2.imwrite("frame_10.png", scaled_10)

# 3 Escala la frame 30 a la mitad de su tamaño
frame_30 = frames[1]
(h, w) = frame_30.shape[:2]
scaled_30 = cv2.resize(frame_30, (int(w*0.5), int(h*0.5)))
cv2.imwrite("frame_30.png", scaled_30)

# 4 Frame 50 rótala 35 grados sobre su centro
frame_50 = frames[2]
h, w = frame_50.shape[:2]
cx, cy = w // 2, h // 2

angle = 35

theta = np.radians(angle)
cos_t = np.cos(theta)
sin_t = np.sin(theta)

traslation_1 = np.array([
    [1, 0, -cx],
    [0, 1, -cy],
    [0, 0,  1 ]
])

rotation = np.array([
    [cos_t,   sin_t,    0],
    [-sin_t,  cos_t,    0],
    [0,     0,      1]
])

traslation_2 = np.array([
    [1, 0, cx],
    [0, 1, cy],
    [0, 0,  1 ]
])

matrix_3x3 = traslation_2 @ rotation @ traslation_1

matrix_2x3 = matrix_3x3[:2, :]
rotated_50 = cv2.warpAffine(frame_50, matrix_2x3, (w, h))
cv2.imwrite("frame_50.png", rotated_50)

#5 Guardar matriz en pickle
with open("rotation_matrix.pkl", "wb") as f:
    pickle.dump(matrix_3x3, f)

#6 Frame 70 házle un flip horizontal
frame_70 = frames[3]
flipped_70 = cv2.flip(frame_70, 1)
cv2.imwrite("frame_70.png", flipped_70)

print("Proceso completado.")